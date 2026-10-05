import sys
from pathlib import Path
import unittest
import hashlib
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze import load_records,validate,screen,summary,equivalent
from extract_table import extract

class AnalysisTests(unittest.TestCase):
    def setUp(self): self.rows=load_records()
    def test_archived_source_checksum(self):
        root=Path(__file__).resolve().parents[1]
        manifest=json.loads((root/'data/source/provenance.json').read_text(encoding='utf8'))
        self.assertEqual(hashlib.sha256((root/'data/source/table1.html').read_bytes()).hexdigest(),manifest['excerpt_sha256'])
    def test_roundtrip_rejects_extra_duplicate(self):
        with self.assertRaises(ValueError):equivalent(self.rows+[self.rows[0]],self.rows)
    def test_complete_source_roundtrip(self):
        self.assertEqual(extract(),self.rows)
        validate(self.rows)
    def test_missing_capacity_is_not_zero(self):
        missing=[r for r in self.rows if r['pmax_mg_p_per_g_biochar'] is None]
        self.assertEqual(len(missing),12)
        self.assertTrue(all(r['pmax_se_mg_p_per_g_biochar'] is None and r['r_squared'] is None for r in missing))
    def test_screen_rejects_planted_misleading_maximum(self):
        fixture=[{'id':1,'r_squared':.01,'pmax_mg_p_per_g_biochar':9999.},{'id':2,'r_squared':.95,'pmax_mg_p_per_g_biochar':5.}]
        self.assertEqual(screen(fixture)[0]['id'],2)
        # Mechanism removed: a capacity-only ranking must fail the accepted-ID criterion.
        self.assertNotEqual(max(fixture,key=lambda r:r['pmax_mg_p_per_g_biochar'])['id'],2)
    def test_threshold_is_strict(self):
        fixture=[{'id':1,'r_squared':.8,'pmax_mg_p_per_g_biochar':9.},{'id':2,'r_squared':.8001,'pmax_mg_p_per_g_biochar':5.}]
        self.assertEqual([r['id'] for r in screen(fixture)],[2])
    def test_known_screen_counts(self):
        result=summary(self.rows)
        self.assertEqual((result['formulations'],result['passing'],result['poor_fit'],result['nr']),(36,16,8,12))
        self.assertEqual([g['passing'] for g in result['activation_groups']],[0,3,4,9])
    def test_sensitivity_changes_leading_recipe(self):
        self.assertEqual(screen(self.rows,.8)[0]['id'],24)
        self.assertEqual(screen(self.rows,.9)[0]['id'],10)
        self.assertEqual([len(screen(self.rows,t)) for t in [.7,.8,.85,.9,.95]],[17,16,14,12,5])
    def test_incomplete_design_rejected(self):
        with self.assertRaises(ValueError):validate(self.rows[:-1])
    def test_duplicate_recipe_rejected(self):
        with self.assertRaises(ValueError):validate(self.rows[:-1]+[self.rows[0]])

if __name__=='__main__':unittest.main()
