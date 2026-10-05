import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from import_wang import extract, RAW, FILE, SHEET, MATERIALS, TIMES
from import_dryad import workbook_cells

class WangTests(unittest.TestCase):
    def test_all_means_and_sd_match_cells(self):
        rows=extract();cells=workbook_cells(RAW/FILE)[SHEET]
        self.assertEqual(len(rows),72)
        self.assertEqual(rows,json.loads((ROOT/'data/processed/wang_kinetics.json').read_text()))
        self.assertEqual({(r['material'],r['time_h']) for r in rows},
                         {(m,t) for m,_,_ in MATERIALS for t in TIMES})
        for r in rows:
            self.assertEqual(r['q_mean_mg_g'],cells[r['source_mean_cell']])
            self.assertEqual(r['q_sd_mg_g'],cells[r['source_sd_cell']])
            self.assertIsNone(r['replicate_n'])
    def test_known_signed_controls_and_uncertainty(self):
        rows=extract()
        bc=next(r for r in rows if r['material']=='BC' and r['time_h']==.5)
        self.assertEqual(bc['q_mean_mg_g'],-.33)
        self.assertEqual(bc['q_sd_mg_g'],.06)
        self.assertEqual(sum(r['q_mean_mg_g']<0 for r in rows),11)
        self.assertEqual(rows[0]['uncertainty_type'],'source standard deviation')
        self.assertEqual(rows[0]['observation_type'],'summary mean')

if __name__=='__main__':unittest.main()
