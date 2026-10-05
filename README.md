# Biochar phosphorus capture with GIGI

A reproducible secondary analysis of **36 published biochar formulations and 540 archived isotherm observations**, with a scientific LaTeX research note, technical drawings, complete source provenance, and verified database queries.

**Question:** Which biochar capacity estimates warrant follow-up testing for phosphorus capture after accounting for weak model fits and phosphorus release?

This project analyzes Padilla et al. (2023) and its public Dryad workbook. It does not report new experiments, demonstrate reduced field runoff, establish a statistically optimal material, or refit the original isotherm models. The paper proposes a next experiment for testing runoff applications.

## Read the results

- [Scientific paper (PDF)](paper/manuscript.pdf) and [standalone LaTeX source](paper/manuscript.tex).
- [36 formulation summaries (CSV)](data/processed/capture_records.csv) and [540 measured pairs (CSV)](data/processed/isotherm_records.csv).
- [Data dictionary](data/README.md), [screening summary](results/summary.json), and [measurement summary](results/isotherm_summary.json).
- [Published-table provenance](data/source/provenance.json) and [Dryad workbook provenance](data/source/dryad/provenance.json).
- [Live screening evidence](results/live_verification.json) and [live measurement evidence](results/isotherm_live_verification.json).

The manuscript includes two original vector technical drawings: the fiber-bundle record organization and a proposed upflow-column experiment with sampling locations and phosphorus mass balance. Its other figures show reported capacity estimates with SE and all 540 signed sorption observations. All graphics are embedded as editable TikZ/PGFPlots code in the standalone source.

## What is a fiber bundle database? A sample-tray analogy

Imagine a laboratory sample tray with a permanent label at each occupied position. At position 24, a measurement card holds the recipe, phosphorus capacity, standard error, fit score, and source. The label answers **which formulation?** The card answers **what is recorded about it?**

| Fiber-bundle idea | Sample-tray analogy | This study |
|---|---|---|
| Base space | The labeled positions | Unique formulation identifiers 1–36 |
| Fiber | The possible entries on the attached card | Recipe, capacity, SE, fit quality, and provenance fields |
| Stored values | The completed card | ID 24: PL3, 1 M Mg, 900 degrees C, capacity 10.35 mg P/g, SE 1.45, R² 0.90 |
| Bundle | The tray and its attached cards | The named collection `biochar_capture_paper_v1` |

The word *possible* matters: the fiber describes where values can live, rather than only the specific values observed. In mathematics, a *section* chooses a value in the fiber over each base point. For this finite dataset, think of stored records as assignments of observed values to labeled positions. The analogy explains the organization; it does not prove that the formulations form a smooth physical surface.

A blank capacity box remains blank. The source's **NR** label means net phosphorus release; its missing fitted capacity is not a measurement of zero. Adjacent identifiers also do not mean adjacent chemistry: ID 24 is not scientifically closer to ID 25 merely because their numbers are consecutive.

GIGI uses this organization for database operations and geometric analyses. Scientifically meaningful distances require choices about units, scaling, categorical encoding, missingness, and which features to include. One degree of temperature is not interchangeable with one mg P/g of capacity. A database cannot settle those experimental judgments from field names alone.

Here, GIGI performs **persistent storage, filtering, sorting, and aggregation**, with measurements and their qualifications kept together. Conventional databases can perform the same screening. This project does not evaluate geometric learning or claim superiority over another database. GIGI's geometric confidence metadata are not statistical confidence intervals and do not replace the source experiment's SE. Section 2 and the first technical drawing explain this before the paper's methods.

## Findings and expected outputs

The primary screen is strictly **R² > 0.80**, applied to displayed rounded values. Equality is excluded.

| Mg activation (M) | Formulations | Retained | Excluded numeric fits | NR | Retained capacity range (mg P/g) |
|---|---:|---:|---:|---:|---|
| 0 | 9 | 0 | 2 | 7 | Unavailable |
| 0.25 | 9 | 3 | 3 | 3 | 0.62–4.10 |
| 0.5 | 9 | 4 | 3 | 2 | 1.67–5.33 |
| 1 | 9 | 9 | 0 | 0 | 2.60–10.35 |
| **Total** | **36** | **16** | **8** | **12** | |

