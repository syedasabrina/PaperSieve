# Project Scope

## Project Title (Loosely)
PaperSieve: A Two-Model Agentic Screening Pipeline for Subjectivity in NLP Tasks

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
- Screens each paper against four structured discovery criteria using Gemini Flash
- Escalates low-confidence results to Gemini Pro with targeted section re-examination
- Scores, tags, and routes papers into relevance buckets
- Auto-retries any papers that failed due to API errors
- Logs all model decisions with evidence quotes for reproducibility

**Input:** Folder of PDFs (`data/papers/`)

**Outputs:**
- `results/<run_id>/rankings.csv` — full ranked list with scores and tags
- `results/<run_id>/logs/<paper_id>.json` — per-paper model evidence logs
- `data/to_read/` — PDFs scoring 4 across all criteria with no low confidence
- `data/maybe_recheck/` — PDFs scoring 4 with any low confidence, or scoring 3 with no low confidence
- `data/maybe_borderline/` — PDFs scoring 1-2, or scoring 0 with any low confidence
- `data/filtered_out/` — PDFs scoring 0 with no low confidence

## Track 3 — Verifiability Pipeline
**Goal:** Verify whether the working definitions, task taxonomy, and handling 
methodology taxonomy developed from manual analysis hold up against the full 
corpus of filtered papers.

**What the pipeline does:**
- Extracts text from PDFs using the existing `extract_sections()` infrastructure
- Runs three structured Gemini prompts per paper, one for each analytical dimension:
  - **Definition prompt** — verifies whether the paper's definition of subjectivity 
    matches the 3-Pillar Working Definition Framework (Expression, Interpretive, Methodological)
  - **Taxonomy prompt** — verifies whether the paper's focal task classification 
    (Subjective / Objective / Mixed) aligns with the Working Task Taxonomy (Category A/B/C) 
    and maps the paper's reasoning to codes R1–R7
  - **Handling prompt** — verifies whether the paper's methodology for handling 
    annotation disagreement and subjectivity matches the Working Handling Taxonomy (A1–A5, B1–B9)
- Logs one JSON file per paper with all three prompt outputs
- Writes results to a single `.xlsx` file with four sheets: Definition, Taxonomy, 
  Handling, and Summary (one row per paper across all three prompts)

**Input:** Any bucket folder of PDFs (starting with `data/to_read/`)

**Outputs:**
- `results/<run_id>/verifiability.xlsx` — 4-sheet workbook with one row per paper
- `results/<run_id>/logs/<paper_id>.json` — per-paper model output logs

**Run command:**
```bash
python main.py verify run --input-dir data/to_read/ --model gemini-2.5-pro --run-id <run_id>
```

**Iteration strategy:**
1. Run on `data/to_read/` first (highest-confidence papers)
2. Assess accuracy against gold standard (`gold_standard_verifiability.xlsx`)
3. Adjust working definition, taxonomy, and handling prompts based on gaps found
4. Increment prompt version (v1 → v2) and re-run
5. Repeat for `data/maybe_recheck/` once definitions stabilize
6. By the time `maybe_recheck` is processed, the taxonomy should be near-exhaustive

**Prompt versioning:**
Prompt files live in `prompts/` and are versioned explicitly:
- `definition_v1.txt`, `taxonomy_v1.txt`, `handling_v1.txt`
- Increment version suffix when making substantive changes after assessment

**New files added:**
- `src/verifier_models.py` — Pydantic models for all three prompt output schemas
- `src/verify.py` — Gemini call logic, prompt loading, JSON parsing, parse-retry on failure
- `src/verify_writer.py` — xlsx writer with 4-sheet output and crash recovery
- `verify_pipeline.py` — orchestrator mirroring `pipeline.py`; supports `--run-id`, `--model`, `--input-dir`
- `gold_standard_verifiability.xlsx` — manually derived gold standard from the 70 papers 
  already analyzed by hand, used to assess pipeline accuracy before full run

---

## Analytical Frameworks (Track 1 outputs, used as Track 3 inputs)

### Working Definition of Subjectivity — Version History

---

#### Version 1 (Derived from 70 manually analyzed papers)

