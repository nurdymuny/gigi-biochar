"""Deterministic secondary analysis of published sorption-fit summaries.

Run: python scripts/analyze.py [--gigi-url http://127.0.0.1:3147]
The default offline analysis requires only Python 3.10+ standard library.
"""
import argparse
import collections
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
CAP='pmax_mg_p_per_g_biochar'
SE='pmax_se_mg_p_per_g_biochar'

def load_records():
    return json.loads((ROOT/'data/processed/capture_records.json').read_text(encoding='utf8'))

def validate(records):
    if len(records)!=36: raise ValueError('Expected all 36 formulation summaries')
    keys={(r['feedstock'],r['mg_activation_molar'],r['pyrolysis_c']) for r in records}
    expected={(f,m,t) for f in ['PL1','PL3','PL7'] for m in [0,.25,.5,1] for t in [500,700,900]}
    if keys!=expected: raise ValueError('Incomplete or duplicated factorial design')
    if len({r['id'] for r in records})!=36: raise ValueError('Record IDs must be unique')
    for r in records:
        if r[CAP] is None:
            if r[SE] is not None or r['r_squared'] is not None or 'NR' not in r['source_cell']:
                raise ValueError('NR must preserve missing capacity, SE and R2')
        elif not (r[CAP]>0 and r[SE]>=0 and 0<=r['r_squared']<=1):
            raise ValueError('Invalid numeric summary')

def screen(records,threshold=.8):
    return sorted((r for r in records if r['r_squared'] is not None and r['r_squared']>threshold),key=lambda r:(-r[CAP],r['id']))

def summary(records):
    validate(records)
    groups=[]
    passing=screen(records)
    for mg in [0.,.25,.5,1.]:
        rows=[r for r in records if r['mg_activation_molar']==mg]
        good=screen(rows)
        missing=sum(r[CAP] is None for r in rows)
        groups.append(dict(mg_molar=mg,total=len(rows),passing=len(good),nr=missing,poor_fit=len(rows)-missing-len(good),passing_mean=None if not good else sum(r[CAP] for r in good)/len(good),passing_range=None if not good else [min(r[CAP] for r in good),max(r[CAP] for r in good)]))
    sensitivities=[]
    for threshold in [.7,.8,.85,.9,.95]:
        good=screen(records,threshold)
        sensitivities.append(dict(threshold=threshold,operator='>',passing=len(good),top_id=good[0]['id'],top_capacity=good[0][CAP],one_molar_passing=sum(r['mg_activation_molar']==1 for r in good)))
    return dict(formulations=len(records),nr=sum(r[CAP] is None for r in records),numeric_fits=sum(r[CAP] is not None for r in records),passing=len(passing),poor_fit=sum(r['r_squared'] is not None and r['r_squared']<=.8 for r in records),ranked_ids=[r['id'] for r in passing],activation_groups=groups,threshold_sensitivity=sensitivities,primary_threshold=.8,threshold_operator='>',uncertainty='Published standard errors of fitted Pmax; not confidence intervals or between-batch variation.',unit='mg P per g biochar',analysis_kind='Descriptive secondary analysis of published fitted summaries; no isotherm refitting or new significance tests.')

def equivalent(actual,expected):
    if len(actual)!=len(expected): raise ValueError('Roundtrip record count differs')
    a={r['id']:r for r in actual}; b={r['id']:r for r in expected}
    if len(a)!=len(actual) or len(b)!=len(expected): raise ValueError('Duplicate roundtrip IDs')
    if set(a)!=set(b): raise ValueError('Roundtrip IDs differ')
    for i in b:
        if set(a[i])!=set(b[i]): raise ValueError(f'Fields differ for row {i}')
        for k,v in b[i].items():
            z=a[i][k]
            if isinstance(v,float):
                if not isinstance(z,(int,float)) or not math.isclose(z,v,rel_tol=1e-12,abs_tol=1e-12): raise ValueError(f'Numeric mismatch: {i}/{k}')
            elif z!=v: raise ValueError(f'Value mismatch: {i}/{k}')

