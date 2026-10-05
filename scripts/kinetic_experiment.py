"""Exploratory contact-time comparison of archived Wang kinetic means/SD.

No interpolation, new kinetic fits, inferred replicate counts or significance tests.
Run offline, or add --gigi-url to verify selections/rankings against a live engine.
"""
import argparse
import csv
import datetime
import hashlib
import itertools
import json
from pathlib import Path
from analyze import Gigi, equivalent
from import_dryad import write_json
from import_wang import extract, MATERIALS, TIMES

ROOT=Path(__file__).resolve().parents[1]
TARGETS=[5.,8.,9.]

def rank_at(rows,time):
    return sorted((r for r in rows if r['time_h']==time),
                  key=lambda r:(-r['q_mean_mg_g'],r['material']))

def sustained_window(series,target,sd_multiplier=0.):
    """First observed time whose value and ALL later sampled values meet target.

    A preceding sample is a grid bracket, not a continuous-time crossing bound.
    For mean-k*SD, this is a deterministic sensitivity scenario, never a CI.
    """
    ordered=sorted(series,key=lambda r:r['time_h'])
    values=[r['q_mean_mg_g']-sd_multiplier*r['q_sd_mg_g'] for r in ordered]
    for i,row in enumerate(ordered):
        if all(v>=target for v in values[i:]):
            return dict(status='at_first_sample' if i==0 else 'observed',
                        previous_sample_h=None if i==0 else ordered[i-1]['time_h'],
                        first_sustained_sample_h=row['time_h'])
    return dict(status='not_sustained_by_last_sample',previous_sample_h=None,
                first_sustained_sample_h=None)

def band_separated(a,b,k):
    """Strict separation of illustrative mean +/- k*SD intervals, not inference."""
    return (a['q_mean_mg_g']-k*a['q_sd_mg_g'] > b['q_mean_mg_g']+k*b['q_sd_mg_g']
            or b['q_mean_mg_g']-k*b['q_sd_mg_g'] > a['q_mean_mg_g']+k*a['q_sd_mg_g'])

def experiment(rows):
    ranking=[]
    for t in TIMES:
        ranked=rank_at(rows,t)
        ranking.append(dict(time_h=t,ordered_materials=[r['material'] for r in ranked],
            ordered_ids=[r['id'] for r in ranked],
            distinct_means=len({r['q_mean_mg_g'] for r in ranked}),
            band_separation=[dict(sd_multiplier=k,separated_pairs=sum(band_separated(a,b,k)
                for a,b in itertools.combinations(ranked,2)),total_pairs=15) for k in [1.,2.]]))
    targets=[]
    for material,_,_ in MATERIALS:
        series=[r for r in rows if r['material']==material]
        for target in TARGETS:
            for k in [0.,1.,2.]:
                targets.append(dict(material=material,target_mg_g=target,sd_multiplier=k,
                                    **sustained_window(series,target,k)))
    selected=[]
    for material,_,_ in MATERIALS:
        observations=[next(r for r in rows if r['material']==material and r['time_h']==t)
                      for t in [.5,2.,6.,24.,72.]]
        selected.append(dict(material=material,observations=observations))
    return dict(kind='Exploratory descriptive computational experiment; no new laboratory experiment',
        input_sha256=hashlib.sha256((ROOT/'data/processed/wang_kinetics.json').read_bytes()).hexdigest(),
        source_records=len(rows),rankings=ranking,target_windows=targets,selected_observations=selected,
        methods=['Rank reported means independently at each measured time; ties are ordered by material label only.',
                 'Targets 5, 8 and 9 mg/g were chosen after inspecting the dataset, as illustrative absolute-uptake sensitivity levels, not regulatory or field requirements.',
                 'First sustained sampled attainment means the point and all later sampled points meet the threshold. No behavior between samples or beyond 72 hours is inferred.',
                 'Attainment at the final sample has no later observation to check persistence. Reported zero SD is not proof of no measurement uncertainty.',
                 'Repeat attainment with mean minus 1 or 2 source SD. Compare all 15 material pairs using strict separation of mean +/- k*SD bands at each time.',
                 'SD perturbations are descriptive sensitivity scenarios, not confidence bounds, p-values, predictive guarantees, or evidence of independent batches.',
                 'No percentage of equilibrium is calculated; 72 hours is not assumed to be equilibrium.',
                 'Unmodified BC is retained with signed means. No division by negative uptake or clipping to zero.',
                 'Study-specific batch uptake cannot establish flow-through retention, dilution performance or later flushing losses.'])

