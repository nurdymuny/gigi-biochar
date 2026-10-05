import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_pdf import verify_hashes,verify_subject

class PdfBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.manifest={'source':'source.tex','pdf':'paper.pdf'}
        for name,key,value in [('source.tex','source_sha256',b'original drawing'),('paper.pdf','pdf_sha256',b'original PDF'),('scripts/build_pdf.py','builder_sha256',b'builder')]:
            p=self.root/name;p.parent.mkdir(exist_ok=True);p.write_bytes(value);self.manifest[key]=hashlib.sha256(value).hexdigest()
    def test_matching_artifacts_pass(self):verify_hashes(self.root,self.manifest)
    def test_source_edit_rejects_stale_pdf(self):
        (self.root/'source.tex').write_bytes(b'changed drawing only')
        with self.assertRaisesRegex(ValueError,'source.tex'):verify_hashes(self.root,self.manifest)
    def test_changed_pdf_is_rejected(self):
        (self.root/'paper.pdf').write_bytes(b'old or unrelated PDF')
        with self.assertRaisesRegex(ValueError,'paper.pdf'):verify_hashes(self.root,self.manifest)
    def test_wrong_embedded_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'stale'):verify_subject('Manuscript source SHA256: old','new')

if __name__=='__main__':unittest.main()