Subjectivity is the condition in which natural language either expresses or is 
interpreted through private states — internal mental or emotional experiences 
such as opinions, evaluations, emotions, and speculations that are not open to 
objective observation or verification (Quirk et al. 1985; Wiebe 1994; Banfield 1982).

**Pillar 1 — Expression Level (Linguistic / Author-Centric)**  
Subjectivity is a property of text when the author's primary intention is to 
communicate a personal, non-objective point of view rather than report verifiable 
facts. Signals include affective vocabulary, evaluative framing, epistemic markers, 
and lexical items encoding an inner state. Subjectivity ≠ sentiment or polarity. 
Subjectivity at this level is graded, not binary.

**Pillar 2 — Interpretive Level (Social / Reader-Centric)**  
Subjectivity is a property of judgment when no single ground truth exists because 
the label assigned to a text is inherently rater-dependent. Judgments vary 
systematically across judges depending on demographics, cultural background, 
religious beliefs, lived experience, or personal biases. Includes the first-person 
vs. third-party distinction and metasubjectivity (N13-1081).

**Pillar 3 — Methodological Level (Annotation / Phenomenological)**  
Subjectivity is present when legitimate disagreement in human annotations 
constitutes meaningful signal about task ambiguity or diverse valid beliefs, 
rather than noise or annotator error. Degree of subjectivity is measurable — 
operationalized as average absolute deviation, pairwise L1 distance, annotation 
entropy, or inverse output similarity across annotators. Disagreement alone does 
not confirm subjectivity — its source must be identified.

---

#### Version 2 (Updated after verifiability run on 175 to_read papers)

**What changed and why:**

The three pillars are structurally unchanged. 151 of 175 papers matched the 
framework at Partial or Full level, confirming the pillars capture the dominant 
operationalizations in the literature. Version 2 adds precision at the boundaries 
of each pillar and documents recurring operationalizations in the corpus that 
the pillars do not fully cover. These are not new pillars — they are extensions, 
boundary conditions, and documented alternatives.

**Changes to Pillar 1:**

Added: Cognitive and psychological process framings — papers grounding subjectivity 
in appraisal theory (2023.findings-emnlp.962), gaze-based cognitive signals 
(2024.emnlp-main.11), or value trade-off theory — are operationalizing Pillar 1 
at a deeper mechanistic level. These count as Pillar 1 operationalizations, not 
gaps, because the underlying phenomenon (private states) is the same. The pillar 
does not need to enumerate psychological theories; it needs to acknowledge that 
the mechanism producing private states is studied independently of their 
linguistic expression.

Added boundary condition: First-person reports of an author's own emotions are 
a special case. Some papers (2024.lrec-main.25) classify these as objective on 
the grounds that the author is the most reliable source for information about 
their own internal state. This is a known theoretical position in the literature 
and should be flagged as a competing claim, not incorporated into the definition.

**Changes to Pillar 2:**

Added: The temporal and situational dimension of rater-dependence. Several papers 
note that what counts as subjective is not stable across time — terms acquire 
subjectivity through evolving social usage, annotator judgments vary with recent 
media exposure or daily mood, and public opinion shifts in response to external 
events. This is acknowledged as a modifier of Pillar 2 rather than a new dimension: 
rater-dependence is not only a function of stable demographic identity but also 
of situational and temporal context.

Added: Structured linguistic theories (Appraisal Theory, Speech Act Theory, 
modality theory) are specific theoretical frameworks that operationalize Pillar 1 
signals, not independent lenses. Their presence in a paper does not constitute 
a definition gap.

**Changes to Pillar 3:**

Added boundary condition: Computational proxies for subjectivity — corpus 
statistics (log-likelihood across corpora types), model predictive uncertainty 
or entropy, latent generative factors, tunable loss parameters — are not 
equivalent to measuring human disagreement. They may correlate with human 
perspectival differences but are not the same phenomenon. Papers that operationalize 
subjectivity exclusively through computational proxies are doing something 
categorically distinct from Pillar 3 and should be flagged as such. This is 
the most frequent gap identified in the to_read corpus (16 occurrences across 
175 papers).

