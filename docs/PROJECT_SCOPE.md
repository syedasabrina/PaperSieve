# Project Scope

## Project Title (Loosely)
PaperSieve: An LLM-Assisted Literature Screening Pipeline for Subjectivity in NLP Tasks

## One-Line Summary
An automated pipeline that screens and ranks NLP papers by their relevance 
to subjectivity-related discourse, producing a curated reading list for 
manual theoretical analysis.

## Track 1 — Research Contribution (Human-Led)
**Goal:** Define a framework for subjectivity in NLP tasks based on 
how researchers use the concept in published literature.

**What I do manually:**
- Read filtered candidate papers
- Identify recurring framings of subjectivity inductively
- Build an analytic codebook (Phase B) from findings
- Define which NLP tasks are subjective and why
- Argue when subjectivity framing is misused or overclaimed
- Analyze how papers treat subjectivity methodologically 

**Output:** (Hopefully) A position paper submitted to an NLP venue (ACL/EMNLP/NAACL)

## Track 2 — Paper Filtering using Agentic Pipeline
**Goal:** Reduce 3000+ papers to a ranked, categorized candidate set 
for manual review.

**What the agent does:**
- Extracts text from PDFs (abstract, introduction, conclusion)
- Screens each paper against four structured discovery criteria
- Scores, tags, and routes papers into relevance buckets
- Extracts subjectivity-related passages for exploratory reading
- Logs all model decisions with evidence quotes for reproducibility

**Input:** Folder of PDFs (`data/papers/`)

**Outputs:**
- `results/rankings.csv` — full ranked list with scores and tags
- `results/passages.csv` — extracted subjectivity-related sentences
- `results/logs/<paper_id>.json` — per-paper model evidence logs
- `data/to_read/` — PDFs scoring 3-4 (high relevance)
- `data/maybe_recheck/` — PDFs scoring 3-4 with low confidence evidence
- `data/maybe_borderline/` — PDFs scoring 1-2 or uncertain noes
- `data/filtered_out/` — PDFs scoring 0 (not relevant)

## Explicit Non-Goals
- The agent does NOT generate theoretical claims
- The agent does NOT define subjectivity
- The agent does NOT decide which tasks are subjective
- The pipeline is a methodological support tool, not the paper's primary
    scholarly contribution
- The paper is not about LLM-assisted screening

## Screening Criteria (Phase A — Discovery)
Four broad yes/no questions applied to every paper:

1. Does the paper explicitly call an NLP task subjective or objective?
2. Does it define or frame what subjectivity means in any way?
3. Does it discuss annotation disagreement or inter-annotator agreement?
4. Does it discuss how to handle subjectivity?

These are discovery criteria only. They do not constitute 
the final theoretical framework.


## Scoring and Routing Rules
- Score = number of "yes" answers (0–4)
- Score 3–4, all confidence medium or high → `data/to_read/`
- Score 3–4, any confidence low → `data/maybe_recheck/`
- Score 1–2, any confidence → `data/maybe_borderline/`
- Score 0, any confidence low → `data/maybe_borderline/`
- Score 0, all confidence medium or high → `data/filtered_out/`
- If confidence = low → `manual_review` flag added

## Inclusion and Exclusion Rules

**Include** if subjectivity is central to at least one of:
- How the task is defined or framed
- How the data or labels were created
- How the model output is evaluated
- How disagreement is handled methodologically

**Exclude** if:
- "Subjective" appears only casually 
  (e.g., "we subjectively observe that...")
- No methodological discussion of subjectivity is present
- Paper only cites subjectivity in passing without elaboration

**Manual review routing:**
If `manual_review=true` (triggered by low confidence), paper is routed 
to `maybe_recheck` or `maybe_borderline` depending on score, until manually checked.


## What This Project Is NOT Claiming
- That the pipeline is exhaustive or perfectly accurate
- That Gemini's judgments replace human scholarly judgment
- That the framework emerges from the agent rather than from 
  human analysis of the filtered literature

