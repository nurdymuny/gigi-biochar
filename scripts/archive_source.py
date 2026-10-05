"""Archive only the attributed source table from a downloaded publisher page.

Usage: python scripts/archive_source.py /path/to/downloaded/table-page.html
This is an explicit source-update operation. Review changes before committing.
"""
import argparse,datetime,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source_page',type=Path);args=parser.parse_args()
    raw=args.source_page.read_bytes(); match=re.search(r'<table.*?</table>',raw.decode('utf8'),re.S)
    if not match:raise ValueError('No table found in supplied HTML')
    excerpt='<!doctype html><html lang="en"><meta charset="utf-8"><title>Padilla et al 2023 Table 1</title><body><h1>Published sorption capacity summaries</h1><p>Padilla et al. (2023), Biochar 5, 64. DOI: 10.1007/s42773-023-00263-5. Table 1. CC BY 4.0.</p>'+match.group()+'<p>Estimates of Pmax were obtained from Langmuir model descriptions of observed isotherm data. NR: Net P release. Units: mg P/g biochar; plus/minus: standard error.</p></body></html>'
    path=ROOT/'data/source/table1.html';path.write_text(excerpt,encoding='utf8')
    metadata=dict(source_doi='10.1007/s42773-023-00263-5',table_url='https://link.springer.com/article/10.1007/s42773-023-00263-5/tables/1',raw_data_doi='10.5061/dryad.pc866t1w7',prepared_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),license='CC-BY-4.0',source_kind='Published fitted summaries',excerpt_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),original_page_sha256=hashlib.sha256(raw).hexdigest(),transformations=['Extract Table 1 and preserve explanatory footnote','Expand temperatures into formulation rows','Preserve NR as null; no imputation'],raw_workbook_status='Initial direct download failed; subsequently supplied and archived unchanged in data/source/dryad. See its separate provenance.json.')
    (ROOT/'data/source/provenance.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
