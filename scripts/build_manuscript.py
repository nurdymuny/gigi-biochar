"""Build the standalone LaTeX manuscript from a prose template and verified data.

Edit paper/manuscript_template.tex for prose, then run this script. The output
manuscript.tex is self-contained and can also be edited directly in an editor.
Rebuilding replaces manual edits to the generated output.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    rows=json.loads((ROOT/'data/processed/capture_records.json').read_text(encoding='utf8'))
    results=json.loads((ROOT/'results/summary.json').read_text(encoding='utf8'))
    byid={r['id']:r for r in rows};ranked=[byid[i] for i in results['ranked_ids']]
    table=[]
    for r in results['activation_groups']:
        ran='--' if r['passing_range'] is None else f"{r['passing_range'][0]:.2f}--{r['passing_range'][1]:.2f}"
        table.append(f"{r['mg_molar']:g} & {r['total']} & {r['passing']} & {r['poor_fit']} & {r['nr']} & {ran} \\\\")
    sensitivity=[]
    for r in results['threshold_sensitivity']:
        top=byid[r['top_id']]
        sensitivity.append(f"{r['threshold']:.2f} & {r['passing']} & {r['one_molar_passing']} & {top['feedstock']}, {top['pyrolysis_c']} & {top['pmax_mg_p_per_g_biochar']:.2f} $\\pm$ {top['pmax_se_mg_p_per_g_biochar']:.2f} \\\\")
    plot='\n'.join(f"{r['pmax_mg_p_per_g_biochar']} {len(ranked)-i} {r['pmax_se_mg_p_per_g_biochar']}" for i,r in enumerate(ranked))
    labels=','.join('{'+f"{r['feedstock']} / {r['mg_activation_molar']:g} / {r['pyrolysis_c']}"+'}' for r in reversed(ranked))
    inventory=[]
    for r in rows:
        cap='NR' if r['pmax_mg_p_per_g_biochar'] is None else f"{r['pmax_mg_p_per_g_biochar']:.2f} $\\pm$ {r['pmax_se_mg_p_per_g_biochar']:.2f}"
        r2='--' if r['r_squared'] is None else f"{r['r_squared']:.2f}"
        state='NR' if r['r_squared'] is None else 'Retained' if r['r_squared']>.8 else 'Excluded'
        inventory.append(f"{r['id']} & {r['feedstock']} & {r['mg_activation_molar']:g} & {r['pyrolysis_c']} & {cap} & {r2} & {state} \\\\")
    template=(ROOT/'paper/manuscript_template.tex').read_text(encoding='utf8')
    raw=json.loads((ROOT/'data/processed/isotherm_records.json').read_text(encoding='utf8'))
    panels=[]
    for mg in [0,.25,.5,1.]:
        pairs='\n'.join(f"{r['solution_p_mg_l']:.12g} {r['sorbed_p_mg_g']:.12g}" for r in raw if r['mg_activation_molar']==mg)
        panels.append('\\nextgroupplot[title={'+f'{mg:g} M Mg'+'}]\n\\addplot[gray,dashed] coordinates {(0,0) (190,0)};\n\\addplot[only marks,mark=*,mark size=1.25pt,blue!55!black] table[header=false] {\n'+pairs+'\n};')
    template=template.replace('@@RAW_PLOTS@@','\n'.join(panels))
    kinetic=json.loads((ROOT/'results/kinetic_experiment.json').read_text(encoding='utf8'))
    records=json.loads((ROOT/'data/processed/wang_kinetics.json').read_text(encoding='utf8'))
    time_rows=[];target_rows=[];kinetic_panels=[]
    for group in kinetic['selected_observations']:
        material=group['material']
        time_rows.append(material+' & '+' & '.join(f"{r['q_mean_mg_g']:.2f} $\\pm$ {r['q_sd_mg_g']:.2f}" for r in group['observations'])+r' \\')
        targets=[r for r in kinetic['target_windows'] if r['material']==material and r['sd_multiplier']==0]
        cells=[]
        for r in targets:
            if r['status']=='at_first_sample': cells.append('First sample (0.5)')
            elif r['status']=='not_sustained_by_last_sample':cells.append('Not by 72')
            else:cells.append(f"{r['previous_sample_h']:g} $\\to$ {r['first_sustained_sample_h']:g}")
        target_rows.append(material+' & '+' & '.join(cells)+r' \\')
        points='\n'.join(f"{r['time_h']:g} {r['q_mean_mg_g']:g} {r['q_sd_mg_g']:g}" for r in records if r['material']==material)
        kinetic_panels.append(r'\nextgroupplot[title={'+material+r'}]'+'\n'+
            r'\addplot[gray,dashed] coordinates {(0.5,0) (72,0)};'+'\n'+
            r'\addplot+[only marks,mark=*,mark size=1.8pt,blue!65!black,error bars/.cd,y dir=both,y explicit] table[x index=0,y index=1,y error index=2,header=false] {'+'\n'+points+'\n};')
    template=template.replace('@@KINETIC_ROWS@@','\n'.join(time_rows)).replace('@@TARGET_ROWS@@','\n'.join(target_rows)).replace('@@KINETIC_PANELS@@','\n'.join(kinetic_panels))
    for key,val in {'ACTIVATION_ROWS':'\n'.join(table),'SENSITIVITY_ROWS':'\n'.join(sensitivity),'PLOT_DATA':plot,'PLOT_LABELS':labels,'INVENTORY_ROWS':'\n'.join(inventory)}.items():template=template.replace('@@'+key+'@@',val)
    if '@@' in template:raise ValueError('Unresolved manuscript placeholder')
    (ROOT/'paper/manuscript.tex').write_text(template,encoding='utf8',newline='\n')
    print('Built standalone manuscript.tex')

if __name__=='__main__':main()
