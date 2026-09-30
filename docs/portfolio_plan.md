# Engineering AI Evaluator — Portfolio Plan

## 1. Project Positioning

Engineering AI Evaluator is a Python and Streamlit application for reviewing student- or AI-generated engineering solutions. It combines engineering-domain knowledge with structured LLM evaluation, deterministic numerical and unit checks, controlled benchmarking, and practical software-engineering safeguards. The project demonstrates how qualitative AI reasoning and auditable Python verification can work together without treating the LLM as an authoritative engineering oracle.

The strongest portfolio positioning is the combination of:

- Engineering domain knowledge across five disciplines
- Python application development
- Structured LLM API integration
- Deterministic numerical and unit verification
- AI evaluation and controlled benchmark design
- Reliability testing, error handling, and experiment documentation

Benchmark error-detection measurements must always be described as results from controlled cases, not as general engineering accuracy.

## 2. Architecture Diagram Plan

### Diagram A — Product Architecture

Purpose: explain what happens when a user evaluates a solution.

Suggested flow:

```text
Engineering Question + Candidate Solution
                    |
                    v
            Evaluation Pipeline
             /               \
            v                 v
Structured LLM Reasoning   Deterministic Python Verification
            \                 /
             v               v
          Structured Evaluation Result
```

The structured result should show:

- Rubric feedback across five dimensions
- Engineering errors and why they matter
- Extracted numerical answer where applicable
- Numerical and unit verification when the user supplies a trusted reference
- Corrected or improved solution
- Overall summary

The diagram must show that deterministic verification is conditional on trusted reference data and that an LLM-generated answer is never treated as trusted ground truth.

### Diagram B — Evaluation and Benchmark Architecture

Purpose: explain how the evaluator itself is tested.

Suggested flow:

```text
Controlled Benchmark Dataset
            |
            v
     Benchmark Runner
            |
            v
        Evaluator
            |
            v
          Results
            |
            v
          Metrics
```

The metrics branch should identify:

- Completion and provider reliability
- Error detection
- Root-category agreement
- False-positive behavior on correct solutions

Use separate colors or labeled containers for Product Operation and Internal Validation. Benchmark reference solutions, expected categories, and correctness labels remain hidden from the LLM request.

## 3. Screenshot Plan

### Screenshot 1 — Application Landing and Input Workspace

**Visible:** product header, engineering-domain selector, Engineering Problem panel, Candidate Solution panel, optional Trusted Reference section, and Run Evaluation action.

**Example:** begin entering the dynamic-pressure problem with `rho = 1.225 kg/m^3` and `V = 50 m/s`, but do not show results yet.

**Why it matters:** establishes that the product accepts arbitrary user questions and candidate solutions rather than operating only on benchmark cases.

### Screenshot 2 — Incorrect Engineering Solution Evaluation

**Visible:** the complete dynamic-pressure question, the candidate's incorrect use of `q = rho*V^2`, the stated result `3062.5 Pa`, and the top of the evaluation result.

**Example:** Fluid Mechanics dynamic pressure.

**Why it matters:** provides an immediately understandable engineering mistake and demonstrates a realistic, plausible-looking candidate answer.

### Screenshot 3 — Rubric and Identified Engineering Errors

**Visible:** Overall Assessment, Identified Issues, the Engineering Method category, explanation of the missing `1/2` factor, and at least part of the five-dimension rubric.

**Example:** the same dynamic-pressure case.

**Why it matters:** demonstrates that the evaluator explains the root engineering cause rather than reporting only a pass/fail result.

### Screenshot 4 — Deterministic Numerical and Unit Verification

**Visible:** trusted value `1531.25`, candidate value `3062.5`, absolute error, percentage error, current tolerance, fail result, and matching `Pa` units.

**Example:** the same dynamic-pressure case with trusted expected value `1531.25` and unit `Pa`.

**Why it matters:** visually separates numerical correctness from unit correctness and distinguishes Python verification from LLM judgment.

### Screenshot 5 — Benchmark and Evaluation Evidence

**Visible:** a concise benchmark summary artifact, the 30-case composition, five-domain coverage, metric definitions, and evidence that correct and intentionally incorrect cases are both represented.

**Example:** use finalized Phase 17/18 comparison artifacts once available. Until then, label this screenshot as pending and do not publish preliminary values as final results.

**Why it matters:** shows that the evaluator is tested systematically rather than demonstrated with only one favorable example.

Screenshots should be captured from the real application and stored results. Do not fabricate interface states, outputs, or metrics.

## 4. Demo Scenario

Use one continuous 60–90 second Fluid Mechanics example.

### Inputs

Question:

```text
Air has density rho = 1.225 kg/m^3 and flows at V = 50 m/s.
Calculate the dynamic pressure.
```

Candidate solution:

```text
q = rho*V^2
q = 1.225*50^2
q = 3062.5 Pa
```

Trusted reference:

```text
Expected value: 1531.25
Expected unit: Pa
```

### Demo sequence

