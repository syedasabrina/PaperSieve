# PaperSieve

A two-model agentic screening pipeline that reduces a corpus of 3000+ NLP papers to a ranked, categorized reading list, with a verifiability pipeline that tests working theoretical frameworks against the filtered corpus. Built to support a PhD research project on subjectivity in NLP tasks.

---

## What it does

PaperSieve takes a folder of PDF papers and screens each one against four structured discovery criteria using a two-model Gemini setup. Each paper is scored, assigned a confidence level, and routed into a relevance bucket. All model decisions are logged with supporting quotes for reproducibility.

Pass 1 uses Gemini Flash for speed and cost efficiency. Any criterion returning low confidence automatically escalates to Gemini Pro, which re-examines the specific section of the paper where evidence was or was not found. Papers that fail due to API errors are automatically retried with exponential backoff at the end of each run.

Once papers are filtered and manually analyzed, the verifiability pipeline tests three working analytical frameworks — a definition of subjectivity, a task taxonomy, and a handling methodology taxonomy — against the full filtered corpus using structured Gemini prompts. Results are written to a four-sheet xlsx for comparison against a manually derived gold standard.

This is a **methodological support tool**, not a research contribution in itself. The pipeline surfaces candidate papers for manual analysis — it does not generate theoretical claims or define subjectivity.

---

## Pipeline architecture

### Track 2 — Screening

```
PDF papers
    │
    ▼
extractor.py     ← section-aware PDF text extraction
    │
    ▼
analyzer.py      ← Gemini Flash screening (pass 1)
    │
    ├── confidence == low? ──► Gemini Pro targeted retry (pass 2)
    │
    ▼
scorer.py        ← persist results to JSON log and rankings CSV
    │
    ▼
route_files.py   ← copy PDFs to bucket folders based on run results
```

### Track 3 — Verifiability

```
PDF papers (from any bucket folder)
    │
    ▼
extractor.py     ← reused section-aware PDF extraction
    │
    ▼
verify.py        ← three Gemini prompts per paper:
    │                 definition_vN.txt  → DefinitionResult
    │                 taxonomy_vN.txt    → TaxonomyResult
    │                 handling_vN.txt    → HandlingResult
    │               parse-failure retry (same model, once)
    ▼
verify_writer.py ← writes 4-sheet xlsx + per-paper JSON logs
```

---

## Screening criteria

Four yes/no questions applied to every paper:

| | Question |
|---|---|
| Q1 | Does the paper explicitly call an NLP task subjective or objective? |
| Q2 | Does it define or frame what subjectivity means in any way? |
| Q3 | Does it discuss annotation disagreement or inter-annotator agreement as a core methodological concern? |
| Q4 | Does it discuss how to handle subjectivity — any strategy, framework, or approach? |

Each answer includes a direct quote from the paper, the section it was found in, a confidence level (high / medium / low), and a justification. A yes answer without a supporting quote is not permitted.

---

## Routing logic

| Score | Confidence | Bucket |
|---|---|---|
| 4 | No low confidence | `to_read` |
| 4 | Any low | `maybe_recheck` |
| 3 | No low confidence | `maybe_recheck` |
| 1–2 | Any | `maybe_borderline` |
| 0 | Any low | `maybe_borderline` |
| 0 | No low confidence | `filtered_out` |

Papers with any low-confidence criterion are flagged `manual_review=true` regardless of bucket.

---

## Verifiability prompts

Three structured prompts are run per paper against the working analytical frameworks:

| Prompt | Tests | Output fields |
|---|---|---|
| `definition_vN.txt` | Whether the paper's definition of subjectivity matches the 3-Pillar Framework | `subjectivity_def_type`, `pillar_match`, `matches_working_definition`, `definition_gap_identified` |
| `taxonomy_vN.txt` | Whether the paper's task classification aligns with the Working Task Taxonomy (Category A/B/C) | `author_task_label`, `taxonomy_category_match`, `reasoning_codes` (R1–R7), `reasoning_gap` |
| `handling_vN.txt` | Whether the paper's methodology matches the Working Handling Taxonomy (A1–A5, B1–B9) | `strategy_code`, `pipeline_stage`, `primary_position`, `internal_consistency` |

Prompts are versioned. After assessing results against the gold standard, prompts are updated (v1 → v2) and re-run. The iteration strategy is: `to_read` first → assess → adjust → `maybe_recheck` next → repeat.

---

## Project structure

