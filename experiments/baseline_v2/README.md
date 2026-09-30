# Benchmark v2 Baseline

This directory freezes the pre-Phase-17 Engineering AI Evaluator baseline for Benchmark v2.

## Run Context

- Benchmark dataset: 30 controlled engineering cases
- Evaluator: Git HEAD baseline, before the Phase-17 prompt improvement
- Execution: sequential live LLM evaluation using the configured external provider/model

## Baseline Metrics

- Total cases: 30
- Completed: 24
- Evaluation failures: 6
- Completion rate: 80.00%
- Error detection rate: 94.12% (16/17 completed incorrect cases)
- Root-category agreement: 76.47% (13/17 completed incorrect cases)
- False-positive rate: 0.00% (0/7 completed correct cases)
- Correct-case clean rate: 100.00% (7/7 completed correct cases)

These are controlled Benchmark v2 results. The 94.12% error detection rate must not be described as general evaluator accuracy.

Failed evaluations are excluded from the completed-case error-detection, root-category-agreement, false-positive, and correct-case-clean denominators. Results can vary between runs because evaluation depends on an external LLM provider and model.

The copied `results.json` and `metrics.json` files preserve the case-level results and derived metrics from this baseline run.
