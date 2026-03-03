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

**Example:**
> To evaluate annotation quality, we measured inter-annotator agreement using
> Cohen's kappa coefficient (Cohen, 1960). The resulting kappa score was 0.92,
> indicating almost perfect agreement and demonstrating the reliability of the
> annotated dataset.

- **Yes if:** At least one of the following is true:
  - Reliability metrics are reported (Cohen's kappa, Krippendorff's alpha,
    Fleiss' kappa, etc.),
  - Annotation disagreement, label variance, or label conflict is discussed,
  - Adjudication or reconciliation is described as a methodological concern.
- **No if:** No annotation, agreement, or disagreement signal anywhere in the
  paper, OR the paper only says annotation happened without any disagreement or
  reliability analysis.
- **Low confidence if:** One-line mention with little substance.
- **Medium confidence if:** Disagreement is clearly mentioned but without deep
  detail or metrics.
- **High confidence if:** Metric and value are reported, OR there is substantial
  conceptual treatment of disagreement's role.
- **Evidence quote must show:** The metric and its value, OR a clear conceptual
  discussion of disagreement's role — not just the word "annotator" appearing
  once.

---

### Q4: Does it discuss how to handle subjectivity?

**Example:**
> We argue that humans are a valuable source of information in SDA and play a
> critical role in capturing subjective data's richness by (1) at the descriptive
> level, recognizing layered and nuanced meanings in the data, and (2) at the
> interpretive level, offering diverse interpretations shaped by their
> positionalities.

- **Yes if:** The paper describes any explicit methodological action taken
  because subjectivity or perspective disagreement is expected or observed. The
  action can be established, hybrid, or entirely novel.
- **No if:** The paper only acknowledges that subjectivity exists but does not
  describe a concrete response in data, modeling, training, inference, or
  evaluation.
- **Low confidence if:** A handling approach is implied but not clearly
  described, or no evidence quote links the approach to subjectivity.
- **High confidence if:** The paper clearly states what was changed
  methodologically and why that change addresses subjectivity or disagreement.
- **Evidence quote must show:** A direct link between (a) a subjectivity-related
  challenge and (b) a concrete methodological response.
- **Optional examples (non-exhaustive):** aggregation or adjudication, soft or
  distributional labels, disagreement-aware modeling, annotator-perspective
  modeling, evaluation redesign, uncertainty-aware decoding, calibration,
  post-hoc analysis, or any novel method introduced by the authors.

---

## Output Fields Per Paper

| Field                 | Type                          |
|-----------------------|-------------------------------|
| q1_label              | yes / no                      |
| q1_quote              | string                        |
| q1_section            | string                        |
| q1_confidence         | high / medium / low           |
| q2_label              | yes / no                      |
| q2_quote              | string                        |
| q2_section            | string                        |
| q2_confidence         | high / medium / low           |
| q3_label              | yes / no                      |
| q3_quote              | string                        |
| q3_section            | string                        |
| q3_confidence         | high / medium / low           |
| q4_label              | yes / no                      |
| q4_quote              | string                        |
| q4_section            | string                        |
| q4_confidence         | high / medium / low           |
| score                 | 0–4                           |
| manual_review         | bool                          |
| manual_review_reason  | string                        |
| bucket                | to_read / maybe / filtered_out|