```
PaperSieve/
├── src/
│   ├── models.py              — Pydantic models for screening pipeline
│   ├── extractor.py           — section-aware PDF extraction
│   ├── analyzer.py            — two-model Gemini calls, backoff, retry logic
│   ├── scorer.py              — JSON logging and CSV appending
│   ├── verifier_models.py     — Pydantic models for verifiability pipeline
│   ├── verify.py              — three-prompt Gemini calls, parse-retry logic
│   └── verify_writer.py       — 4-sheet xlsx writer with crash recovery
├── scripts/
│   ├── route_files.py         — copy PDFs to bucket folders from a run's CSV
│   └── validate.py            — compare pipeline results against gold labels
├── prompts/
│   ├── screening_v1.txt       — main screening prompt (Flash)
│   ├── retry_v1.txt           — targeted retry prompt (Pro)
│   ├── definition_v1.txt      — verifiability: definition prompt
│   ├── taxonomy_v1.txt        — verifiability: task taxonomy prompt
│   ├── handling_v1.txt        — verifiability: handling taxonomy prompt
│   └── criterion_questions.json
├── docs/
│   └── screening_rubric.md
├── tests/
│   ├── test_models.py
│   └── test_scorer.py
├── data/
│   ├── papers/                — input PDFs (gitignored)
│   ├── to_read/               — score 4, no low confidence
│   ├── maybe_recheck/         — score 4 with any low confidence, or score 3 with no low confidence
│   ├── maybe_borderline/      — score 1-2, or score 0 with any low confidence
│   └── filtered_out/          — score 0, no low confidence
├── results/
│   └── <run_id>/
│       ├── rankings.csv           — screening: one row per paper
│       ├── verifiability.xlsx     — verifiability: 4-sheet workbook
│       └── logs/                  — one JSON per paper for both pipelines
├── pipeline.py                — screening orchestrator with auto-retry
├── verify_pipeline.py         — verifiability orchestrator
├── main.py                    — CLI entry point (screening + verify subcommands)
├── gold_standard_verifiability.xlsx — manually derived gold standard (70 papers)
└── requirements.txt
```

---

## Usage

**Run the screening pipeline:**

```bash
python main.py run --input-dir data/papers --run-id run_001
```

Override models if needed:

```bash
python main.py run --input-dir data/papers --run-id run_001 --model gemini-2.5-flash --retry-model gemini-2.5-pro
```

If the run crashes, re-running the same command resumes from where it stopped. Papers that failed due to API errors are automatically retried at the end of the run.

**Run the verifiability pipeline:**

```bash
python main.py verify run --input-dir data/to_read/ --run-id verify_001 --model gemini-2.5-pro
```

Use `--model gemini-2.5-flash` for a faster, cheaper pass. Use `--model gemini-2.5-pro` for the assessment run you compare against the gold standard.

**Route PDFs to bucket folders after a screening run:**

```bash
python scripts/route_files.py --run-id run_001 --source-dir data/papers
```

**Validate screening results against gold labels:**

```bash
python scripts/validate.py --run-id run_001
```

---

## Output files

**Screening:**

`results/<run_id>/rankings.csv` — one row per paper with score, bucket, per-criterion labels and confidence levels, retry metadata, model version, and timestamp.

`results/<run_id>/logs/<paper_id>.json` — full evidence record for one paper including all four criterion results with quotes, sections, justifications, and pipeline metadata.

**Verifiability:**

`results/<run_id>/verifiability.xlsx` — four sheets: Definition (one row per paper), Taxonomy (one row per focal task per paper), Handling (one row per paper), Summary (one row per paper combining all three prompts).

`results/<run_id>/logs/<paper_id>.json` — per-paper model output for all three verifiability prompts.

---

## Models

| Pass | Model | Purpose |
|---|---|---|
| Screening pass 1 | `gemini-2.5-flash` | Full paper screening, all four criteria |
| Screening pass 2 (retry) | `gemini-2.5-pro` | Targeted re-examination of low-confidence criteria |
| Verifiability | configurable via `--model` | All three prompts per paper; default `gemini-2.5-flash` |

Temperature is set to 0.0 for deterministic outputs. 503 errors are retried with exponential backoff (30s, 60s, 90s).

---

## Validation

The screening pipeline was validated against a manually labeled gold set of 36 papers before running on the full corpus. Three configurations were evaluated: Flash-only, Pro-only, and the final two-model pipeline with the current routing logic.

### Per-criterion label agreement

| Criterion | Question | Flash | Pro | Two-Model |
|---|---|---|---|---|
| Q1 | Does the paper explicitly call an NLP task subjective or objective? | 27/36 (75%) | 29/36 (80%) | 29/36 (80%) |
| Q2 | Does it define or frame what subjectivity means in any way? | 33/36 (91%) | 33/36 (91%) | 33/36 (91%) |
| Q3 | Does it discuss annotation disagreement or inter-annotator agreement? | 29/36 (80%) | 30/36 (83%) | 30/36 (83%) |
| Q4 | Does it discuss how to handle subjectivity? | 31/36 (86%) | 31/36 (86%) | 32/36 (88%) |

### Classification metrics

| Metric | Flash | Pro | Two-Model |
|---|---|---|---|
| Exact bucket match | 24/36 (66%) | 25/36 (69%) | 22/36 (61%) |
| Precision (to_read) | 0.79 | 0.85 | 1.00 |
| Recall (to_read) | 0.85 | 0.85 | 0.54 |
| False positive rate | 0.13 | 0.09 | 0.00 |
| to_read papers incorrectly filtered out | 0/36 (0%) | 0/36 (0%) | 0/36 (0%) |

The two-model pipeline achieves perfect precision — every paper placed in `to_read` is a true positive. The tradeoff is recall: five score==3 papers that were manually judged relevant are routed to `maybe_recheck` rather than `to_read`. These papers are not lost; they require manual review. The sixth false negative (`2025.emnlp-main.1261`) is a documented Q1 strictness failure. Known limitations are documented in `docs/PROJECT_SCOPE.md`.

The verifiability pipeline is validated against `gold_standard_verifiability.xlsx`, a manually derived gold standard covering 70 papers from the `to_read` bucket across all three analytical dimensions.

---

## Setup

```bash
git clone https://github.com/syedasabrina/PaperSieve.git
cd PaperSieve
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add a `.env` file at the project root:

```
GEMINI_API_KEY=your_key_here
```