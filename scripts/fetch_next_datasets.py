"""Attempt public downloads for the follow-up data inventory; never requires a key.

Keeps successful source files unchanged and records failures honestly. This is
an optional network step, not part of deterministic CI or the current paper.
"""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
CANDIDATES=[
    dict(id='wang_2021_kinetics',doi='10.5061/dryad.3xsj3txf4',file='PO4-P_adsorption_kinetis_and_isotherms_raw_data.xlsx',url='https://datadryad.org/downloads/file_stream/672522',purpose='Kinetic and equilibrium comparisons across metal-loaded reed biochars; batch data, not a runoff trial.'),
    dict(id='dharmakeerthi_2020_flooding',doi='10.5061/dryad.bv10m57',file='Dharmakeerthi_Datadryad.xlsx',url='https://datadryad.org/downloads/file_stream/469737',purpose='Repeated pore-water and floodwater chemistry under cold and warm flooding; release risk, not column breakthrough.')]

def main():
    directory=ROOT/'data/source/next_experiments';directory.mkdir(parents=True,exist_ok=True)
    outcomes=[]
    for item in CANDIDATES:
        result=dict(item)
        try:
            request=urllib.request.Request(item['url'],headers={'User-Agent':'gigi-biochar research reproduction','Accept':'application/octet-stream'})
            with urllib.request.urlopen(request,timeout=45) as response:body=response.read()
            if not body.startswith(b'PK'):raise ValueError('Response was not an XLSX ZIP file')
            (directory/item['file']).write_bytes(body)
            result.update(status='downloaded',bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),license='CC0 (Dryad dataset terms)')
        except (urllib.error.HTTPError,urllib.error.URLError,ValueError,TimeoutError) as error:
            result.update(status='not_downloaded',reason=str(error))
        outcomes.append(result);print(item['id']+': '+result['status']+' '+result.get('reason',''))
    manifest=dict(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Follow-up candidates; not added to the published Padilla analysis',datasets=outcomes)
    (directory/'download_status.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')

if __name__=='__main__':main()
