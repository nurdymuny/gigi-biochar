import collections
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from import_dryad import extract,summarize

class DryadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows,cls.sheets=extract()
    def test_source_files_unchanged(self):
        manifest=json.loads((ROOT/'data/source/dryad/provenance.json').read_text())
        for name,digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/'data/source/dryad'/name).read_bytes()).hexdigest(),digest)
    def test_all_source_pairs_preserved(self):
        self.assertEqual(self.rows,json.loads((ROOT/'data/processed/isotherm_records.json').read_text()))
        self.assertEqual(len(self.rows),540)
        self.assertEqual(collections.Counter(collections.Counter(r['formulation_id'] for r in self.rows).values()),{15:36})
    def test_known_cells_and_release_sign(self):
        first=self.rows[0]
        self.assertEqual(first['source_cells'],'E9:F9')
        self.assertEqual(first['solution_p_mg_l'],35.54)
        self.assertAlmostEqual(first['sorbed_p_mg_g'],-2.072222222222222)
        counts=[g['negative_sorption'] for g in summarize(self.rows,self.sheets)['activation_groups']]
        self.assertEqual(counts,[93,52,26,0])
    def test_identity_anomalies_are_not_silently_joined(self):
        result=summarize(self.rows,self.sheets)
        self.assertEqual(set(result['label_anomalies']),{'Figure 1 and Sup. Fig. S2','Proximate Analysis'})
        self.assertEqual({r['feedstock'] for r in self.rows},{'PL1','PL3','PL7'})

if __name__=='__main__':unittest.main()
