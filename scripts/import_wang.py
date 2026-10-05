"""Archive and extract Wang's kinetic means/SD; keep distinct from Padilla.

The isotherm sheet is archived but not normalized because its Qe unit needs review.
"""
import argparse
import csv
import datetime
import hashlib
import json
from pathlib import Path
import zipfile
from analyze import Gigi, equivalent
from import_dryad import workbook_cells, write_json

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/source/wang_2021'
FILE = 'PO4-P_adsorption_kinetis_and_isotherms_raw_data.xlsx'
SHEET = 'PO4-P adsorption kinetics'
MATERIALS = [('Al-BC','B','C'), ('Ca-BC','D','E'), ('Fe-BC','F','G'),
             ('La-BC','H','I'), ('Mg-BC','J','K'), ('BC','L','M')]
TIMES = [.5,1,1.5,2,3,4,6,8,12,24,48,72]

def archive(path):
    RAW.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as source:
        body = source.read(FILE)
        inventory = {i.filename: i.file_size for i in source.infolist()}
    (RAW / FILE).write_bytes(body)
    write_json(RAW/'provenance.json', dict(
        doi='10.5061/dryad.3xsj3txf4', version='2021-04-22',
        obtained='User-supplied public Dryad ZIP; kinetic/isotherm workbook preserved unchanged',
        archive_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        archive_inventory_bytes=inventory,
        files={FILE:hashlib.sha256(body).hexdigest()}, license='CC0',
        dataset_url='https://datadryad.org/dataset/doi:10.5061/dryad.3xsj3txf4',
        source_unchanged=True, other_archive_members='Inventoried, not extracted or analyzed'))

def extract():
    manifest = json.loads((RAW/'provenance.json').read_text())
    if hashlib.sha256((RAW/FILE).read_bytes()).hexdigest() != manifest['files'][FILE]:
        raise ValueError('Wang source checksum mismatch')
    cells = workbook_cells(RAW/FILE)[SHEET]
    if cells['A1'] != 't (h)': raise ValueError('Unexpected time unit')
    rows = []
    for material, mean_col, sd_col in MATERIALS:
        if cells[mean_col+'2'] != 'Mean' or cells[sd_col+'2'] != 'Standard deviation':
            raise ValueError('Mean/SD headers changed')
        if material not in cells[mean_col+'1'] or '(mg/g)' not in cells[mean_col+'1']:
            raise ValueError('Material or uptake unit changed')
        for index, time in enumerate(TIMES, 3):
            t, q, sd = [cells[col+str(index)] for col in ['A',mean_col,sd_col]]
            if t != time or not isinstance(q,float) or not isinstance(sd,float) or sd < 0:
                raise ValueError('Unexpected kinetic value')
            rows.append(dict(id=len(rows)+1, study_id='wang_2021', material=material,
                time_h=t, q_mean_mg_g=q, q_sd_mg_g=sd, replicate_n=None,
                uncertainty_type='source standard deviation', observation_type='summary mean',
                source_sheet=SHEET, source_time_cell='A'+str(index),
                source_mean_cell=mean_col+str(index), source_sd_cell=sd_col+str(index)))
    return rows

def summarize(rows):
    return dict(summary_records=len(rows), materials=6, times_h=TIMES,
        negative_means=sum(r['q_mean_mg_g']<0 for r in rows),
        at_30_minutes=[{k:r[k] for k in ['material','q_mean_mg_g','q_sd_mg_g']} for r in rows if r['time_h']==.5],
        notes=['Means and standard deviations, not individual replicate measurements.',
               'Replicate count is not specified in the workbook; no count or SE is inferred.',
               'The kinetics header reports mg/g under PO4-P; original units are preserved without conversion.',
               'Thirty minutes is the earliest measured time. No performance before that time is inferred.',
               'Negative means are preserved as signed observations.',
               'Isotherm Qe headers report mg/L, unlike kinetic Q mg/g. Isotherms remain archived pending unit review.',
               'No new model fits, significance tests, equilibrium claims, or cross-study material ranking.'])

def live(rows, url):
    client=Gigi(url); name='biochar_wang_kinetic_summaries_v1'; gate='biochar_wang_time_gate_v1'
    planted=[dict(id=1,time_h=72.,q=99.),dict(id=2,time_h=.5,q=1.)]
    client.load(gate,planted)
    query=dict(conditions=[dict(field='time_h',op='eq',value=.5)],sort=[dict(field='q',desc=True)],limit=1)
    if client.call(f'/v1/bundles/{gate}/query',query)['data'][0]['id']!=2:
        raise ValueError('Planted time selection failed')
    del query['conditions']
    if client.call(f'/v1/bundles/{gate}/query',query)['data'][0]['id']!=1:
        raise ValueError('Mechanism-removed time control failed')
    client.load(name,rows,field_types={'replicate_n':'integer'})
    for time in TIMES:
        # Match the float schema: this engine distinguishes integer/float equality.
        result=client.call(f'/v1/bundles/{name}/query',dict(conditions=[dict(field='time_h',op='eq',value=float(time))],limit=1000))
        if result.get('meta',{}).get('truncated'): raise ValueError('Truncated time query')
        equivalent(result['data'],[r for r in rows if r['time_h']==time])
    write_json(ROOT/'results/wang_live_verification.json',dict(
        checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bundle=name,
        source_sha256=hashlib.sha256((ROOT/'data/processed/wang_kinetics.json').read_bytes()).hexdigest(),
        checks=['Planted time filter','Mechanism-removed negative control','All 72 summaries roundtrip','All 12 time selections match Python'],receipts=client.receipts))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path);parser.add_argument('--gigi-url');args=parser.parse_args()
    if args.archive:archive(args.archive)
    rows=extract()
    write_json(ROOT/'data/processed/wang_kinetics.json',rows)
    with (ROOT/'data/processed/wang_kinetics.csv').open('w',encoding='utf8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    result=summarize(rows);write_json(ROOT/'results/wang_summary.json',result)
    if args.gigi_url:live(rows,args.gigi_url)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
