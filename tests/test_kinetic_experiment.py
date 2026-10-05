import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from kinetic_experiment import rank_at,sustained_window,band_separated

def point(t,q,sd=0.,material='x'):
    return dict(time_h=t,q_mean_mg_g=q,q_sd_mg_g=sd,material=material)

class ContactTimeTests(unittest.TestCase):
    def test_rank_uses_time_and_signed_means(self):
        rows=[point(.5,-1,material='release'),point(.5,4,material='early'),point(72,99,material='late')]
        self.assertEqual([r['material'] for r in rank_at(rows,.5)],['early','release'])
    def test_transient_crossing_is_not_sustained(self):
        rows=[point(.5,4),point(1,6),point(2,3),point(4,5),point(8,6)]
        self.assertEqual(sustained_window(rows,5),dict(status='observed',previous_sample_h=2,first_sustained_sample_h=4))
    def test_no_attainment_and_first_sample_are_distinct(self):
        self.assertEqual(sustained_window([point(.5,-1),point(72,-2)],5)['status'],'not_sustained_by_last_sample')
        self.assertEqual(sustained_window([point(.5,5),point(72,6)],5),dict(status='at_first_sample',previous_sample_h=None,first_sustained_sample_h=.5))
    def test_sd_scenario_changes_attainment(self):
        rows=[point(.5,5,.5),point(2,6,.1)]
        self.assertEqual(sustained_window(rows,5,0)['first_sustained_sample_h'],.5)
        self.assertEqual(sustained_window(rows,5,1)['first_sustained_sample_h'],2)
    def test_touching_bands_are_not_separated(self):
        self.assertFalse(band_separated(point(1,5,1),point(1,3,1),1))
        self.assertTrue(band_separated(point(1,5,1),point(1,2,1),1))
        self.assertFalse(band_separated(point(1,5,1),point(1,2,1),2))

if __name__=='__main__':unittest.main()