def window_text(row):
    if row['status']=='at_first_sample':return 'At first sample (0.5 h)'
    if row['status']=='not_sustained_by_last_sample':return 'Not sustained by 72 h'
    return f"{row['previous_sample_h']:g} -> {row['first_sustained_sample_h']:g} h"

def report(result):
    lines=['# Contact-time computational experiment','',
        'Exploratory secondary analysis of Wang (2021), Dryad [10.5061/dryad.3xsj3txf4](https://doi.org/10.5061/dryad.3xsj3txf4). This uses 72 source means with SD, not 72 independent replicates. No physical experiment was performed.','',
        '## Results at selected measured times','',
        'Values are mean ± reported SD in the kinetic sheet\'s mg/g units under PO4-P. SD is not SE or a confidence interval.','',
        '| Material | 0.5 h | 2 h | 6 h | 24 h | 72 h |','|---|---:|---:|---:|---:|---:|']
    for group in result['selected_observations']:
        lines.append('| '+group['material']+' | '+' | '.join(f"{r['q_mean_mg_g']:.2f} ± {r['q_sd_mg_g']:.2f}" for r in group['observations'])+' |')
    lines += ['', '## Mean rankings across time','',
        'These are descriptive orderings; a small difference does not establish superiority.','',
        '| Time (h) | Descending mean uptake | Separated pairs: ±1 SD | Separated pairs: ±2 SD |',
        '|---:|---|---:|---:|']
    for row in result['rankings']:
        lines.append(f"| {row['time_h']:g} | "+' > '.join(row['ordered_materials'])+' | '+
                     ' | '.join(f"{b['separated_pairs']}/15" for b in row['band_separation'])+' |')
    lines += ['', '## Sampled attainment of exploratory targets','',
        'Each arrow runs from the preceding sample to the first sample that meets the target and remains above it at all later sampled times. It is a sampling-grid bracket, not a fitted crossing time or proof of continuous retention. Attainment at 72 hours has no later sample to check persistence. Equality meets the target. Targets were chosen after data inspection. A source SD displayed as zero is retained as reported; it does not establish absence of measurement uncertainty.','',
        '| Material | 5 mg/g | 8 mg/g | 9 mg/g |','|---|---|---|---|']
    for material,_,_ in MATERIALS:
        chosen=[r for r in result['target_windows'] if r['material']==material and r['sd_multiplier']==0]
        lines.append('| '+material+' | '+' | '.join(window_text(r) for r in chosen)+' |')
    lines += ['', 'All 54 material/target/SD scenarios are in [CSV](../results/kinetic_target_windows.csv). The complete [JSON](../results/kinetic_experiment.json) records methods and source hash. Applying mean minus 1 or 2 SD tests sensitivity to the reported dispersion; it does not estimate a probability of meeting the target.','',
        '## Interpretation and next physical test','',
        'La-BC has the largest reported mean at every sampled time. Mg-BC moves from fifth at 30 minutes to second at 24 hours; its later ordering relative to Ca-BC is not stable. Their very close late-time means should not be used to declare a reliable winner. The SD-band comparison exposes overlap without treating it as a hypothesis test.','',
        'The useful next laboratory question is whether faster batch uptake translates to lower effluent P during the intended residence time, while retaining P during later flushing. Compare shortlisted materials under matched water chemistry, include untreated/media controls, and measure paired inlet/outlet loads across loading and flushing. Select achievable contact times from the actual apparatus and intended runoff regime. There are no observations before 30 minutes and no desorption phase in these kinetics.','',
        'The separate isotherm sheet is excluded because its Qe units require review. This study is not pooled with the poultry-litter dataset. Replicate count and covariance across times are unknown from the workbook; no p-values, fitted rate constants, confidence intervals or field-scale sizing are calculated.','',
        '## Reproduce','', '```sh','python scripts/import_wang.py','python scripts/kinetic_experiment.py',
        'python scripts/kinetic_experiment.py --gigi-url http://127.0.0.1:3147','```','',
        'The final command needs the isolated engine described in the main README. GIGI verifies retrieval, signed values, all twelve ranked time selections, and all three threshold selections; Python computes sampled attainment and SD sensitivity. A planted control must select the larger early value, while removing the time condition must select the late high value. [Live receipts](../results/kinetic_experiment_live.json) contain exact requests/responses and independent comparisons. Offline reproduction does not refresh live evidence.','']
    (ROOT/'docs/KINETIC_EXPERIMENT.md').write_text('\n'.join(lines),encoding='utf8',newline='\n')