1. Show the question and candidate answer in the two engineering panels.
2. Select Fluid Mechanics and open the optional trusted-reference section.
3. Enter `1531.25` and `Pa`, then run the evaluation.
4. Show that the evaluator identifies the missing `1/2` in `q = 0.5*rho*V^2` as a governing-formula or Engineering Method error.
5. Show the deterministic comparison between `3062.5 Pa` and `1531.25 Pa`.
6. Point out that the numerical result fails while the unit still matches.
7. Show the corrected solution ending in `1531.25 Pa`.
8. Close with one sentence explaining that a 30-case controlled benchmark measures evaluator behavior across five engineering domains.

Keep the narration focused on the separation between engineering reasoning and deterministic verification.

## 5. GitHub README Final Structure

Recommended order:

1. **Overview** — one-paragraph project description and positioning
2. **Problem** — why convincing engineering solutions may still be wrong
3. **Key Capabilities** — implemented MVP behavior only
4. **Architecture** — Product Architecture diagram and hybrid responsibility split
5. **Evaluation Rubric** — five dimensions and four statuses
6. **Example** — dynamic-pressure walkthrough
7. **Benchmark Methodology** — controlled cases, hidden ground truth, and metric definitions
8. **Benchmark Results** — mark final Phase 17/18 comparison results as pending until validation is complete
9. **Testing** — offline test coverage and distinction from engineering accuracy
10. **Tech Stack** — Python, Streamlit, OpenAI-compatible client, OpenRouter, pytest, JSON
11. **Installation** — environment creation, dependencies, and secure local configuration
12. **Usage** — running the Streamlit app, tests, and benchmark tools
13. **Limitations** — probabilistic evaluation, provider dependency, unit limitations, and benchmark scope
14. **Future Work** — evidence-backed improvements only
15. **Project Learnings** — engineering/AI boundary design, evaluation methodology, and reliability lessons
16. **Author** — Samarth Ghorpade, B.Tech Aerospace Engineering

The README should keep controlled benchmark results separate from claims about general evaluator accuracy.

## 6. Portfolio Website Case-Study Structure

### Problem

Engineering answers can be fluent and numerically plausible while using the wrong governing relationship, assumption, sign, or unit.

### Why a Simple LLM Judge Is Insufficient

An LLM can interpret reasoning and concepts, but it remains probabilistic and should not invent or supply trusted numerical ground truth.

### Hybrid Solution

Explain the separation between structured LLM reasoning evaluation and deterministic Python checks against optional trusted references.

### Architecture

Present the product diagram first, followed by the internal benchmark diagram.

### Benchmark Methodology

Describe the 30 controlled cases, five domains, correct control cases, intentionally injected mistakes, hidden labels, and defined metrics.

### Results

Present only frozen and validated Phase 17/18 results. Include provider failures and denominators rather than showing only favorable metrics.

### Engineering Lessons

Discuss root-cause classification, governing-equation verification, the distinction between units and numerical correctness, and the need to test false positives.

### Limitations

State the small benchmark scope, LLM/provider variability, simple unit comparison, fixed MVP tolerance, and lack of independently verified corrected solutions.

### Future Improvements

Prioritize repeatability testing, benchmark growth, reliable provider handling, stronger unit support, and targeted symbolic verification.

## 7. Demo Video Plan

Suggested 60–90 second structure:

- **0–10 seconds:** title, problem statement, and one-sentence product purpose
- **10–25 seconds:** enter the dynamic-pressure question and incorrect candidate solution
- **25–35 seconds:** add the optional trusted value and unit, then run evaluation
- **35–55 seconds:** show the identified Engineering Method error and rubric feedback
- **55–70 seconds:** show deterministic numerical failure and unit match
- **70–80 seconds:** show the corrected solution
- **80–90 seconds:** mention the 30-case benchmark, five-domain coverage, and that final comparative results are pending validation

Use readable cursor movement, limited zooming, and concise captions. Record the real application; do not simulate results.

## 8. Resume Bullet Placeholders

- Built a Python and Streamlit evaluator for student- and AI-generated engineering solutions across five domains, using a structured five-dimension rubric and controlled LLM outputs.
- Implemented hybrid evaluation that combines LLM-based engineering reasoning with deterministic numerical-tolerance and normalized unit checks against optional trusted references.
- Designed a 30-case controlled engineering benchmark and offline test suite to measure completion reliability, error detection, root-category agreement, and false-positive behavior without treating benchmark results as general accuracy.

Final performance percentages should be added only after Phase 17/18 validation and repeatability review are complete.

## 9. Remaining Portfolio Checklist

- Complete the Phase-17 candidate run after provider quota is available.
- Freeze candidate results and metrics without overwriting the baseline artifacts.
- Complete the baseline-versus-candidate comparison.
- Perform the planned repeatability experiment or clearly label single-run results as preliminary.
- Decide whether to retain, revise, or reject the candidate prompt.
- Update the README with final validated Benchmark v2 results and explicit denominators.
- Produce the two final architecture diagrams.
- Capture the five real screenshots with consistent dimensions and readable text.
- Record and edit the 60–90 second demonstration video.
- Add accessibility text for diagrams and screenshots.
- Verify deployment under a supported Python version with pinned runtime dependencies.
- Configure deployment secrets outside the repository and confirm no credentials are tracked.
- Confirm provider quota/model availability is appropriate for a public demo.
- Run the complete offline test suite on the final presentation revision.
- Review all public claims for accuracy and remove outdated preliminary metrics.
- Ensure the repository has a clean, understandable commit history and no temporary or sensitive files before publication.
