# Next experiment: capture during flow, retention during flushing

The current analysis supports a shortlist of materials for testing. The next decision is whether a candidate **removes a net phosphorus load during short flow events and retains it through subsequent flushing**. A high equilibrium capacity after 24 hours does not establish either result.

This document is a proposed research plan, not a performed experiment or an engineered treatment specification. The existing paper's column drawing shows the sampling arrangement. Resolve the target water chemistry, laboratory resources, and experimental unit with the collaborating laboratory before fixing the protocol.

The first **computational** follow-up has now been run: [contact-time experiment](KINETIC_EXPERIMENT.md), with verified GIGI rankings, sampled target attainment and SD sensitivity. The paper includes its results in Appendix B. The physical column experiment below still requires new laboratory measurements.

## What data we already have

The frozen [Padilla workbook](../data/source/dryad/Compiled_Data.xlsx) contains the 540 isotherm observations used in the paper and additional sheets that have not been normalized into the analysis.

- `Sup. Fig. S1`, cells C6:G32, contains 27 sorbed-P measurements: PL1, PL3 and PL7 at 700 degrees C, at days 1, 2 and 3, with source replication labels 1–3. The earliest measurement is 24 hours. These data can describe the measured day-scale pattern, but cannot estimate capture during minutes of stormwater contact. The sheet does not identify Mg activation in its data columns; establish treatment metadata from the paper before joining it to a formulation.
- Other sheets contain additional material characterization and release-related measurements. Review units, treatment labels and experimental replication before extracting them. Some use PL9 where the paper and isotherm sheet use PL7. Do not silently relabel those records.
- A reviewed refit of the archived isotherms could estimate affinity as well as capacity, with uncertainty and model checks. That would extend the present analysis, which does not fit new models. It would still not provide measured breakthrough or flushing losses.

## Public follow-up data located

Checked 5 October 2026. Each dataset answers a different part of the problem; do not pool their observations as interchangeable replicates.

