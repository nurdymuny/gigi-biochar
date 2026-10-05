"""Compile the manuscript and bind the exported PDF to its exact source.

Requires pdfLaTeX and pypdf. Normal exports update paper/pdf_build.json.
CI uses --output-dir build/ci to compile independently without changing it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',default='paper')
    parser.add_argument('--compiler',default='pdflatex')
    args=parser.parse_args()
    compiler=shutil.which(args.compiler)
    if not compiler:raise SystemExit('pdfLaTeX not found; provide --compiler with its installed path.')
    source=ROOT/'paper/manuscript.tex'
    sha=digest(source)
    out=(ROOT/args.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    command=[compiler,'-interaction=nonstopmode','-halt-on-error','-no-shell-escape',f'-output-directory={out}','-jobname=manuscript',r'\def\ManuscriptSourceSHA{'+sha+r'}\input{paper/manuscript.tex}']
    for _ in range(3):
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf8',errors='replace')
        if result.returncode:
            print(result.stdout[-6000:]);raise SystemExit('PDF build failed; inspect manuscript.log in the output directory.')
    log=(out/'manuscript.log').read_text(encoding='utf8',errors='replace')
    bad=[line for line in log.splitlines() if any(s in line for s in ['undefined','Overfull','Rerun to get','Label(s) may have changed'])]
    if bad:raise SystemExit('Unresolved PDF diagnostics:\n'+'\n'.join(bad))
    if digest(source)!=sha:raise SystemExit('Source changed during compilation; rerun the build.')
    from pypdf import PdfReader
    reader=PdfReader(out/'manuscript.pdf')
    if reader.metadata.get('/Subject')!='Manuscript source SHA256: '+sha:
        raise SystemExit('Compiled PDF lacks the expected source digest.')
    if out==(ROOT/'paper').resolve():
        manifest=dict(source='paper/manuscript.tex',source_sha256=sha,pdf='paper/manuscript.pdf',pdf_sha256=digest(out/'manuscript.pdf'),builder_sha256=digest(Path(__file__)),pages=len(reader.pages),method='Three pdfLaTeX passes; exact source digest embedded during compilation; no unresolved references or overflow.')
        (out/'pdf_build.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
    print(f'Compiled {len(reader.pages)} pages; source SHA256 {sha}')

if __name__=='__main__':main()
