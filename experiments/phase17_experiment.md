# Phase 17 — Evidence-Driven Prompt Improvement

## Objective

Test whether the candidate evaluator prompt improves engineering error detection and root-cause classification compared with the Benchmark v2 baseline.

## Controlled Variables

- Same 30 Benchmark v2 cases
- Same model identifier
- Same provider
- Same structured output schema
- Same deterministic checks
- Same benchmark runner

## Independent Variable

The independent variable is the evaluator prompt: the baseline prompt versus the Phase-17 candidate prompt.

## Baseline Results

- Total cases: 30
- Completed: 24
- Provider or structured-output failures: 6
- Completion rate: 80.00%
- Error detection rate: 94.12% (16/17 completed incorrect cases)
- Root-category agreement: 76.47% (13/17 completed incorrect cases)
- False-positive rate: 0.00% (0/7 completed correct cases)
- Correct-case clean rate: 100.00% (7/7)

These are controlled Benchmark v2 results. The 94.12% error detection rate is **not** general evaluator accuracy and must not be presented as such.

## Candidate Prompt Changes

The Phase-17 candidate prompt adds:

- A structured engineering verification sequence
- Independent verification of the governing engineering equation or principle
- Clearer boundaries between the five Rubric v1 categories
- Classification according to the primary root cause of an error
- An explicit instruction not to return hidden reasoning traces

## First Candidate Run

The first attempted candidate run is **invalid for reasoning-performance comparison**. It produced:

- Attempted: 30
- Completed: 0
- Request failures: 30

A separate one-request diagnostic identified an HTTP 429 response caused by exhaustion of the provider's daily free-model request quota.

This was an infrastructure/provider event, not evidence that the candidate prompt performed worse than the baseline. The failed run contains no completed evaluations from which error detection, root-category agreement, or false-positive behavior can be assessed.

No raw provider responses, user identifiers, API keys, authorization headers, credentials, or other sensitive information are recorded here.

## Next Step

After the provider quota resets:

1. Run the same 30-case benchmark with the Phase-17 candidate prompt.
2. Analyze the completed candidate results.
3. Freeze the candidate result and metric artifacts.
4. Compare them with `experiments/baseline_v2`.
5. Decide whether to keep, revise, or reject the candidate based on measured evidence.

## Later Validation

Repeatability testing has been designed because a single LLM evaluation run contains provider and model variability. Any initial baseline-versus-candidate comparison should therefore be treated as preliminary until repeated runs establish whether the observed behavior is stable.
