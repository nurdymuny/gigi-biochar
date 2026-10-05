"""Preserve a supplied Dryad archive and normalize its sorption-isotherm pairs.

Core extraction uses Python's standard library; the source workbook is not edited.
Usage: python scripts/import_dryad.py [--archive downloaded.zip] [--gigi-url URL]
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from analyze import Gigi,equivalent

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/source/dryad'
SHEET='Figure 5 and Sup. Fig. S5'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def write_json(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n',encoding='utf8',newline='\n')

def archive(path):
    RAW.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path) as z:
        for name in ['Compiled_Data.xlsx','README.md']:
            (RAW/name).write_bytes(z.read(name))
    write_json(RAW/'provenance.json',dict(doi='10.5061/dryad.pc866t1w7',version='2023-10-10',obtained='User-supplied copy of the public Dryad dataset archive',archive_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),files={name:hashlib.sha256((RAW/name).read_bytes()).hexdigest() for name in ['Compiled_Data.xlsx','README.md']},reuse='CC0; Dryad dataset terms https://datadryad.org/terms',source_unchanged=True))

def workbook_cells(path=RAW/'Compiled_Data.xlsx'):
    with zipfile.ZipFile(path) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            shared=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        relationships={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        workbook=ET.fromstring(z.read('xl/workbook.xml'))
        sheets={}
        for s in workbook.findall('s:sheets/s:sheet',NS):
            key=s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target=relationships[key]
            target=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            cells={}
            for c in ET.fromstring(z.read(target)).findall('.//s:sheetData/s:row/s:c',NS):
                if c.find('s:f',NS) is not None:
                    raise ValueError('Formula cell requires an explicit cached-value review: '+s.attrib['name']+'!'+c.attrib['r'])
                val=c.find('s:v',NS);typ=c.attrib.get('t')
                if typ=='inlineStr':value=''.join(c.find('s:is',NS).itertext())
                elif val is None:continue
                elif typ=='s':value=shared[int(val.text)]
                elif typ in ('str','e'):value=val.text
                else:value=float(val.text)
                cells[c.attrib['r']]=value
            sheets[s.attrib['name']]=cells
        return sheets

def extract():
    sheets=workbook_cells();cells=sheets[SHEET]
    summaries=json.loads((ROOT/'data/processed/capture_records.json').read_text(encoding='utf8'))
    identities={(r['feedstock'],r['pyrolysis_c'],r['mg_activation_molar']):r['id'] for r in summaries}
    rows=[]
    headers=sorted(int(k[1:]) for k,v in cells.items() if k.startswith('C') and v=='Biochar')
    if len(headers)!=9:raise ValueError('Expected nine formulation blocks')
    for h in headers:
        for xcol,ycol in [('E','F'),('H','I'),('K','L'),('N','O')]:
            feed=cells[xcol+str(h)]
            temp=int(re.match(r'\d+',cells[xcol+str(h+1)]).group())
            mg=float(cells[xcol+str(h+2)].split()[0])
            identity=identities[(feed,temp,mg)]
            if cells.get(xcol+str(h+3))!='Solution P Concentration (mg/L)':raise ValueError('Unexpected concentration header')
            if cells.get(ycol+str(h+3))!='Sorbed P Concentration (mg/g)':raise ValueError('Unexpected uptake header')
            for point,r in enumerate(range(h+4,h+19),1):
                ce=cells.get(xcol+str(r));q=cells.get(ycol+str(r))
                if not isinstance(ce,(int,float)) or not isinstance(q,(int,float)):raise ValueError('Missing paired observation')
                rows.append(dict(id=len(rows)+1,formulation_id=identity,feedstock=feed,pyrolysis_c=temp,mg_activation_molar=mg,point_index=point,solution_p_mg_l=ce,sorbed_p_mg_g=q,source_sheet=SHEET,source_cells=f'{xcol}{r}:{ycol}{r}'))
    return rows,sheets

def summarize(rows,sheets):
    groups=[]
    for mg in [0,.25,.5,1.]:
        subset=[r for r in rows if r['mg_activation_molar']==mg]
        groups.append(dict(mg_molar=mg,observations=len(subset),negative_sorption=sum(r['sorbed_p_mg_g']<0 for r in subset),q_min=min(r['sorbed_p_mg_g'] for r in subset),q_max=max(r['sorbed_p_mg_g'] for r in subset)))
    return dict(observations=len(rows),formulations=len({r['formulation_id'] for r in rows}),points_per_formulation=sorted(set(collections.Counter(r['formulation_id'] for r in rows).values())),negative_sorption=sum(r['sorbed_p_mg_g']<0 for r in rows),activation_groups=groups,solution_p_range_mg_l=[min(r['solution_p_mg_l'] for r in rows),max(r['solution_p_mg_l'] for r in rows)],workbook_sheets=list(sheets),label_anomalies={name:sorted({v for v in cells.values() if isinstance(v,str) and v=='PL9'}) for name,cells in sheets.items() if any(v=='PL9' for v in cells.values())},notes=['Observation counts pool concentration conditions and within-condition measurements; they are not independent batches or field events.','Point index records sheet order only; no replicate identity or initial concentration is inferred from position.','Negative sorbed-P values are preserved as net release, not set to zero.','Only the isotherm sheet is normalized for this analysis. Other sheets are archived and inventoried; PL9 labels there are not silently mapped to PL7.','Workbook General Information names Figure 4 and Sup. Fig. S5, but the actual isotherm tab is Figure 5 and Sup. Fig. S5.','This descriptive extraction does not refit Langmuir parameters or reproduce published SE and R-squared.'])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path)
    parser.add_argument('--gigi-url')
    args=parser.parse_args()
    if args.archive:archive(args.archive)
    manifest=json.loads((RAW/'provenance.json').read_text())
    for name,digest in manifest['files'].items():
        if hashlib.sha256((RAW/name).read_bytes()).hexdigest()!=digest:raise ValueError('Dryad source checksum mismatch: '+name)
    rows,sheets=extract();result=summarize(rows,sheets)
    write_json(ROOT/'data/processed/isotherm_records.json',rows)
    with (ROOT/'data/processed/isotherm_records.csv').open('w',encoding='utf8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    write_json(ROOT/'results/isotherm_summary.json',result)
    if args.gigi_url:
        client=Gigi(args.gigi_url);name='biochar_isotherms_v1'
        client.load(name,rows)
        negative=client.call(f'/v1/bundles/{name}/query',{'conditions':[{'field':'sorbed_p_mg_g','op':'lt','value':0}],'limit':1000})
        if negative.get('meta',{}).get('truncated'):raise ValueError('Truncated negative-sorption query')
        equivalent(negative['data'],[r for r in rows if r['sorbed_p_mg_g']<0])
        import datetime
        write_json(ROOT/'results/isotherm_live_verification.json',dict(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bundle=name,source_sha256=hashlib.sha256((ROOT/'data/processed/isotherm_records.json').read_bytes()).hexdigest(),checks=['Complete row roundtrip','All negative-sorption observations match independent reference'],receipts=client.receipts))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