class Gigi:
    def __init__(self,base):
        self.base=base.rstrip('/'); self.receipts=[]
    def call(self,path,body=None):
        headers={'Content-Type':'application/json'}
        if os.environ.get('GIGI_API_KEY'): headers['X-API-Key']=os.environ['GIGI_API_KEY']
        request=urllib.request.Request(self.base+path,data=None if body is None else json.dumps(body,allow_nan=False).encode(),headers=headers)
        try:
            with urllib.request.urlopen(request,timeout=60) as response:
                result=json.load(response); status=response.status
        except urllib.error.HTTPError as error:
            detail=error.read().decode()
            raise RuntimeError(f'{path}: HTTP {error.code}: {detail}. Read the refusal before retrying.') from error
        if path=='/v1/gql' and result=={'status':'ok'}: raise RuntimeError('GQL returned no execution evidence')
        # Headers, credentials, base URL and unrelated server logs are not persisted.
        self.receipts.append(dict(path=path,request=body,status=status,response=result))
        return result
    def load(self,name,rows,field_types=None):
        items=self.call('/v1/bundles')
        if isinstance(items,dict): items=items['data']
        # Do not retain an inventory of unrelated bundles in the public receipt.
        self.receipts.pop()
        if any(r['name']==name for r in items):
            response=self.call(f'/v1/bundles/{name}/query',{'limit':1000})
            if response.get('meta',{}).get('truncated'): raise ValueError('Truncated bundle read')
            equivalent(response['data'],rows)
            return
        # Explicit types are needed for columns whose observed values are all null.
        fields=dict(field_types or {})
        for row in rows:
            for k,v in row.items():
                if v is not None: fields[k]='integer' if isinstance(v,int) else 'float' if isinstance(v,float) else 'text'
        self.call('/v1/bundles',{'name':name,'schema':{'fields':fields,'keys':['id']}})
        result=self.call(f'/v1/bundles/{name}/insert',{'records':rows})
        if result.get('count',result.get('inserted'))!=len(rows): raise ValueError('Insert count mismatch')
        equivalent(self.call(f'/v1/bundles/{name}/query',{'limit':1000})['data'],rows)

def live_check(records,base):
    client=Gigi(base)
    name='biochar_capture_paper_v1'
    fixture='biochar_capture_paper_gate_v1'
    planted=[dict(id=1,pmax=9999.,r_squared=.01),dict(id=2,pmax=5.,r_squared=.95)]
    client.load(fixture,planted)
    order=[{'field':'pmax','desc':True}]
    good=client.call(f'/v1/bundles/{fixture}/query',{'conditions':[{'field':'r_squared','op':'gt','value':.8}],'sort':order,'limit':1})['data']
    if good[0]['id']!=2: raise ValueError('Planted screening check failed')
    broken=client.call(f'/v1/bundles/{fixture}/query',{'sort':order,'limit':1})['data']
    if broken[0]['id']!=1: raise ValueError('Mechanism-removed negative control failed')
    client.load(name,records)
    for threshold in [.7,.8,.85,.9,.95]:
        conditions=[{'field':'r_squared','op':'gt','value':threshold}]
        result=client.call(f'/v1/bundles/{name}/query',{'conditions':conditions,'sort':[{'field':CAP,'desc':True}],'limit':1000})
        expected=screen(records,threshold)
        if result.get('meta',{}).get('truncated'): raise ValueError('Truncated ranking')
        equivalent(result['data'],expected)
        if [r['id'] for r in result['data']]!=[r['id'] for r in expected]: raise ValueError('Ranking mismatch')
    for group in summary(records)['activation_groups']:
        if group['passing']==0: continue
        response=client.call(f'/v1/bundles/{name}/aggregate',{'group_by':'mg_activation_molar','field':CAP,'conditions':[{'field':'r_squared','op':'gt','value':.8},{'field':'mg_activation_molar','op':'eq','value':group['mg_molar']}]})
        value=next(iter(response['groups'].values()))
        if value['count']!=group['passing'] or not math.isclose(value['avg'],group['passing_mean'],abs_tol=1e-12): raise ValueError('Aggregate mismatch')
    out=dict(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bundle=name,source_sha256=hashlib.sha256((ROOT/'data/processed/capture_records.json').read_bytes()).hexdigest(),checks=['Planted ranking','Mechanism-removed negative control','Complete row roundtrip','Five threshold rankings','Grouped counts and means'],receipts=client.receipts)
    (ROOT/'results/live_verification.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8',newline='\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gigi-url',help='Optional live verification; creates only project-specific bundles and never overwrites differing data.')
    args=parser.parse_args()
    rows=load_records(); result=summary(rows)
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    if args.gigi_url: live_check(rows,args.gigi_url)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
