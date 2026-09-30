import json
import sys
from pathlib import Path


BENCHMARK_DIR = Path(__file__).resolve().parent
RESULTS_PATH = BENCHMARK_DIR / "results.json"
METRICS_PATH = BENCHMARK_DIR / "metrics.json"


def calculate_rate(numerator, denominator):
    if denominator == 0:
        return None

    return numerator / denominator


def load_results():
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(
            "benchmark/results.json was not found. "
            "Run benchmark/run_benchmark.py first."
        )

    with open(RESULTS_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    case_results = data.get("case_results", [])

    if not isinstance(case_results, list):
        raise ValueError(
            "benchmark/results.json must contain a case_results array."
        )

    return data, case_results


def evaluation_completed(case):
    return case.get("evaluation_status") == "completed"


def error_detected(case):
    errors = case.get("evaluator_errors")

    if isinstance(errors, list):
        return bool(errors)

    categories = case.get("detected_error_categories", [])
    return bool(categories) if isinstance(categories, list) else False


def build_case_diagnostics(case_results):
    diagnostics = []

    for case in case_results:
        completed = evaluation_completed(case)
        candidate_is_correct = case.get("candidate_is_correct")
        detected = error_detected(case) if completed else None

        root_agreement = None
        false_positive = None

        if completed and candidate_is_correct is False:
            root_agreement = (
                case.get("root_error_detection_pass") is True
            )

        if completed and candidate_is_correct is True:
            false_positive = detected

        categories = case.get("detected_error_categories", [])
        if not isinstance(categories, list):
            categories = []

        diagnostics.append(
            {
                "id": case.get("id"),
                "domain": case.get("domain"),
                "candidate_is_correct": candidate_is_correct,
                "evaluation_completed": completed,
                "error_detected": detected,
                "root_category_agreement": root_agreement,
                "false_positive": false_positive,
                "detected_categories": categories,
            }
        )

    return diagnostics


def build_failure_information(case_results):
    failures = []

    for case in case_results:
        if evaluation_completed(case):
            continue

        failure = case.get("evaluation_failure")
        failure_type = None
        failure_message = None

        if isinstance(failure, dict):
            failure_type = failure.get("type")
            failure_message = failure.get("message")
        elif failure is not None:
            failure_message = str(failure)

        failures.append(
            {
                "id": case.get("id"),
                "domain": case.get("domain"),
                "failure_type": failure_type,
                "failure_message": (
                    failure_message
                    or "No failure message was recorded."
                ),
            }
        )

    return failures


def count_reference_comparisons(case_results, field, outcome_field):
    performed = 0
    matches = 0
    mismatches = 0
    not_performed = 0

    for case in case_results:
        if not evaluation_completed(case):
            continue

        comparison = case.get(field)

        if comparison is None:
            continue

        if not isinstance(comparison, dict) or not comparison.get(
            "performed",
            False,
        ):
            not_performed += 1
            continue

        performed += 1

        if comparison.get(outcome_field) is True:
            matches += 1
        else:
            mismatches += 1

    return {
        "performed_comparisons": performed,
        "matches": matches,
        "mismatches": mismatches,
        "not_performed": not_performed,
    }


def calculate_metrics(case_results):
    total_cases = len(case_results)
    completed_cases = [
        case for case in case_results if evaluation_completed(case)
    ]
    failed_cases = total_cases - len(completed_cases)

    completed_incorrect_cases = [
        case
        for case in completed_cases
        if case.get("candidate_is_correct") is False
    ]
    detected_incorrect_cases = sum(
        error_detected(case) for case in completed_incorrect_cases
    )
    root_agreement_passes = sum(
        case.get("root_error_detection_pass") is True
        for case in completed_incorrect_cases
    )

    completed_correct_cases = [
        case
        for case in completed_cases
        if case.get("candidate_is_correct") is True
    ]
    false_positive_cases = sum(
        error_detected(case) for case in completed_correct_cases
    )
    clean_correct_cases = (
        len(completed_correct_cases) - false_positive_cases
    )

    completion = {
        "total_cases": total_cases,
        "completed_cases": len(completed_cases),
        "failed_cases": failed_cases,
        "evaluation_completion_rate": calculate_rate(
            len(completed_cases),
            total_cases,
        ),
    }

    error_detection = {
        "completed_intentionally_incorrect_cases": len(
            completed_incorrect_cases
        ),
        "cases_with_detected_errors": detected_incorrect_cases,
        "cases_without_detected_errors": (
            len(completed_incorrect_cases) - detected_incorrect_cases
        ),
        "error_detection_rate": calculate_rate(
            detected_incorrect_cases,
            len(completed_incorrect_cases),
        ),
    }

    root_category_agreement = {
        "completed_intentionally_incorrect_cases": len(
            completed_incorrect_cases
        ),
        "agreement_passes": root_agreement_passes,
        "agreement_failures": (
            len(completed_incorrect_cases) - root_agreement_passes
        ),
        "root_category_agreement_rate": calculate_rate(
            root_agreement_passes,
            len(completed_incorrect_cases),
        ),
    }

    false_positive_behavior = {
        "completed_intentionally_correct_cases": len(
            completed_correct_cases
        ),
        "false_positive_cases": false_positive_cases,
        "clean_correct_cases": clean_correct_cases,
        "false_positive_rate": calculate_rate(
            false_positive_cases,
            len(completed_correct_cases),
        ),
        "correct_case_clean_rate": calculate_rate(
            clean_correct_cases,
            len(completed_correct_cases),
        ),
    }

    return {
        "benchmark_case_count": total_cases,
        "completion": completion,
        "error_detection": error_detection,
        "root_category_agreement": root_category_agreement,
        "false_positive_behavior": false_positive_behavior,
        "reference_numerical_comparison": count_reference_comparisons(
            completed_cases,
            "reference_numerical_comparison",
            "within_tolerance",
        ),
        "reference_unit_comparison": count_reference_comparisons(
            completed_cases,
            "reference_unit_comparison",
            "units_match",
        ),
        "failures": build_failure_information(case_results),
        "case_diagnostics": build_case_diagnostics(case_results),
    }


def format_rate(rate, numerator, denominator):
    if rate is None:
        return f"N/A ({numerator}/{denominator})"

    return f"{rate * 100:.2f}% ({numerator}/{denominator})"


def format_yes_no(value):
    if value is None:
        return "N/A"

    return "Yes" if value else "No"


def format_pass_fail(value):
    if value is None:
        return "N/A"

    return "PASS" if value else "FAIL"


def print_metric_summary(metrics):
    completion = metrics["completion"]
    error_detection = metrics["error_detection"]
    root_agreement = metrics["root_category_agreement"]
    false_positive = metrics["false_positive_behavior"]
    numerical = metrics["reference_numerical_comparison"]
    unit = metrics["reference_unit_comparison"]

    print("Engineering AI Evaluator — Benchmark Metrics v1")
    print("=" * 58)

    print("\nEvaluation completion/reliability")
    print(f"Total cases: {completion['total_cases']}")
    print(f"Completed cases: {completion['completed_cases']}")
    print(
        "Failed/API/structured-output cases: "
        f"{completion['failed_cases']}"
    )
    print(
        "Evaluation completion rate: "
        + format_rate(
            completion["evaluation_completion_rate"],
            completion["completed_cases"],
            completion["total_cases"],
        )
    )

    print("\nError detection")
    print(
        "Error detection rate: "
        + format_rate(
            error_detection["error_detection_rate"],
            error_detection["cases_with_detected_errors"],
            error_detection[
                "completed_intentionally_incorrect_cases"
            ],
        )
    )

    print("\nRoot-error category agreement")
    print(
        "Root-category agreement rate: "
        + format_rate(
            root_agreement["root_category_agreement_rate"],
            root_agreement["agreement_passes"],
            root_agreement[
                "completed_intentionally_incorrect_cases"
            ],
        )
    )

    print("\nFalse-positive behavior")
    print(
        "False-positive rate: "
        + format_rate(
            false_positive["false_positive_rate"],
            false_positive["false_positive_cases"],
            false_positive[
                "completed_intentionally_correct_cases"
            ],
        )
    )
    print(
        "Correct-case clean rate: "
        + format_rate(
            false_positive["correct_case_clean_rate"],
            false_positive["clean_correct_cases"],
            false_positive[
                "completed_intentionally_correct_cases"
            ],
        )
    )

    print("\nReference numerical comparison")
    print(
        "These counts describe candidate-answer agreement with trusted "
        "benchmark values, not evaluator extraction accuracy."
    )
    print(f"Matches: {numerical['matches']}")
    print(f"Mismatches: {numerical['mismatches']}")
    print(f"Comparisons not performed: {numerical['not_performed']}")

    print("\nReference unit comparison")
    print(
        "These counts compare evaluator-extracted candidate units with "
        "trusted benchmark units; they are not extraction accuracy."
    )
    print(f"Matches: {unit['matches']}")
    print(f"Mismatches: {unit['mismatches']}")
    print(f"Comparisons not performed: {unit['not_performed']}")


def print_failures(failures):
    print("\nEvaluation failures")

    if not failures:
        print("None")
        return

    for failure in failures:
        failure_label = failure["failure_message"]

        if failure["failure_type"]:
            failure_label = (
                f"{failure['failure_type']}: {failure_label}"
            )

        print(
            f"- {failure['id']} | {failure['domain']} | "
            f"{failure_label}"
        )


def table_value(value):
    return "" if value is None else str(value)


def print_case_diagnostic_table(diagnostics):
    print("\nCase-level diagnostics")

    headers = [
        "Case ID",
        "Domain",
        "Candidate correct?",
        "Completed?",
        "Error detected?",
        "Root agreement",
        "False positive",
        "Detected categories",
    ]

    rows = []

    for case in diagnostics:
        categories = case["detected_categories"]
        category_text = ", ".join(categories) if categories else "none"

        rows.append(
            [
                table_value(case["id"]),
                table_value(case["domain"]),
                format_yes_no(case["candidate_is_correct"]),
                format_yes_no(case["evaluation_completed"]),
                format_yes_no(case["error_detected"]),
                format_pass_fail(case["root_category_agreement"]),
                format_yes_no(case["false_positive"]),
                category_text,
            ]
        )

    widths = [len(header) for header in headers]

    for row in rows:
        widths = [
            max(width, len(value))
            for width, value in zip(widths, row)
        ]

    def print_row(row):
        print(
            " | ".join(
                value.ljust(width)
                for value, width in zip(row, widths)
            )
        )

    print_row(headers)
    print("-+-".join("-" * width for width in widths))

    for row in rows:
        print_row(row)


def save_metrics(metrics):
    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main():
    try:
        _, case_results = load_results()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"Unable to analyze benchmark results: {error}")
        return 1

    metrics = calculate_metrics(case_results)
    print_metric_summary(metrics)
    print_failures(metrics["failures"])
    print_case_diagnostic_table(metrics["case_diagnostics"])
    save_metrics(metrics)
    print(f"\nMetrics saved to: {METRICS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
