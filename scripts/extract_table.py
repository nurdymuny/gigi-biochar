"""Rebuild normalized data from the archived, attributed source-table excerpt."""
import csv
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
URL='https://link.springer.com/article/10.1007/s42773-023-00263-5/tables/1'

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_body=False; self.in_cell=False; self.rows=[]
    def handle_starttag(self,tag,attrs):
        if tag=='tbody': self.in_body=True
        elif tag=='tr' and self.in_body: self.row=[]
        elif tag=='td' and self.in_body: self.in_cell=True; self.cell=''
    def handle_data(self,value):
        if self.in_cell:self.cell+=value
    def handle_endtag(self,tag):
        if tag=='td' and self.in_cell:
            self.row.append(re.sub(r'\s+',' ',self.cell).strip());self.in_cell=False
        elif tag=='tr' and self.in_body:self.rows.append(self.row)
        elif tag=='tbody':self.in_body=False

def extract():
    parser=TableParser();parser.feed((ROOT/'data/source/table1.html').read_text(encoding='utf8'))
    if len(parser.rows)!=12:raise ValueError('Source table must have 12 body rows')
    records=[];feedstock=None
    for line,raw in enumerate(parser.rows,1):
        cells=list(raw)
        if len(cells)==8:feedstock=cells.pop(0)
        if len(cells)!=7 or feedstock not in ['PL1','PL3','PL7']:raise ValueError('Unexpected table layout')
        mg=float(cells[0])
        for index,temp in enumerate([500,700,900]):
            cell=cells[1+index*2]
            if 'NR' in cell:
                cap=se=r2=None;state='NR: net P release (source table label)'
            else:
                cap,se=[float(x.strip()) for x in cell.split('±')];r2=float(cells[2+index*2])
                state='passes R2 > 0.80 screen' if r2>.8 else 'poor Langmuir fit: R2 <= 0.80'
            records.append(dict(id=len(records)+1,feedstock=feedstock,feedstock_age_years={'PL1':'1','PL3':'3-5','PL7':'7-9'}[feedstock],mg_activation_molar=mg,pyrolysis_c=temp,pmax_mg_p_per_g_biochar=cap,pmax_se_mg_p_per_g_biochar=se,r_squared=r2,fit_screen=state,source_table_row=line,source_cell=cell,source_url=URL))
    return records

def main():
    rows=extract()
    (ROOT/'data/processed/capture_records.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8',newline='\n')
    with (ROOT/'data/processed/capture_records.csv').open('w',newline='',encoding='utf8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(f'Extracted {len(rows)} formulations. CSV blank numeric cells mean unavailable, not zero.')

if __name__=='__main__':main()