| Source | Available measurements and use | Acquisition status |
|---|---|---|
| [Wang et al. Dryad dataset](https://datadryad.org/dataset/doi:10.5061/dryad.3xsj3txf4), associated [2021 paper](https://doi.org/10.1098/rsos.201789) | Phosphate adsorption kinetics and isotherms for reed biochars loaded with different metal oxides. Different feedstock and chemistry from Padilla. | Acquired from the user-supplied 22 April 2021 ZIP after automated download failed. Unchanged workbook archived; 72 kinetic mean/SD summaries extracted and verified in GIGI. |
| [Dharmakeerthi et al. Dryad dataset](https://datadryad.org/dataset/doi:10.5061/dryad.bv10m57), associated [paper](https://doi.org/10.2134/jeq2019.02.0091) | Pore-water and floodwater chemistry during cold and warm flooding of two soils, with biochar, gypsum and unamended treatments. Useful for assessing release under different soil/water conditions; not a column-breakthrough dataset. | `Dharmakeerthi_Datadryad.xlsx` is listed. Direct download returned HTTP 403 here. No measurements imported. |
| [McCrum, Heyvaert and Schmidt (2017), Evaluation of Pinyon-Juniper Biochar as a Media Amendment for Stormwater Treatment](https://lands.nv.gov/uploads/documents/3._Evaluation_of_P-J_biochar_final_report_.pdf) | Public report includes batch and column adsorption/desorption work. Useful for designing a capture-plus-flush experiment. | Report readable; a separate raw time-series archive has not been located. Report figures are not treated as raw observations. |

The two Dryad datasets are offered under CC0. Their terms are separate from this repository's original code and manuscript licenses. Third-party PDFs are linked, not relicensed by this project.

### First descriptive kinetic comparison

The Wang workbook has six materials measured at 12 times from 0.5 to 72 hours. Its entries are means and standard deviations; individual replicates and their count are not supplied in the workbook. Reported mean uptake at the first measured time (30 minutes) is:

| Material | Mean ± reported SD (mg/g) |
|---|---:|
| Al-BC | 1.81 ± 0.30 |
| Ca-BC | 6.83 ± 0.29 |
| Fe-BC | 5.87 ± 0.45 |
| La-BC | 9.82 ± 0.04 |
| Mg-BC | 1.51 ± 0.02 |
| Unmodified BC | −0.33 ± 0.06 |

These are within-study descriptions, not significance rankings or recommendations for field deployment. Mg-BC reaches 9.86 ± 0.02 mg/g at 24 hours. Contact time therefore warrants direct testing. The unmodified BC has 11 negative means among its 12 time points; preserve this release signal. No uptake before 30 minutes, kinetic mechanism, or uncertainty on an unobserved treatment is inferred. The source kinetics header uses mg/g under PO4-P; no phosphate-to-P conversion is applied.

The second sheet contains 60 isotherm summaries, but its Qe headers say mg/L, whereas kinetic Q is mg/g. These values remain in the unchanged workbook and are excluded from quantitative normalization pending unit review. The repository does not silently repair the header or fit new isotherms.

Reproduce the follow-up offline or verify it against an isolated GIGI instance:

```sh
python scripts/import_wang.py
python scripts/import_wang.py --gigi-url http://127.0.0.1:3147
```

The second command requires the server setup described in the main README. It creates/reuses `biochar_wang_kinetic_summaries_v1` and a two-record synthetic gate bundle, verifies every record and all 12 time selections, and records exact HTTP receipts. Source provenance is in [wang_2021/provenance.json](../data/source/wang_2021/provenance.json); outputs are [CSV](../data/processed/wang_kinetics.csv), [summary](../results/wang_summary.json), and [live receipts](../results/wang_live_verification.json). To deliberately rearchive a supplied ZIP, add `--archive /path/to/archive.zip`; this replaces the archived workbook and its provenance, so review the diff and version before accepting it.

### Reattempt or supply the workbooks

From the repository root, an optional network acquisition step is:

```sh
python scripts/fetch_next_datasets.py
```

It writes unchanged successful XLSX responses into `data/source/next_experiments/` and records successes or failures in [download_status.json](../data/source/next_experiments/download_status.json). This step is not part of deterministic CI. An exit code of zero means the acquisition attempts were recorded, not that both files downloaded. Inspect each `status` and checksum. The checked-in manifest records the initial automated failures; the subsequently supplied Wang archive has its own provenance under `data/source/wang_2021/`. Do not interpret the earlier network failure as absence of that now-archived workbook. The flooded-soil workbook is still pending.

Alternatively, use the Download controls on the two dataset pages and place the named workbooks in that directory. Record the dataset version, retrieval date, file size and SHA-256 before extraction. Do not overwrite the frozen Padilla workbook or append new measurements to its bundles. A browser download supplied by a collaborator is acceptable provenance when its original file and retrieval details are preserved.

Before analysis, inspect sheets and headers, distinguish mg P/L from mg phosphate/L, preserve signed values and detection-limit qualifiers, identify controls and replication, and map every extracted value back to a cell. Missing metadata must remain missing. A kinetic model needs actual times, concentrations and batch conditions; a time-series plot alone does not establish its mechanism.

## Proposed laboratory sequence

### 1. Establish realistic contact times and release controls

Measure representative agricultural drainage or runoff first: dissolved reactive phosphorus (DRP), total phosphorus (TP), pH, conductivity, dissolved organic carbon, major ions, suspended solids, temperature and event flow. Select concentrations and contact times from that target system. Keep a standardized phosphate solution as a separate comparison matrix.

Start with one or two shortlisted Mg-treated recipes, their corresponding untreated biochars, a media-only hydraulic control, and reagent/method blanks. Include an established sorbent benchmark if the laboratory has one. Prewashing is a treatment choice: record its water volume and exported P instead of discarding that loss from the accounting.

Use independent preparation batches as material replicates and independent columns as experimental units. Repeated effluent samples from one column are a time series, not independent column replicates. Randomize column assignments and block runs when apparatus capacity requires multiple days. A small pilot can estimate batch and column variation; set confirmatory replication using that variation and a stated minimum useful reduction, not the present table's parameter SE.

Measure short-contact uptake and P release in P-free water before selecting column conditions. Include early observations spanning the intended residence time and later observations that check approach to equilibrium. Predefine sampling times, preservation, filtration, analytical method, calibration checks and handling of values below quantification limits.

### 2. Run repeated loading events followed by flushing

Record dry biochar mass, other bed media, particle size, bed dimensions, packing, porosity estimate, influent composition, temperature and measured flow. Report empty-bed contact time (bed volume divided by flow) separately from measured pore-water residence time. A tracer measurement can identify bypass or substantial residence-time differences between treatments.

Collect paired influent and effluent samples with corresponding measured volumes through each event. Follow loading with low-P flushing under a defined water chemistry and volume, and repeat the sequence. Sample densely enough to resolve the rise in effluent P; measure head loss or pressure as well as capture. Track DRP and TP separately to distinguish dissolved capture from particle retention, and assess Mg release and pH shifts for Mg-treated materials.

Predefine breakthrough operationally. For example, the first sustained effluent/influent DRP ratio above 0.10 can be a pilot criterion, but it is a design choice, not a universal standard. Specify the duration or number of samples required, the treatment of changing influent concentrations, and any absolute effluent limit relevant to the intended application. Ratios are not meaningful when influent P is approximately zero; use mass release during those flushes.

### 3. Use the complete event mass balance

For fraction-integrated samples, calculate P mass as concentration times measured fraction volume and sum across loading **and flushing**:

```text
M_in  = sum(C_in,i  * V_in,i)
M_out = sum(C_out,i * V_out,i)
net retained P per dry g biochar = (M_in - M_out) / dry biochar mass
```

Concentrations in mg P/L and volumes in L give mg P. With grab samples, state and test the time/flow integration rule instead of assuming that a single sample represents an entire fraction. Include prewash export explicitly or report it as a separate lifecycle debit. Account for final pore-water storage and sampling withdrawals when material to the budget. Report control-column results alongside treatment results and explain any correction rather than hiding it.

Primary outcomes should include cumulative net retention, effluent concentration through time, flushing loss, and breakthrough in time and bed volumes. A negative net balance is release, not a zero to truncate. Avoid percentages when the input mass is negligible. Uncertainty should reflect independent batches/columns and analytical uncertainty; report incomplete breakthrough curves as censored rather than extrapolating an unobserved capacity. Close the P budget with retained-P measurements when feasible and report recovery discrepancies.

## Data structure for GIGI

Keep a material/batch table, a column table, and a fraction-level measurement table linked by explicit identifiers. Suggested required measurement fields are:

```text
study_id, batch_id, material_id, column_id, event_id, phase,
sample_id, collection_start, collection_end, elapsed_minutes,
influent_volume_l, effluent_volume_l,
influent_drp_mg_p_l, effluent_drp_mg_p_l,
influent_tp_mg_p_l, effluent_tp_mg_p_l,
ph_in, ph_out, temperature_c, flow_ml_min,
qualifier, method_id, source_file, source_sheet, source_cell
```

Material metadata carry feedstock, activation, pyrolysis, washing and dry mass; column metadata carry dimensions, media mixture and packing. Define null versus measured zero and store quantification limits separately. Keep actual measurement times rather than inferred row order. Public studies and the laboratory's own experiment should have separate study identifiers and source versions.

GIGI can retain these linked records, select comparable conditions and calculate validated summaries. Independently reproduce each mass balance in Python and plant a known capture-and-release example before trusting a live query. Keep original measurements immutable and save the exact requests/responses. Do not invoke geometric or time-series methods simply because they exist: their sampling and uncertainty requirements must match the measurements.

## What would justify the next claim?

A candidate advances when independent columns show useful net retention across loading and flushing under the target water conditions, with uncertainty and hydraulic performance acceptable to the laboratory's predefined criteria. Batch kinetics, flooded-soil release and engineered-column evidence can inform this design; none alone establishes reduced phosphorus runoff from a farm. Field or pilot-scale performance remains a subsequent experiment.