**Documented alternative operationalizations (not incorporated into the pillars):**

These are recurring framings in the corpus that do not fit the three pillars 
and are documented as competing or complementary positions for the position paper 
to engage with:

1. *Behavioral / pragmatic impact framing.* Several papers (most explicitly 
   N13-1081; also ACL_D15-1238, RLHF/preference papers) define opinion or 
   subjectivity not through the author's private state or the reader's judgment, 
   but through its potential effect on a third party's behavior. N13-1081 
   explicitly rejects the Pillar 1 private-state definition and proposes this 
   as a replacement. This is the strongest theoretical alternative to the 
   three-pillar framework in the corpus and requires a direct response in the 
   position paper.

2. *Normative / prescriptive framing.* Some papers (2021.findings-emnlp.155) 
   define subjectivity as deviation from an objective standard (e.g., Wikipedia's 
   NPOV policy) rather than as an inherent property of language or judgment. 
   This conflates subjectivity with bias and treats objectivity as achievable 
   through policy, which is a prescriptive rather than descriptive position.

3. *Ambiguity conflation.* Several papers treat disagreement arising from textual 
   ambiguity or missing context as equivalent to disagreement arising from 
   perspectival differences. The three-pillar framework explicitly distinguishes 
   these (Pillar 3 boundary condition). Papers that conflate them are 
   methodologically imprecise by the framework's standard.

**What did not change:**

The core definition — subjectivity as private states not open to objective 
observation or verification — survives intact. The three-level structure 
(expression, interpretation, methodology) survives intact. The graded rather 
than binary treatment survives intact. The distinction between subjectivity and 
polarity/sentiment survives intact.

---

#### Summary: v1 → v2 delta

| Component | v1 | v2 |
|---|---|---|
| Number of pillars | 3 | 3 (unchanged) |
| Pillar 1 scope | Private states, linguistic signals | + cognitive/psychological mechanism acknowledged; + competing claim on self-reported emotion noted |
| Pillar 2 scope | Demographic rater-dependence, first-person vs third-party, metasubjectivity | + temporal and situational variability of rater-dependence added |
| Pillar 3 scope | Legitimate disagreement as signal; measurable via AAD, L1, entropy, ROUGE | + boundary condition: computational proxies ≠ human disagreement |
| Documented alternatives | None | Behavioral/pragmatic impact framing; normative/prescriptive framing; ambiguity conflation |
| Core definition | Unchanged | Unchanged |

---

### Working Task Taxonomy

**Category A — Always Subjective**  
Tasks where no single ground truth exists and judges legitimately disagree due 
to perspectival, demographic, or value-based differences. Includes: sentiment 
analysis, emotion detection, hate speech detection, toxicity detection, 
misogyny/sexism detection, sarcasm/irony detection, stance detection, argument 
quality judgment, dialogue act classification, moral value classification, 
NLG/MT quality evaluation, guilt perception prediction, cognitive appraisal 
prediction, politeness/offensiveness rating, subjectivity classification, 
belief identification.

**Category B — Always Objective**  
Tasks where a single recoverable correct answer exists under a defined schema, 
independent of annotator perspective. Includes: POS tagging, named entity 
recognition, factual information extraction.

**Category C — Mixed / Context-Dependent**  
Tasks whose subjectivity status depends on the dimension annotated, the task 
framing, or annotation methodology. Includes: summarization, machine translation, 
lexical complexity prediction, reading fluency assessment, opinion expression 
annotation, evaluative sentence identification, RST annotation, word sense 
subjectivity tagging, subjectivity detection, forum thread classification.

**Reasoning Codes (R1–R7):**
- R1 — Private State Grounding
- R2 — No Ground Truth
- R3 — Annotator Identity Dependence
- R4 — Annotation Divergence as Signal
- R5 — Metasubjectivity
- R6 — Prescriptive Suppression
- R7 — Instance-Level Variability

### Working Handling Taxonomy

**Position A — Subjectivity as Noise:**  
A1 Majority Voting / Aggregation, A2 Prescriptive Annotation Guidelines,  
A3 Filtering / Exclusion of Ambiguous Instances, A4 Label Noise Correction,  
A5 Distant Supervision / Automatic Labeling

