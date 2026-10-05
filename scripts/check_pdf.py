"""Reject stale source/PDF pairs; optionally compare an independent PDF build.

The content comparison normalizes whitespace and ligatures, not numbers or words.
Source digest binding also detects edits to drawings without textual changes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata
ROOT=Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_hashes(root,manifest):
    for name,key in [(manifest['source'],'source_sha256'),(manifest['pdf'],'pdf_sha256'),('scripts/build_pdf.py','builder_sha256')]:
        if digest(root/name)!=manifest[key]:raise ValueError('PDF build manifest mismatch: '+name)

def verify_subject(subject,source_digest):
    if subject!='Manuscript source SHA256: '+source_digest:raise ValueError('PDF source digest is missing or stale')

def normalized_text(reader):
    return re.sub(r'\s+','',unicodedata.normalize('NFKC','\n'.join(page.extract_text() or '' for page in reader.pages)))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--compare',type=Path);args=parser.parse_args()
    manifest=json.loads((ROOT/'paper/pdf_build.json').read_text())
    verify_hashes(ROOT,manifest)
    from pypdf import PdfReader
    stored=PdfReader(ROOT/manifest['pdf'])
    verify_subject(stored.metadata.get('/Subject'),manifest['source_sha256'])
    if len(stored.pages)!=manifest['pages']:raise ValueError('Published page count changed')
    if args.compare:
        fresh=PdfReader(args.compare)
        verify_subject(fresh.metadata.get('/Subject'),manifest['source_sha256'])
        if len(stored.pages)!=len(fresh.pages):raise ValueError('Independent build page count differs; review layout')
        if normalized_text(stored)!=normalized_text(fresh):raise ValueError('Independent build text differs; review exported PDF')
    print('PDF source binding, artifact hash and'+(' independent build content' if args.compare else ' page count')+' verified.')

if __name__=='__main__':main()
