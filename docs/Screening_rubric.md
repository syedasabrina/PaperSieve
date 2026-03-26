# Screening Rubric — Phase A Discovery Pass

## Global Decision Rules (apply to all four criteria)
- A criterion can be marked yes only if there is a supporting quote.
- If quote support is weak or indirect, set confidence=low and manual_review=true.
- If no quote is found for a claimed yes, set provisional no + manual_review=true.
- If quote and label conflict, keep label + set manual_review=true + add brief note.
- Score = number of yes answers (0–4). manual_review overrides automatic trust.

---

## Evidence Policy (shared across all criteria)
- Preferred sections: abstract, introduction, conclusion.
- Allowed fallback: methods, results, appendix if explicit signal exists.
- Quote length target: 1–2 sentences (max 3).
- Quote must be from the paper text — not a model paraphrase.

---

## Borderline Handling Rules
- If only appendix or table contains evidence → allow label, but default to low
  confidence unless unambiguous.
- If multiple criteria are low-confidence → keep score but enforce
  manual_review=true.
- If paper has high score but all evidence is weak → route to maybe pending
  manual review.

---

## Screening Questions

### Q1: Does the paper explicitly call an NLP task subjective or objective?

**Focus:** Linking a specific task name to a subjectivity label. The word
"subjective," "objectivity," or a direct equivalent must appear in connection
with the task.

**Example:**
> In practice, this tendency becomes especially evident in subjective annotation
> tasks, where low inter-annotator agreement...

- **Yes if:** A specific NLP task is named (e.g., hate speech detection,
  sentiment analysis, summarization evaluation), AND the paper makes an explicit
  subjectivity or objectivity claim about that task.
- **No if:** No task is named, OR a task is named but no subjectivity or
  objectivity framing is made.
- **Low confidence if:** Passing mention of "subjective" with no development or
  justification.
- **Medium confidence if:** Task and explicit claim are present, but reasoning
  is unclear.
- **High confidence if:** Task + explicit claim + reason or justification are
  all present.
- **Evidence quote must show:** Task name and subjectivity or objectivity claim
  in the same or adjacent sentences.

---

### Q2: Does it define or frame what subjectivity means in any way?

**Focus:** The "What" and "Why" of subjectivity — definitions, contrasts, or
characterizations. The label used may be synonymous with subjective (e.g.,
perspective-dependent, opinion-based).

**Example:**
> By "complex subjective", we refer to problems where multiple (subjective)
> interpretations can be reasonable, and there is often no single "correct"
> answer.

- **Yes if:** The paper provides any conceptual framing of subjectivity — a
  definition, a contrast with objectivity, an explanation of why multiple
  interpretations are valid, or any characterization of what makes something
  subjective. The definition does not need to be correct or complete.
- **No if:** "Subjective" or "subjectivity" appears only as a label with no
  explanation.
- **Low confidence if:** Assertion only — the word appears but no explanatory
  language surrounds it.
- **Medium confidence if:** Partial or implicit framing is present.
- **High confidence if:** Explicit framing language is used ("we define…",
  "subjectivity means…", "we use subjectivity to refer to…").
- **Evidence quote must show:** Actual definitional or framing text — not just
  the keyword appearing.

---

### Q3: Does it discuss annotation disagreement or inter-annotator agreement?

**Focus:** Technical or procedural intervention. The authors are not just
measuring agreement — they are doing something with it as a core part of
methodology or experiments.

**Example:**
> To evaluate annotation quality, we measured inter-annotator agreement using
> Cohen's kappa coefficient (Cohen, 1960). The resulting kappa score was 0.92,
> indicating almost perfect agreement and demonstrating the reliability of the
> annotated dataset.

- **Yes if:** The paper introduces, develops, or applies a specific method,
  model, or pipeline designed to manage, reconcile, or utilize annotator
  disagreement as a core part of its methodology or experiments.
- **No if:** Annotator agreement or disagreement is never mentioned, OR it is
  only mentioned in the introduction or literature review as a general problem
  without the authors proposing a specific fix.
- **Low confidence if:** The paper mentions using a common method (e.g., "we
  used MACE to handle labels") but provides no detail, discussion, or analysis
  of that process.
- **Medium confidence if:** Disagreement is clearly mentioned and engaged with,
  but the methodological response lacks detail.
- **High confidence if:** The authors describe a novel or adapted system or
  heuristic and report results based on it.
- **Evidence quote must show:** The technical description of the method or the
  procedural step taken to address the agreement or disagreement issue.

---

### Q4: Does it discuss how to handle subjectivity?

**Focus:** Strategic or conceptual "how-to." Covers both building systems and
high-level arguments. This includes position papers and theoretical
recommendations.

**Example:**
> We argue that humans are a valuable source of information in SDA and play a
> critical role in capturing subjective data's richness by (1) at the descriptive
> level, recognizing layered and nuanced meanings in the data, and (2) at the
> interpretive level, offering diverse interpretations shaped by their
> positionalities.

- **Yes if:** The paper describes any strategy, framework, or philosophical
  approach for dealing with subjectivity. This can be a technical system
  (methodology) OR a theoretical recommendation (position paper).
- **No if:** Subjectivity is acknowledged as a problem but the authors offer no
  strategy, way forward, or concrete response.
- **Low confidence if:** A strategy is mentioned in a single sentence without
  explaining how it would be implemented or why it works.
- **Medium confidence if:** A handling method is stated but rationale is weak
  or underdeveloped.
- **High confidence if:** The authors develop and test a system specifically for
  subjectivity, OR make a well-reasoned theoretical argument for a handling
  approach.
- **Evidence quote must show:** The actual strategy or handling mechanism, OR
  the explicit theoretical recommendation — not just acknowledgment that
  subjectivity exists.
- **Optional examples (non-exhaustive):** aggregation or adjudication, soft or
  distributional labels, disagreement-aware modeling, annotator-perspective
  modeling, evaluation redesign, uncertainty-aware decoding, calibration,
  post-hoc analysis, or any novel method introduced by the authors.

---

## Output Fields Per Paper

| Field                 | Type                           |
|-----------------------|--------------------------------|
| q1_label              | yes / no                       |
| q1_quote              | string                         |
| q1_section            | string                         |
| q1_confidence         | high / medium / low            |
| q2_label              | yes / no                       |
| q2_quote              | string                         |
| q2_section            | string                         |
| q2_confidence         | high / medium / low            |
| q3_label              | yes / no                       |
| q3_quote              | string                         |
| q3_section            | string                         |
| q3_confidence         | high / medium / low            |
| q4_label              | yes / no                       |
| q4_quote              | string                         |
| q4_section            | string                         |
| q4_confidence         | high / medium / low            |
| score                 | 0–4                            |
| manual_review         | bool                           |
| manual_review_reason  | string                         |
| bucket                | to_read / maybe / filtered_out |