**Position B — Subjectivity as Signal:**  
B1 Non-Aggregation (Preserving Individual Labels), B2 Soft Label Training,  
B3 Multi-Task Learning with Per-Annotator Heads, B4 Personalized Modeling,  
B5 Continuous Subjectivity Quantification, B6 Modeling Subjectivity as Auxiliary 
Prediction Target, B7 Annotator Identity / Context as Model Input,  
B8 Annotator-Centric Active Learning, B9 Preserving Disagreement in Released Datasets

---

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
- Score 4, no low confidence → `data/to_read/`
- Score 4, any low confidence → `data/maybe_recheck/`
- Score 3, no low confidence → `data/maybe_recheck/`
- Score 1–2, any confidence → `data/maybe_borderline/`
- Score 0, any low confidence → `data/maybe_borderline/`
- Score 0, no low confidence → `data/filtered_out/`
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

The pipeline was validated against a manually labeled gold set of 36 papers before running on the full corpus. Each paper was independently labeled by the researcher across all four screening criteria and assigned a final bucket. Three configurations were evaluated: Flash-only, Pro-only, and the final two-model pipeline (Flash pass 1, Pro retry on low-confidence criteria) with the current routing logic.

### Gold Set Composition

| Bucket | Count |
|---|---|
| to_read | 13 |
| maybe_recheck | 3 |
| maybe_borderline | 2 |
| filtered_out | 18 |
| **Total** | **36** |

### Per-Criterion Label Agreement

| Criterion | Question | Flash | Pro | Two-Model |
|---|---|---|---|---|
| Q1 | Does the paper explicitly call an NLP task subjective or objective? | 27/36 (75%) | 29/36 (80%) | 29/36 (80%) |
| Q2 | Does it define or frame what subjectivity means in any way? | 33/36 (91%) | 33/36 (91%) | 33/36 (91%) |
| Q3 | Does it discuss annotation disagreement or inter-annotator agreement? | 29/36 (80%) | 30/36 (83%) | 30/36 (83%) |
| Q4 | Does it discuss how to handle subjectivity? | 31/36 (86%) | 31/36 (86%) | 32/36 (88%) |

### Bucket and Classification Metrics

| Metric | Flash | Pro | Two-Model |
|---|---|---|---|
| Exact bucket match | 24/36 (66%) | 25/36 (69%) | 22/36 (61%) |
| Precision (to_read) | 0.79 | 0.85 | 1.00 |
| Recall (to_read) | 0.85 | 0.85 | 0.54 |
| False positive rate | 0.13 | 0.09 | 0.00 |
| to_read papers incorrectly filtered out | 0/36 (0%) | 0/36 (0%) | 0/36 (0%) |

### Model Decision

The final pipeline uses a two-model design: `gemini-2.5-flash` for pass 1 on all papers, escalating to `gemini-2.5-pro` for any criterion returning low confidence. The current routing logic requires score==4 with no low-confidence criteria for `to_read` placement, which yields perfect precision at the cost of recall. Five of the six false negatives are score==3 papers routed to `maybe_recheck` — they are not lost, but require manual review. The sixth (`2025.emnlp-main.1261`) is a documented false negative caused by Q1 strictness.

### Known Limitations

- The pipeline occasionally counts claims attributed to cited works as the authors' own claims, inflating Q1 and Q2 yes rates.
- General annotation protocols (e.g., multi-phase labeling for consistency) are sometimes counted as Q3 yes answers despite not constituting methodological intervention on disagreement.
- Appendix-only evidence was occasionally assigned high confidence despite the rubric requiring low confidence for appendix sources, causing some irrelevant papers to score highly.
- Non-determinism in Gemini outputs means identical papers may receive different labels across runs. Temperature is set to 0.0 to minimize this, but some variance remains.
- The gold set of 36 papers is sufficient for pilot validation but not for statistically robust agreement reporting. A larger gold set is recommended before drawing strong conclusions about pipeline accuracy.
- The stricter routing logic (score==4 only for `to_read`) trades recall for precision. Researchers prioritizing coverage over precision should also review the `maybe_recheck` bucket.