## Validation Plan
- Manually label 30–50 papers before full run (gold set)
- Report agreement rate per criterion after pilot run
- All model logs archived for reproducibility audit

## Confidence Criteria (Operational Definitions)

| Level  | Criteria |
|--------|----------|
| High   | Direct quote present + explicit claim about subjectivity/task |
| Medium | Indirect reference, paraphrase, or partial evidence only |
| Low    | Inferred from vague language, no direct supporting quote |

If confidence = low, `ambiguity` flag is also set to true automatically.

## Corpus
- Source: ACL Anthology
- Primary keyword: subjectiv*
- Secondary keywords: disagreement, annotator variation, 
  inter-annotator agreement, perspectiv*, crowd truth, 
  multiple valid labels, annotation variability
- Estimated size: 3000+ papers


## Validation Results — Phase A Pilot Run

The pipeline was validated against a manually labeled gold set of 36 papers before running on the full corpus. Each paper was independently labeled by the researcher across all four screening criteria and assigned a final bucket. Two model configurations were tested: `gemini-2.5-flash` and `gemini-2.5-pro`.

### Gold Set Composition

| Bucket | Count |
|---|---|
| to_read | 13 |
| maybe_recheck | 3 |
| maybe_borderline | 2 |
| filtered_out | 18 |
| **Total** | **36** |

### Per-Criterion Label Agreement

| Criterion | Question | Flash | Pro |
|---|---|---|---|
| Q1 | Does the paper explicitly call an NLP task subjective or objective? | 27/36 (75%) | 29/36 (80%) |
| Q2 | Does it define or frame what subjectivity means in any way? | 33/36 (91%) | 33/36 (91%) |
| Q3 | Does it discuss annotation disagreement or inter-annotator agreement? | 29/36 (80%) | 30/36 (83%) |
| Q4 | Does it discuss how to handle subjectivity? | 31/36 (86%) | 31/36 (86%) |

### Bucket and Classification Metrics

| Metric | Flash | Pro |
|---|---|---|
| Exact bucket match | 24/36 (66%) | 25/36 (69%) |
| Precision (to_read) | 0.79 | 0.85 |
| Recall (to_read) | 0.85 | 0.85 |
| False positive rate | 0.13 | 0.09 |
| to_read papers incorrectly filtered out | 0/36 (0%) | 0/36 (0%) |

### Model Decision

`gemini-2.5-pro` was selected for the full corpus run. Pro outperformed Flash on every metric except recall, which remained equal at 0.85. Precision improved from 0.79 to 0.85 and false positive rate dropped from 0.13 to 0.09, meaning fewer irrelevant papers will be incorrectly routed to `to_read`. Both models achieved zero unsafe errors — no relevant paper was sent to `filtered_out` in either configuration.

The two remaining false negatives (`W06-0303` and `2025.emnlp-main.1261`) are known edge cases where Q1 strictness causes the pipeline to miss papers that discuss subjective content without explicitly labeling the task as subjective. These are documented as a known limitation of the Q1 criterion rather than a prompt failure.

### Known Limitations

- The pipeline occasionally counts claims attributed to cited works as the authors' own claims, inflating Q1 and Q2 yes rates.
- General annotation protocols (e.g., multi-phase labeling for consistency) are sometimes counted as Q3 yes answers despite not constituting methodological intervention on disagreement.
- Appendix-only evidence was occasionally assigned high confidence despite the rubric requiring low confidence for appendix sources, causing some irrelevant papers to score highly.
- Non-determinism in Gemini outputs means identical papers may receive different labels across runs. Temperature is set to 0.0 to minimize this, but some variance remains.
- The gold set of 36 papers is sufficient for pilot validation but not for statistically robust agreement reporting. A larger gold set is recommended before drawing strong conclusions about pipeline accuracy.