The leading retained point estimate is **10.35 ± 1.45 mg P/g**, R² 0.90, for PL3 / 1 M Mg / 900 degrees C, ID 24. The ± value is the **published parameter SE**, not a 95% interval or between-batch variation. The largest unscreened estimate is 134.41 ± 133.98 mg P/g with R² 0.00.

| Strict R² cutoff | Retained | Retained at 1 M | Leading ID | Leading capacity (mg P/g) |
|---|---:|---:|---:|---:|
| > 0.70 | 17 | 9 | 24 | 10.35 |
| > 0.80 | 16 | 9 | 24 | 10.35 |
| > 0.85 | 14 | 9 | 24 | 10.35 |
| > 0.90 | 12 | 7 | 10 | 8.55 |
| > 0.95 | 5 | 4 | 11 | 7.41 |

The leading recipe changes with the screen. These are descriptive shortlists, not significance rankings.

The workbook supplies **15 measured pairs per formulation**, 540 total. **171** have negative sorbed-P values, indicating net release. Counts by Mg activation are **93/135, 52/135, 26/135, and 0/135** for 0, 0.25, 0.5, and 1 M, respectively. Those denominators pool concentrations and within-condition measurements; they are not independent batches or runoff events. All signed values are preserved. No new p-values or confidence intervals are inferred from these pooled counts.

## Quick start: complete offline reproduction

### Prerequisites

- Git, unless downloading a repository ZIP.
- Python **3.10+**. GitHub Actions uses Python 3.12.
- No Python packages, API keys, database, or network after cloning are required for extraction, analysis, manuscript generation, and tests. XLSX reading uses Python's standard ZIP/XML libraries.
- A LaTeX environment is required only to rebuild the PDF.

Run from a terminal. Use `python3` instead of `python` where appropriate, or `py -3` on Windows.

```sh
git clone https://github.com/nurdymuny/gigi-biochar.git
cd gigi-biochar
python --version
python scripts/extract_table.py
python scripts/analyze.py
python scripts/import_dryad.py
python -m unittest discover -s tests -v
python scripts/build_manuscript.py
git diff --exit-code -- data/processed results/summary.json results/isotherm_summary.json paper/manuscript.tex
```

Run each command successfully before continuing. In PowerShell, inspect `$LASTEXITCODE` if a command fails; separate commands do not automatically stop execution on a native-program error. In Unix shells, the last exit code is `$?`.

Expected results:

1. Extraction reports 36 formulations and rewrites JSON and CSV from the archived table.
2. Screening prints JSON with `formulations: 36`, `numeric_fits: 24`, `passing: 16`, `poor_fit: 8`, and `nr: 12`.
3. Dryad extraction prints `observations: 540`, `formulations: 36`, `points_per_formulation: [15]`, and `negative_sorption: 171`.
4. All **14 tests** pass.
5. Manuscript generation prints `Built standalone manuscript.tex`.
6. The final Git command exits 0 with no diff. It checks deterministic text outputs, not PDF byte identity or live database execution.

The archived workbook and original Dryad README are included unchanged, so routine reproduction does **not** require downloading the archive again. Scripts resolve paths relative to their own repository location; there are no personal machine paths in the workflow.

### Optional Python environment

The core workflow needs no installed packages. `requirements.txt` supplies only optional `pypdf` for PDF inspection.

Windows, without activation or execution-policy changes:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Figures use LaTeX/PGFPlots, not matplotlib. Optional PDF-inspection package versions do not affect numerical results. Nothing needs installing to read the checked-in PDF.

## Reproduce the live GIGI checks

### 1. Obtain and build the engine

