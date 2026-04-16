# PaperSieve

A two-model agentic screening pipeline that reduces a corpus of 3000+ NLP papers to a ranked, categorized reading list. Built to support a PhD research project on subjectivity in NLP tasks.

---

## What it does

PaperSieve takes a folder of PDF papers and screens each one against four structured discovery criteria using a two-model Gemini setup. Each paper is scored, assigned a confidence level, and routed into a relevance bucket. All model decisions are logged with supporting quotes for reproducibility.

Pass 1 uses Gemini Flash for speed and cost efficiency. Any criterion returning low confidence automatically escalates to Gemini Pro, which re-examines the specific section of the paper where evidence was or was not found. Papers that fail due to API errors are automatically retried with exponential backoff at the end of each run.

This is a **methodological support tool**, not a research contribution in itself. The pipeline surfaces candidate papers for manual analysis — it does not generate theoretical claims or define subjectivity.

---

## Pipeline architecture

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

The two-model retry loop is what makes this an agent rather than a batch script. After the Flash pass, any criterion with low confidence triggers a second targeted Pro call on the specific section where evidence was found. Both responses are logged. Papers failing due to 503 errors are retried automatically with exponential backoff.

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
| 3–4 | All medium or high | `to_read` |
| 3–4 | Any low | `maybe_recheck` |
| 1–2 | Any | `maybe_borderline` |
| 0 | Any low | `maybe_borderline` |
| 0 | All medium or high | `filtered_out` |

Papers with any low-confidence criterion are flagged `manual_review=true` regardless of bucket.

---

## Project structure

```
PaperSieve/
├── src/
│   ├── models.py          — Pydantic data models and enums
│   ├── extractor.py       — section-aware PDF extraction
│   ├── analyzer.py        — two-model Gemini calls, backoff, retry logic
│   └── scorer.py          — JSON logging and CSV appending
├── scripts/
│   ├── route_files.py     — copy PDFs to bucket folders from a run's CSV
│   └── validate.py        — compare pipeline results against gold labels
├── prompts/
│   ├── screening_v1.txt   — main screening prompt (Flash)
│   ├── retry_v1.txt       — targeted retry prompt (Pro)
│   └── criterion_questions.json
├── docs/
│   └── screening_rubric.md
├── tests/
│   ├── test_models.py
│   └── test_scorer.py
├── data/
│   ├── papers/            — input PDFs (gitignored)
│   ├── to_read/           — high relevance
│   ├── maybe_recheck/     — high score, weak evidence
│   ├── maybe_borderline/  — low score or uncertain noes
│   └── filtered_out/      — no signal found
├── results/
│   └── <run_id>/
│       ├── rankings.csv   — one row per paper with scores and buckets
│       └── logs/          — one JSON file per paper with full evidence
├── pipeline.py            — main orchestrator with auto-retry
├── main.py                — CLI entry point
└── requirements.txt
```

---

## Usage

**Run the screening pipeline:**

```bash
python main.py --input-dir data/papers --run-id run_001
```

Override models if needed:

```bash
python main.py --input-dir data/papers --run-id run_001 --model gemini-2.5-flash --retry-model gemini-2.5-pro
```

If the run crashes, re-running the same command resumes from where it stopped. Papers that failed due to API errors are automatically retried at the end of the run.

**Route PDFs to bucket folders after a run:**

```bash
python scripts/route_files.py --run-id run_001 --source-dir data/papers
```

**Validate results against gold labels:**

```bash
python scripts/validate.py --run-id run_001
```

---

## Output files

`results/<run_id>/rankings.csv` — one row per paper with score, bucket, per-criterion labels and confidence levels, retry metadata, model version, and timestamp.

`results/<run_id>/logs/<paper_id>.json` — full evidence record for one paper including all four criterion results with quotes, sections, justifications, and pipeline metadata.

---

## Models

| Pass | Model | Purpose |
|---|---|---|
| Pass 1 | `gemini-2.5-flash` | Full paper screening, all four criteria |
| Pass 2 (retry) | `gemini-2.5-pro` | Targeted re-examination of low-confidence criteria |

Temperature is set to 0.0 for deterministic outputs. Both models are configurable via CLI args. 503 errors are retried with exponential backoff (30s, 60s, 90s).

---

## Validation

The pipeline was validated against a manually labeled gold set of 36 papers before running on the full corpus. Two model configurations were compared.

### Per-criterion label agreement

| Criterion | Question | Flash | Pro |
|---|---|---|---|
| Q1 | Does the paper explicitly call an NLP task subjective or objective? | 27/36 (75%) | 29/36 (80%) |
| Q2 | Does it define or frame what subjectivity means in any way? | 33/36 (91%) | 33/36 (91%) |
| Q3 | Does it discuss annotation disagreement or inter-annotator agreement? | 29/36 (80%) | 30/36 (83%) |
| Q4 | Does it discuss how to handle subjectivity? | 31/36 (86%) | 31/36 (86%) |

### Classification metrics

| Metric | Flash | Pro |
|---|---|---|
| Exact bucket match | 24/36 (66%) | 25/36 (69%) |
| Precision (to_read) | 0.79 | 0.85 |
| Recall (to_read) | 0.85 | 0.85 |
| False positive rate | 0.13 | 0.09 |
| to_read papers incorrectly filtered out | 0/36 (0%) | 0/36 (0%) |

Pro outperforms Flash on every metric except recall, which is equal at 0.85. The two-model design uses Flash for pass 1 and Pro for retries, capturing the cost efficiency of Flash on straightforward cases while applying Pro's stronger reasoning to ambiguous ones. Neither model ever incorrectly sent a relevant paper to `filtered_out`. Known limitations are documented in `PROJECT_SCOPE.md`.

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