def live(rows,url):
    client=Gigi(url); name='biochar_wang_kinetic_summaries_v1'; gate='biochar_contact_rank_gate_v1'
    client.load(name,rows,field_types={'replicate_n':'integer'})
    planted=[dict(id=1,time_h=.5,q=1.),dict(id=2,time_h=.5,q=8.),dict(id=3,time_h=72.,q=99.)]
    client.load(gate,planted)
    query=dict(conditions=[dict(field='time_h',op='eq',value=.5)],sort=[dict(field='q',desc=True)],limit=1)
    if client.call(f'/v1/bundles/{gate}/query',query)['data'][0]['id']!=2:raise ValueError('Planted ranking failed')
    del query['conditions']
    if client.call(f'/v1/bundles/{gate}/query',query)['data'][0]['id']!=3:raise ValueError('Mechanism-removed filter control failed')
    for time in TIMES:
        response=client.call(f'/v1/bundles/{name}/query',dict(conditions=[dict(field='time_h',op='eq',value=float(time))],sort=[dict(field='q_mean_mg_g',desc=True)],limit=1000))
        if response.get('meta',{}).get('truncated'):raise ValueError('Truncated rank query')
        expected=rank_at(rows,time);equivalent(response['data'],expected)
        if [r['id'] for r in response['data']]!=[r['id'] for r in expected]:raise ValueError('Rank order mismatch')
    for target in TARGETS:
        # Combine gt and eq explicitly, using independently checked disjoint sets.
        selected=[]
        for op in ['gt','eq']:
            response=client.call(f'/v1/bundles/{name}/query',dict(conditions=[dict(field='q_mean_mg_g',op=op,value=target)],limit=1000))
            if response.get('meta',{}).get('truncated'):raise ValueError('Truncated target query')
            selected+=response['data']
        equivalent(selected,[r for r in rows if r['q_mean_mg_g']>=target])
    write_json(ROOT/'results/kinetic_experiment_live.json',dict(
        checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        input_sha256=hashlib.sha256((ROOT/'data/processed/wang_kinetics.json').read_bytes()).hexdigest(),
        checks=['Complete roundtrip','Planted filtered ranking','Filter-removed negative control','12 ranked time selections','3 inclusive uptake selections'],
        boundary='GIGI retrieves and ranks; Python computes sampled attainment and SD sensitivity',receipts=client.receipts))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--gigi-url');args=parser.parse_args()
    rows=extract()
    equivalent(rows,json.loads((ROOT/'data/processed/wang_kinetics.json').read_text()))
    result=experiment(rows);write_json(ROOT/'results/kinetic_experiment.json',result)
    with (ROOT/'results/kinetic_target_windows.csv').open('w',encoding='utf8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(result['target_windows'][0]),lineterminator='\n')
        writer.writeheader();writer.writerows(result['target_windows'])
    report(result)
    if args.gigi_url:live(rows,args.gigi_url)
    print(f"Analyzed {len(rows)} source summaries; 12 rankings and {len(result['target_windows'])} target/SD scenarios.")

if __name__=='__main__':main()
