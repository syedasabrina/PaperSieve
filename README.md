# PaperSieve

An LLM-assisted literature screening pipeline that reduces a corpus of 3000+ NLP papers to a ranked, categorized reading list. Built to support a PhD research project on subjectivity in NLP tasks.

---

## What it does

PaperSieve takes a folder of PDF papers and screens each one against four structured discovery criteria using the Gemini API. Each paper is scored, assigned a confidence level, and routed into a relevance bucket. All model decisions are logged with supporting quotes for reproducibility.

This is a **methodological support tool**, not a research contribution in itself. The pipeline surfaces candidate papers for manual analysis — it does not generate theoretical claims or define subjectivity.

---

## Pipeline architecture

```
PDF papers
    │
    ▼
extractor.py        ← section-aware PDF text extraction
    │
    ▼
analyzer.py         ← Gemini API screening (pass 1)
    │
    ├── confidence == low? ──► retry with targeted section (pass 2, Gemini Pro)
    │
    ▼
scorer.py           ← persist results to JSON log and rankings CSV
    │
    ▼
route_files.py      ← copy PDFs to bucket folders based on run results
```

The retry loop is what makes this an agent rather than a simple batch script. After the first Gemini pass, any criterion with low confidence triggers a second targeted call on the specific section where evidence was (or was not) found. Both responses are logged.

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
│   ├── models.py         — Pydantic data models and enums
│   ├── extractor.py      — section-aware PDF extraction
│   ├── analyzer.py       — Gemini API calls, retry logic, paper analysis
│   └── scorer.py         — JSON logging and CSV appending
├── scripts/
│   └── route_files.py    — copy PDFs to bucket folders from a run's CSV
├── prompts/
│   ├── screening_v1.txt  — main screening prompt
│   ├── retry_v1.txt      — targeted retry prompt for low-confidence criteria
│   └── criterion_questions.json
├── docs/
│   └── screening_rubric.md
├── tests/
│   ├── test_models.py
│   └── test_scorer.py
├── data/
│   ├── papers/           — input PDFs (gitignored)
│   ├── to_read/          — high relevance
│   ├── maybe_recheck/    — high score, weak evidence
│   ├── maybe_borderline/ — low score or uncertain noes
│   └── filtered_out/     — no signal found
├── results/
│   └── <run_id>/
│       ├── rankings.csv  — one row per paper with scores and buckets
│       └── logs/         — one JSON file per paper with full evidence
├── pipeline.py           — main orchestrator
└── requirements.txt
```

---

## Usage

**Run the screening pipeline:**

```bash
python pipeline.py --input-dir data/papers --run-id run_001
```

If the run crashes, re-running the same command resumes from where it stopped — already processed papers are skipped automatically.

**Route PDFs to bucket folders after a run:**

```bash
python scripts/route_files.py --run-id run_001
```

**Re-screen a maybe folder in a new run:**

```bash
python pipeline.py --input-dir data/maybe_recheck --run-id run_002
```

---

## Output files

**`results/<run_id>/rankings.csv`** — one row per paper with score, bucket, per-criterion labels and confidence levels, retry metadata, model version, and timestamp.

**`results/<run_id>/logs/<paper_id>.json`** — full evidence record for one paper including all four criterion results with quotes, sections, justifications, and pipeline metadata.

---

## Models

| Pass | Model | Purpose |
|---|---|---|
| Pass 1 | `gemini-2.5-flash` | Full paper screening, all four criteria |
| Pass 2 (retry) | `gemini-2.5-pro` | Targeted re-examination of low-confidence criteria |

Temperature is set to 0.0 for deterministic outputs across both passes.

---

## Validation

The pipeline was validated against a manually labeled gold set of 36 papers before running on the full corpus. Agreement was measured per criterion and per bucket. Known limitations are documented in the accompanying position paper.

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

---

