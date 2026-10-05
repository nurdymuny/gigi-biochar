# Contact-time computational experiment

Exploratory secondary analysis of Wang (2021), Dryad [10.5061/dryad.3xsj3txf4](https://doi.org/10.5061/dryad.3xsj3txf4). This uses 72 source means with SD, not 72 independent replicates. No physical experiment was performed.

## Results at selected measured times

Values are mean ± reported SD in the kinetic sheet's mg/g units under PO4-P. SD is not SE or a confidence interval.

| Material | 0.5 h | 2 h | 6 h | 24 h | 72 h |
|---|---:|---:|---:|---:|---:|
| Al-BC | 1.81 ± 0.30 | 2.86 ± 0.22 | 3.78 ± 0.20 | 6.55 ± 0.37 | 9.25 ± 0.01 |
| Ca-BC | 6.83 ± 0.29 | 7.75 ± 0.12 | 9.56 ± 0.04 | 9.79 ± 0.06 | 9.83 ± 0.01 |
| Fe-BC | 5.87 ± 0.45 | 6.49 ± 0.22 | 7.57 ± 0.31 | 8.82 ± 0.16 | 8.75 ± 0.02 |
| La-BC | 9.82 ± 0.04 | 9.87 ± 0.02 | 9.91 ± 0.01 | 9.91 ± 0.01 | 9.91 ± 0.02 |
| Mg-BC | 1.51 ± 0.02 | 7.38 ± 0.01 | 9.28 ± 0.00 | 9.86 ± 0.02 | 9.82 ± 0.01 |
| BC | -0.33 ± 0.06 | -0.22 ± 0.18 | -0.37 ± 0.33 | -0.43 ± 0.09 | -0.77 ± 0.02 |

## Mean rankings across time

These are descriptive orderings; a small difference does not establish superiority.

| Time (h) | Descending mean uptake | Separated pairs: ±1 SD | Separated pairs: ±2 SD |
|---:|---|---:|---:|
| 0.5 | La-BC > Ca-BC > Fe-BC > Al-BC > Mg-BC > BC | 14/15 | 13/15 |
| 1 | La-BC > Ca-BC > Fe-BC > Al-BC > Mg-BC > BC | 14/15 | 14/15 |
| 1.5 | La-BC > Ca-BC > Fe-BC > Mg-BC > Al-BC > BC | 14/15 | 14/15 |
| 2 | La-BC > Ca-BC > Mg-BC > Fe-BC > Al-BC > BC | 15/15 | 15/15 |
| 3 | La-BC > Ca-BC > Mg-BC > Fe-BC > Al-BC > BC | 15/15 | 14/15 |
| 4 | La-BC > Ca-BC > Mg-BC > Fe-BC > Al-BC > BC | 15/15 | 15/15 |
| 6 | La-BC > Ca-BC > Mg-BC > Fe-BC > Al-BC > BC | 15/15 | 15/15 |
| 8 | La-BC > Ca-BC > Mg-BC > Fe-BC > Al-BC > BC | 14/15 | 14/15 |
| 12 | La-BC > Ca-BC > Mg-BC > Fe-BC > Al-BC > BC | 15/15 | 14/15 |
| 24 | La-BC > Mg-BC > Ca-BC > Fe-BC > Al-BC > BC | 14/15 | 12/15 |
| 48 | La-BC > Ca-BC > Mg-BC > Fe-BC > Al-BC > BC | 14/15 | 14/15 |
| 72 | La-BC > Ca-BC > Mg-BC > Al-BC > Fe-BC > BC | 14/15 | 14/15 |

## Sampled attainment of exploratory targets

Each arrow runs from the preceding sample to the first sample that meets the target and remains above it at all later sampled times. It is a sampling-grid bracket, not a fitted crossing time or proof of continuous retention. Attainment at 72 hours has no later sample to check persistence. Equality meets the target. Targets were chosen after data inspection. A source SD displayed as zero is retained as reported; it does not establish absence of measurement uncertainty.

| Material | 5 mg/g | 8 mg/g | 9 mg/g |
|---|---|---|---|
| Al-BC | 8 -> 12 h | 24 -> 48 h | 48 -> 72 h |
| Ca-BC | At first sample (0.5 h) | 2 -> 3 h | 3 -> 4 h |
| Fe-BC | At first sample (0.5 h) | 6 -> 8 h | Not sustained by 72 h |
| La-BC | At first sample (0.5 h) | At first sample (0.5 h) | At first sample (0.5 h) |
| Mg-BC | 1.5 -> 2 h | 2 -> 3 h | 4 -> 6 h |
| BC | Not sustained by 72 h | Not sustained by 72 h | Not sustained by 72 h |

All 54 material/target/SD scenarios are in [CSV](../results/kinetic_target_windows.csv). The complete [JSON](../results/kinetic_experiment.json) records methods and source hash. Applying mean minus 1 or 2 SD tests sensitivity to the reported dispersion; it does not estimate a probability of meeting the target.

## Interpretation and next physical test

La-BC has the largest reported mean at every sampled time. Mg-BC moves from fifth at 30 minutes to second at 24 hours; its later ordering relative to Ca-BC is not stable. Their very close late-time means should not be used to declare a reliable winner. The SD-band comparison exposes overlap without treating it as a hypothesis test.

The useful next laboratory question is whether faster batch uptake translates to lower effluent P during the intended residence time, while retaining P during later flushing. Compare shortlisted materials under matched water chemistry, include untreated/media controls, and measure paired inlet/outlet loads across loading and flushing. Select achievable contact times from the actual apparatus and intended runoff regime. There are no observations before 30 minutes and no desorption phase in these kinetics.

The separate isotherm sheet is excluded because its Qe units require review. This study is not pooled with the poultry-litter dataset. Replicate count and covariance across times are unknown from the workbook; no p-values, fitted rate constants, confidence intervals or field-scale sizing are calculated.

## Reproduce

```sh
python scripts/import_wang.py
python scripts/kinetic_experiment.py
python scripts/kinetic_experiment.py --gigi-url http://127.0.0.1:3147
```

The final command needs the isolated engine described in the main README. GIGI verifies retrieval, signed values, all twelve ranked time selections, and all three threshold selections; Python computes sampled attainment and SD sensitivity. A planted control must select the larger early value, while removing the time condition must select the late high value. [Live receipts](../results/kinetic_experiment_live.json) contain exact requests/responses and independent comparisons. Offline reproduction does not refresh live evidence.