Obtain [GIGI](https://github.com/nurdymuny/gigi) separately. This analysis does not redistribute the engine or database files. Consult its build instructions and license. Building requires Rust/Cargo and a platform linker; Windows may require Visual Studio C++ build tools.

From the analysis checkout, create a sibling engine checkout:

```sh
cd ..
git clone https://github.com/nurdymuny/gigi.git
cd gigi
cargo build --release --bin gigi-stream
git rev-parse HEAD
```

The binary is normally `target/release/gigi-stream.exe` on Windows or `target/release/gigi-stream` elsewhere. Record the engine commit and binary SHA-256 for your run. A build from current upstream is a compatibility reproduction, not a claim of byte-identical reproduction of the original pre-existing executable. `results/environment.json` records the preparation binary and environment; its source revision could not be verified from that executable.

If you change engine code, stop **your own** server, rebuild, confirm the executable timestamp changed, and restart. `cargo test` alone does not rebuild/restart a live server. This project's Python tests do not claim to run the engine's full Rust test suite.

### 2. Start an isolated instance in terminal A

Return to the analysis checkout. These examples assume sibling directories named `gigi` and `gigi-biochar`; adjust navigation if you used another name.

Windows PowerShell:

```powershell
cd ..\gigi-biochar
New-Item -ItemType Directory -Force .runtime\gigi | Out-Null
$env:PORT = '3147'
$env:GIGI_DATA_DIR = (Resolve-Path .runtime\gigi).Path
& ..\gigi\target\release\gigi-stream.exe
```

macOS/Linux:

```sh
cd ../gigi-biochar
mkdir -p .runtime/gigi
PORT=3147 GIGI_DATA_DIR="$PWD/.runtime/gigi" ../gigi/target/release/gigi-stream
```

Leave this foreground process running while using terminal B. Stop it with Ctrl+C in terminal A when finished. `.runtime/` is ignored by Git. Use a fresh research directory, not a production database. If 3147 is occupied, choose an unused port and change both server and client settings rather than stopping an unrelated process.

For authenticated use, set `GIGI_API_KEY` to the same authorized private value in terminal A before startup and terminal B before analysis. The client sends `X-API-Key`, not a Bearer header. It does not automatically load `.env`. Never commit the key.

### 3. Import and verify in terminal B

Open terminal B at the analysis repository root:

```sh
python scripts/analyze.py --gigi-url http://127.0.0.1:3147
python scripts/import_dryad.py --gigi-url http://127.0.0.1:3147
```

Use `127.0.0.1` locally: on Windows, `localhost` can resolve to IPv6 first and add delays. These operations need write permission and are not intended for GIGI's public read-only instance.

| Bundle | Records | Content |
|---|---:|---|
| `biochar_capture_paper_v1` | 36 | Published fit summaries |
| `biochar_capture_paper_gate_v1` | 2 | Explicitly synthetic test records |
| `biochar_isotherms_v1` | 540 | Archived solution-concentration/sorbed-P pairs |

Absent bundles are created. Matching existing records are reused. Mismatching records cause a failure; these scripts never overwrite or delete an existing differing bundle. For an incomplete bundle left by an interrupted import, restart with a fresh isolated data directory. Do not merge private lab records into these fixed reproduction bundles.

### 4. What successful verification establishes

The screening script checks a planted answer: a capacity of 9999 with R² 0.01 must lose to a capacity of 5 with R² 0.95 after filtering. Removing the fit filter must select 9999, demonstrating that the check detects the intended mechanism. It then verifies all 36 rows, complete rankings at five thresholds, and retained counts and means for the three nonempty activation groups against an independent Python reference.

The measurement script verifies all 540 rows and every returned negative-sorption record against the independently extracted source. Text, identifiers, and nulls must match exactly; numeric fields use relative or absolute tolerance of 1e-12. Truncated reads and duplicate/excess records are not accepted as successful roundtrips.

Live receipts include UTC time, the normalized-input SHA-256, and exact endpoint paths, request bodies, HTTP statuses, and returned values. They exclude authentication headers, server address, and inventories of unrelated bundles. They demonstrate these operations, not all engine features or a performance benchmark.

Receipts are **not byte-for-byte deterministic**: time, execution metadata, and create-versus-reuse calls vary. A successful rerun replaces the receipt with your new evidence. A failed run may leave an older receipt, so require exit code 0 and inspect `checked_at_utc` before claiming success. The offline numerical outputs should remain unchanged.

## Build and edit the scientific paper

`paper/manuscript.tex` is self-contained: all plotted coordinates, technical drawings, tables, and bibliography are embedded. It requires no separate image files or BibTeX database. Open this file directly in a LaTeX editor.

`paper/manuscript_template.tex` is the prose template with `@@...@@` placeholders. **Do not compile the template directly.** For lasting edits, edit the template and run `python scripts/build_manuscript.py`. Direct edits in `manuscript.tex` remain editable, but regeneration replaces them; transfer such changes back to the template first.

If source data or analytical rules change, regenerate data, summaries, and manuscript, then review the prose and README manually. Tables and plotted coordinates are generated automatically; prose conclusions are not automatically rewritten.

From the repository root, with an installed pdfLaTeX:

```sh
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=paper paper/manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=paper paper/manuscript.tex
```

The second pass resolves references and table widths. Rerun if the log requests another pass. Output is `paper/manuscript.pdf`. Intermediate files are ignored. MiKTeX supports adding `--disable-installer` to prevent automatic package installation.

Packages: `geometry`, T1 `fontenc`, `lmodern`, `microtype`, `amsmath`, `booktabs`, `longtable`, `array`, `pgfplots` (compatibility 1.18), PGF/TikZ libraries `arrows.meta`, `patterns`, `positioning`, and `groupplots`, plus `hyperref` and `caption`. Use a distribution with these installed, or its usual package manager if one is missing.

During preparation, the built-in document editor reported **“Unable to find standard directories for platform”** without a source-line diagnostic. The source was kept open, and the user authorized an installed local compiler for PDF export. A successful local export does not repair the editor's internal compiler. For ordinary LaTeX source errors, inspect the `.tex` line named in the log instead.

PDF hashes can differ by compiler, platform, and timestamps. Reproduce the deterministic source and scientific content, then visually review all pages. Check for undefined references, clipped drawings, overlapping labels, figure axes, error bars, and the complete appendix. The technical apparatus drawing is a proposed measurement scheme, not a specification for manufacturing a treatment unit.

## Data origin and methodological decisions

Padilla JT, Watts DW, Novak JM, Cerven V, Ippolito JA, Szogi AA, Johnson MG (2023). *Magnesium activation affects the properties and phosphate sorption capacity of poultry litter biochar*. Biochar 5:64. [Article](https://doi.org/10.1007/s42773-023-00263-5), [Table 1](https://link.springer.com/article/10.1007/s42773-023-00263-5/tables/1), [Dryad data](https://doi.org/10.5061/dryad.pc866t1w7).

The published table is preserved as an attributed HTML excerpt with a checked SHA-256. Its 12 body rows expand across three temperatures into 36 formulation summaries. Each row keeps original cell text, source-table row, and URL. NR becomes JSON `null` and blank CSV numeric cells; neither means zero. The manifest's original full-page checksum is historical provenance; only the excerpt is included, so the full-page checksum cannot be verified from this checkout alone.

The unchanged Dryad files are from the **10 October 2023** archive. An initial programmatic download failed; the user subsequently supplied the public archive. Its original ZIP hash and both extracted file hashes are recorded. Only the isotherm sheet is normalized for this analysis; all other sheets remain available in the original workbook. XLSX extraction reads stored numeric cells, rejects formula cells pending explicit review, and records Excel coordinates. It does not execute workbook code or infer replicate identities from position.

Known source issues are recorded rather than silently corrected:

- The published table gives PL7 / 0.25 M / 900 degrees C as **0.62 ± 0.06**, R² 0.96; the article narrative states a 0.66 minimum. The table's 0.62 is retained. Importing observations does not by itself resolve this fit discrepancy.
- The workbook notes name `Figure 4 and Sup. Fig. S5`; the actual isotherm tab is `Figure 5 and Sup. Fig. S5` and has the expected concentration and sorption headers.
- `Figure 1 and Sup. Fig. S2` and `Proximate Analysis` contain `PL9` labels, while the paper and isotherm sheet use PL7. These other sheets are not silently relabeled or joined.
- The source uses both `> 0.80` and exclusion of `< 0.80` in different passages. No displayed value equals 0.80, so this does not alter the primary subset. All analysis thresholds here are explicitly strict.

Source batch conditions include 0.1 g biochar in 20 mL, 25–150 mg P/L initial solution, 10 mM KCl, initial pH approximately 5, and 24 hours at 21 degrees C. The fitted-capacity table lacks the affinity parameter needed to predict uptake at a target concentration. Raw observations make future reviewed refitting possible; no such model is fitted in this repository. Neither data layer measures runoff loads, field breakthrough, or long-term desorption. Small equilibrium concentrations in some points do not independently validate dilute-influent treatment performance.

## Intentionally refreshing sources

Normal reproduction uses frozen sources. To deliberately replace the Dryad files with another downloaded archive:

```sh
python scripts/import_dryad.py --archive /path/to/downloaded/archive.zip
```

That command replaces the two archived files and their manifest. Use a quoted path on Windows if it contains spaces. Review the dataset version and Git diff before accepting it. To refresh the published table from a saved Table 1 HTML page:

```sh
python scripts/archive_source.py /path/to/table-page.html
python scripts/extract_table.py
python scripts/analyze.py
python scripts/import_dryad.py
python -m unittest discover -s tests -v
python scripts/build_manuscript.py
git diff
```

The table archiver extracts the first HTML table, so manually confirm it is still Table 1. Extraction expects the original layout and known results. Investigate changed sources and failed tests rather than changing expected values merely to obtain a passing run. New observations belong in a separately versioned analysis, with documented mappings and units.

## Tests and continuous integration

The **14 tests** check source-file hashes, all-cell extraction agreement, NR missingness, strict thresholds, known screening counts, sensitivity, the planted filter mechanism, rejection of incomplete/duplicate designs and excess roundtrip rows, all 540 workbook pairs, a known negative cell, and preservation of label anomalies.

GitHub Actions runs these under Python 3.12, regenerates both data layers, both summaries, and the manuscript, and fails on unexpected diffs. It does not start GIGI or compile LaTeX. Live execution and PDF review are separate checks. There are no random samples or random seeds in this descriptive analysis.

## Troubleshooting

| Symptom | Next step |
|---|---|
| `python` not found | Try `python3` or `py -3`; confirm Python 3.10+. |
| Source checksum fails | Inspect source bytes and Git diff. Do not blindly replace the expected hash. |
| Unexpected table/workbook layout | Check the source version, sheet names, and headers; review the parser before accepting changes. |
| Formula-cell refusal in workbook | Review calculation provenance before adding cached-value support. No silent recalculation occurs. |
| Live connection refused | Confirm server, port, and `127.0.0.1` URL. |
| HTTP 401/403 | Check the authorized `GIGI_API_KEY`; a public read-only server cannot accept imports. |
| HTTP 422 naming a field requirement | Read the refusal and correct the input. It is not evidence of a crash. |
| GQL HTTP 500 with a field requirement | GIGI can return input refusals as GQL 500; read the body. These scripts use REST. |
| GQL `{"status":"ok"}` without data | It can mean nothing executed. Rows or values are needed as evidence. |
| Existing bundle differs | Use a fresh isolated data directory; the scripts intentionally protect existing data. |
| Windows build cannot replace binary | Stop your own engine instance, rebuild, and check binary timestamp. |
| `@@...@@` in LaTeX | Generate and compile `manuscript.tex`, not the template. |
| Undefined references after first pass | Compile again, then inspect the log. |
| Built-in compiler platform-directory error | The observed internal compiler could not initialize; preserve source and use a working local export environment. |
| Git diff after reproduction | Review it: live receipt changes are expected; deterministic data/summary/source changes are not expected for the same revision. |

## Repository map

| Location | Purpose |
|---|---|
| `data/source/table1.html` | Attributed published-table excerpt |
| `data/source/dryad/` | Unchanged workbook, original README, provenance |
| `data/processed/capture_records.*` | 36 formulation summaries |
| `data/processed/isotherm_records.*` | 540 source-linked measured pairs |
| `scripts/archive_source.py` | Explicit table-source refresh |
| `scripts/extract_table.py` | Table normalization |
| `scripts/analyze.py` | Fit screening and optional live GIGI verification |
| `scripts/import_dryad.py` | Workbook normalization and optional live verification |
| `scripts/build_manuscript.py` | Data + prose template -> standalone LaTeX |
| `results/` | Deterministic summaries, live receipts, preparation environment |
| `paper/` | Template, standalone source, exported PDF |
| `tests/` | Offline verification suite |
| `.github/workflows/verify.yml` | Automated regeneration and verification |

Temporary servers, snapshots, credentials, dependency environments, rendering previews, and unrelated experiments are excluded. The earlier crop-availability exploration is outside this capture-focused repository.

## Authorship, citation, and reuse

Repository maintainer: **Bee Rosa Davis**. Commits prepared here use **bee_davis@alumni.brown.edu** as author and committer, with no co-author trailers. Git authorship is distinct from a scholarly author list.

The manuscript discloses AI-assisted preparation. Its research authors, affiliations, funding, and competing-interest declarations remain for the responsible researchers to supply before journal submission. It is a discussion draft. See [CITATION.md](CITATION.md); cite the original study and Dryad data, and identify the exact repository commit for reproductions.

Published article/table material retains CC BY 4.0 attribution. Dryad data are supplied under CC0. GIGI has separate upstream licensing. No license has yet been selected for newly authored code and manuscript; a public repository alone does not grant blanket reuse rights. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
