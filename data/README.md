# Data dictionary and provenance

## Published fit summaries

Each row represents one biochar formulation and its published Langmuir fit summary, not an independent experimental replicate. All 36 factorial combinations are present. Data origin: Padilla et al. (2023), Table 1, DOI 10.1007/s42773-023-00263-5.

| Field | Meaning |
|---|---|
| `id` | Stable local row identifier, 1–36 |
| `feedstock` | Published PL1, PL3 or PL7 code |
| `feedstock_age_years` | Published age category, as text |
| `mg_activation_molar` | Mg activation solution concentration, mol/L; not a measured Mg content in the final biochar |
| `pyrolysis_c` | Final pyrolysis temperature, degrees Celsius |
| `pmax_mg_p_per_g_biochar` | Published fitted Langmuir maximum capacity, mg P/g biochar |
| `pmax_se_mg_p_per_g_biochar` | Published standard error of Pmax, in the same units |
| `r_squared` | Published model-fit R², rounded to two decimal places |
| `fit_screen` | Derived primary screening label using strict R² > 0.80 |
| `source_table_row` | One-based table body row before expanding temperature columns |
| `source_cell` | Original capacity cell text, including NR/footnote markers |
| `source_url` | Direct published table URL |

## Extraction

The table's feedstock cells span four rows. Extraction carries that label down and expands each temperature's capacity/SE and R² pair into a row. No values are imputed. NR cells yield null capacity, SE and R². JSON preserves null; CSV writes a blank. The source table defines NR as net P release; the numerical amount of release is not supplied.

The current parser deliberately validates this table's exact 12-row layout rather than attempting to infer arbitrary future tables. The source excerpt and provenance manifest preserve attribution and SHA-256 checksums.

## Interpretation limits

- R² is a fit diagnostic, not independent predictive validation or a field-performance probability.
- SE is not a 95% interval and does not measure independent manufacturing-batch variability.
- The strict cutoff is applied to displayed, rounded R². Values close to the cutoff cannot be resolved more finely.
- The paper's threshold wording is not entirely consistent: the figure description uses >0.80; another passage excludes <0.80. No displayed value is exactly 0.80, so this does not change the primary subset. Sensitivity thresholds are explicitly strict.
- Capacity fits, especially those from linearized isotherms, cannot establish removal at a specified low water concentration without additional fitted parameters and data.
- The source table gives PL7 / 0.25 M / 900 °C as 0.62 ± 0.06 with R² 0.96. The article narrative gives a 0.66 minimum. The table is preserved without correction.

## Archived isotherm measurements

`isotherm_records.json` and `.csv` preserve 540 paired observations from the unchanged Dryad workbook, version 10 October 2023. The workbook and original README are in `source/dryad`, together with their byte hashes and the original supplied archive hash. The earlier download failure was resolved when the user supplied the public archive. No Excel formulas or macros are executed.

| Field | Meaning |
|---|---|
| `id` | Unique local observation identifier, 1–540 |
| `formulation_id` | Link to a published formulation using exact feedstock, temperature, and activation keys |
| `feedstock` | PL1, PL3, or PL7, as written on the isotherm sheet |
| `pyrolysis_c` | Source temperature label parsed as degrees Celsius |
| `mg_activation_molar` | Source activation-solution concentration, mol/L |
| `point_index` | Position 1–15 within the source formulation block; not an inferred replicate identity or time |
| `solution_p_mg_l` | Source solution P concentration, mg/L |
| `sorbed_p_mg_g` | Source sorbed P, mg/g; negative values preserved as net release |
| `source_sheet` | Exact worksheet name |
| `source_cells` | Excel cell pair such as E9:F9, enabling direct source review |

The exact source sheet is `Figure 5 and Sup. Fig. S5`. Its nine header blocks contain four activation conditions each, and each condition has 15 numeric pairs. Concentration conditions and replicate identities are not reconstructed from position alone. No fitting or imputation occurs. Counts by activation pool materials and concentration conditions and cannot be interpreted as independent experimental success probabilities.

Other workbook sheets are archived but not quantitatively analyzed here. Two contain PL9 labels (`Figure 1 and Sup. Fig. S2` and `Proximate Analysis`), which are flagged rather than mapped silently to PL7. The workbook's general notes also give a mismatched isotherm tab name. Source labels, units, signs, and location references are retained to support a reviewed future analysis.

## Separate Wang kinetic summaries

`wang_kinetics.json` and `.csv` contain 72 means with source SD from `source/wang_2021/PO4-P_adsorption_kinetis_and_isotherms_raw_data.xlsx`, Dryad DOI 10.5061/dryad.3xsj3txf4, version 22 April 2021. These belong to a different study and are not joined to Padilla formulation IDs. The separate contact-time analysis appears in Appendix B and `docs/KINETIC_EXPERIMENT.md`.

| Field | Meaning |
|---|---|
| `id`, `study_id` | Local record ID and explicit study identifier |
| `material` | Source label: Al-BC, Ca-BC, Fe-BC, La-BC, Mg-BC or unmodified BC |
| `time_h` | Measured sampling time, hours; 0.5–72 |
| `q_mean_mg_g` | Reported mean Q, retaining the sheet's mg/g unit under PO4-P |
| `q_sd_mg_g` | Reported standard deviation, same units; not SE or a confidence interval |
| `replicate_n` | Null because replicate count is not given in the workbook; blank in CSV |
| `uncertainty_type`, `observation_type` | Explicit labels distinguishing SD and summary means from individual observations |
| `source_sheet` | `PO4-P adsorption kinetics` |
| `source_time_cell`, `source_mean_cell`, `source_sd_cell` | Exact Excel addresses for each value |

No conversion of phosphate mass to elemental phosphorus mass is applied. The archived isotherm sheet labels Qe in mg/L rather than mg/g; its 60 summaries are not normalized pending unit review. Do not use its source column name as evidence that the dimensional discrepancy is resolved. Other members of the supplied ZIP are inventoried in provenance but not extracted or analyzed.

The derived `results/kinetic_target_windows.csv` records `material`, the exploratory `target_mg_g`, and `sd_multiplier` (0, 1 or 2 applied as mean minus multiplier times SD). `first_sustained_sample_h` identifies the first sampled value meeting the target with all later sampled values also meeting it. `previous_sample_h` is the preceding grid time, not a fitted lower confidence bound. `status` distinguishes attainment at the first sample, later observed attainment and no sustained attainment by the final sample. Null times are blank CSV cells, not zero. A final-sample attainment has no later observation to test persistence. These are 54 descriptive scenarios, not 54 experiments or hypothesis tests.
