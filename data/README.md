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
