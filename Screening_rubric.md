# Screening Rubric — Phase A Discovery Pass

## Global Rule
If the model extracts a quote but its own confidence in whether that quote
demonstrates the criterion is low, the paper is flagged for manual review
regardless of score. This applies to all four criteria.

---

## Screening Questions

### Q1: Does the paper explicitly call an NLP task subjective or objective?

**Example:**
> In practice, this tendency becomes especially evident in subjective annotation
> tasks, where low inter-annotator agreement...

- **Yes if:** The paper explicitly names an NLP task AND makes a claim about its
  subjectivity, for whatever reason the authors give.
- **No if:** The paper either doesn't discuss a specific NLP task, OR discusses
  one but never frames it in subjectivity terms at all.
- **Low confidence if:** Subjectivity is mentioned once in passing with no
  justification or development.
- **High confidence yes if:** The paper names a task and gives a reason — any
  reason — for why it is subjective.
- **Evidence quote must show:** The task name and the subjectivity claim in close
  proximity. One or two sentences is enough.

---

### Q2: Does it define or frame what subjectivity means in any way?

**Example:**
> By "complex subjective", we refer to problems where multiple (subjective)
> interpretations can be reasonable, and there is often no single "correct"
> answer.

- **Yes if:** The paper offers any characterization of what subjectivity means —
  a definition, a description, a contrast with objectivity, or a framing of what
  makes something subjective. The definition doesn't need to be correct or
  complete.
- **No if:** Subjectivity is never mentioned, or mentioned only as a label with
  zero elaboration.
- **Low confidence if:** The word "subjective" or "subjectivity" appears but no
  explanation of what it means is given — just assertion.
- **High confidence yes if:** The paper gives linguistic framing — says why
  something is subjective, or what subjectivity consists of in their context.
- **Evidence quote must show:** The actual framing or definition language, not
  just the word "subjective" appearing.

---

### Q3: Does it discuss annotation disagreement or inter-annotator agreement?

**Example:**
> To evaluate annotation quality, we measured inter-annotator agreement using
> Cohen's kappa coefficient (Cohen, 1960). The resulting kappa score was 0.92,
> indicating almost perfect agreement and demonstrating the reliability of the
> annotated dataset.

- **Yes if:** The paper discusses annotation disagreement or inter-annotator
  reliability as a meaningful part of its methodology or findings — not merely
  mentions that annotation occurred.
- **No if:** No mention of annotation, annotators, agreement, disagreement, or
  IAA metrics anywhere in the paper.
- **Low confidence if:** One sentence mention with no metrics and no development,
  in the body of the paper.
- **High confidence yes if:** Developed discussion with metrics reported, or a
  conceptual argument about the role and value of annotator disagreement.
- **Evidence quote must show:** Either the metric and its value, or the
  conceptual argument about disagreement — not just the word "annotator"
  appearing once.

---

### Q4: Does it discuss how to handle subjectivity?

**Example:**
> We argue that humans are a valuable source of information in SDA and play a
> critical role in capturing subjective data's richness by (1) at the descriptive
> level, recognizing layered and nuanced meanings in the data, and (2) at the
> interpretive level, offering diverse interpretations shaped by their
> positionalities.

- **Yes if:** The paper describes any method or approach for dealing with
  subjectivity in their task, whatever form that takes.
- **No if:** Subjectivity is mentioned but no handling strategy is described or
  implied.
- **Low confidence if:** A handling approach is referenced but not explained or
  justified.
- **High confidence yes if:** The paper explains what they did AND why — the
  reasoning behind the handling choice is made explicit.
- **Evidence quote must show:** The actual handling strategy in the authors' own
  terms, not just acknowledgment that subjectivity exists.