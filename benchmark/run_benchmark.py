import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BENCHMARK_PATH = PROJECT_ROOT / "benchmark" / "questions.json"
RESULTS_PATH = PROJECT_ROOT / "benchmark" / "results.json"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluator.deterministic_checks import (  # noqa: E402
    evaluate_numerical_answer,
    evaluate_unit,
)
from evaluator.llm_evaluator import evaluate_solution  # noqa: E402


SEPARATOR = "-" * 50


def load_benchmark_cases():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError("Benchmark data must be a JSON array.")

    return cases


def extract_detected_categories(errors):
    categories = {
        error.get("category")
        for error in errors
        if isinstance(error, dict)
        and isinstance(error.get("category"), str)
    }

    return sorted(categories)


def compare_reference_number(expected_value, extracted_answer):
    if expected_value is None:
        return None

    candidate_value = extracted_answer.get("value")
    has_numerical_answer = extracted_answer.get(
        "has_numerical_answer",
        False,
    )

    if (
        not has_numerical_answer
        or not isinstance(candidate_value, (int, float))
        or isinstance(candidate_value, bool)
    ):
        return {
            "performed": False,
            "expected": expected_value,
            "candidate": candidate_value,
            "reason": "The evaluator did not extract a numerical answer.",
        }

    comparison = evaluate_numerical_answer(
        expected=expected_value,
        candidate=candidate_value,
        tolerance=2,
    )

    return {
        "performed": True,
        **comparison,
    }


def compare_reference_unit(expected_unit, extracted_answer):
    if expected_unit is None:
        return None

    candidate_unit = extracted_answer.get("unit")

    if not isinstance(candidate_unit, str) or not candidate_unit.strip():
        return {
            "performed": False,
            "expected_unit": expected_unit,
            "candidate_unit": candidate_unit,
            "reason": "The evaluator did not extract a candidate unit.",
        }

    comparison = evaluate_unit(
        expected_unit=expected_unit,
        candidate_unit=candidate_unit,
    )

    return {
        "performed": True,
        **comparison,
    }


def evaluate_benchmark_case(case):
    # Benchmark ground truth is intentionally excluded from this call.
    evaluation = evaluate_solution(
        domain=case["domain"],
        question=case["question"],
        candidate_solution=case["candidate_solution"],
    )

    extracted_answer = evaluation["extracted_answer"]
    reasoning_evaluation = evaluation["reasoning_evaluation"]
    errors = reasoning_evaluation.get("errors", [])

    expected_categories = case["expected_error_categories"]
    detected_categories = extract_detected_categories(errors)
    missing_categories = sorted(
        set(expected_categories) - set(detected_categories)
    )
    additional_categories = sorted(
        set(detected_categories) - set(expected_categories)
    )

    candidate_is_correct = case["candidate_is_correct"]
    root_error_detection_pass = (
        None if candidate_is_correct else not missing_categories
    )
    false_positive_pass = (
        not errors if candidate_is_correct else None
    )

    return {
        "id": case["id"],
        "domain": case["domain"],
        "candidate_is_correct": candidate_is_correct,
        "evaluation_status": "completed",
        "evaluation_failure": None,
        "expected_error_categories": expected_categories,
        "detected_error_categories": detected_categories,
        "missing_required_categories": missing_categories,
        "additional_detected_categories": additional_categories,
        "root_error_detection_pass": root_error_detection_pass,
        "false_positive_pass": false_positive_pass,
        "extracted_numerical_value": extracted_answer.get("value"),
        "extracted_unit": extracted_answer.get("unit"),
        "reference_numerical_comparison": compare_reference_number(
            case["expected_numerical_answer"],
            extracted_answer,
        ),
        "reference_unit_comparison": compare_reference_unit(
            case["expected_unit"],
            extracted_answer,
        ),
        "evaluator_summary": reasoning_evaluation.get("summary"),
        "evaluator_errors": errors,
    }


def create_failure_result(case, error):
    expected_categories = case["expected_error_categories"]

    return {
        "id": case["id"],
        "domain": case["domain"],
        "candidate_is_correct": case["candidate_is_correct"],
        "evaluation_status": "failed",
        "evaluation_failure": {
            "type": type(error).__name__,
            "message": str(error),
        },
        "expected_error_categories": expected_categories,
        "detected_error_categories": [],
        "missing_required_categories": (
            []
            if case["candidate_is_correct"]
            else list(expected_categories)
        ),
        "additional_detected_categories": [],
        "root_error_detection_pass": None,
        "false_positive_pass": None,
        "extracted_numerical_value": None,
        "extracted_unit": None,
        "reference_numerical_comparison": None,
        "reference_unit_comparison": None,
        "evaluator_summary": None,
        "evaluator_errors": [],
    }


def format_categories(categories):
    return ", ".join(categories) if categories else "none"


def format_pass_fail(value):
    if value is None:
        return "NOT APPLICABLE"

    return "PASS" if value else "FAIL"


def print_reference_comparisons(result):
    numerical = result["reference_numerical_comparison"]

    if numerical is not None:
        if numerical["performed"]:
            outcome = format_pass_fail(numerical["within_tolerance"])
            print(
                "Reference numerical comparison: "
                f"{outcome} "
                f"(reference={numerical['expected']}, "
                f"extracted={numerical['candidate']})"
            )
        else:
            print(
                "Reference numerical comparison: NOT PERFORMED "
                f"({numerical['reason']})"
            )

    unit = result["reference_unit_comparison"]

    if unit is not None:
        if unit["performed"]:
            outcome = "MATCH" if unit["units_match"] else "MISMATCH"
            print(
                "Reference unit comparison: "
                f"{outcome} "
                f"(reference={unit['expected_unit']}, "
                f"extracted={unit['candidate_unit']})"
            )
        else:
            print(
                "Reference unit comparison: NOT PERFORMED "
                f"({unit['reason']})"
            )


def print_case_result(result):
    print(SEPARATOR)
    print(f"{result['id']} | {result['domain']}")

    if result["evaluation_status"] == "failed":
        failure = result["evaluation_failure"]
        print(
            "Evaluation/API failure: "
            f"{failure['type']}: {failure['message']}"
        )
        print(SEPARATOR)
        return

    expected_categories = result["expected_error_categories"]
    detected_categories = result["detected_error_categories"]

    if result["candidate_is_correct"]:
        print("Expected errors: none")
        print(f"Detected errors: {format_categories(detected_categories)}")
        print(
            "False-positive test: "
            f"{format_pass_fail(result['false_positive_pass'])}"
        )
    else:
        print(
            "Expected root errors: "
            f"{format_categories(expected_categories)}"
        )
        print(f"Detected errors: {format_categories(detected_categories)}")
        print(
            "Missing required errors: "
            f"{format_categories(result['missing_required_categories'])}"
        )
        print(
            "Additional detected errors: "
            f"{format_categories(result['additional_detected_categories'])}"
        )
        print(
            "Required root detection: "
            f"{format_pass_fail(result['root_error_detection_pass'])}"
        )

    print(
        "Extracted answer: "
        f"{result['extracted_numerical_value']} "
        f"{result['extracted_unit']}"
    )
    print_reference_comparisons(result)
    print(f"Evaluator summary: {result['evaluator_summary']}")
    print(SEPARATOR)


def build_aggregate_counts(cases, results):
    return {
        "total_cases": len(cases),
        "completed_evaluations": sum(
            result["evaluation_status"] == "completed"
            for result in results
        ),
        "api_or_evaluation_failures": sum(
            result["evaluation_status"] == "failed"
            for result in results
        ),
        "intentionally_incorrect_cases": sum(
            not case["candidate_is_correct"] for case in cases
        ),
        "required_root_error_detections_passed": sum(
            result["root_error_detection_pass"] is True
            for result in results
        ),
        "required_root_error_detections_failed": sum(
            result["root_error_detection_pass"] is False
            for result in results
        ),
        "intentionally_correct_cases": sum(
            case["candidate_is_correct"] for case in cases
        ),
        "false_positive_tests_passed": sum(
            result["false_positive_pass"] is True
            for result in results
        ),
        "false_positive_tests_failed": sum(
            result["false_positive_pass"] is False
            for result in results
        ),
    }


def print_final_summary(counts):
    print("\nBenchmark Summary")
    print(SEPARATOR)
    print(f"Total cases: {counts['total_cases']}")
    print(f"Completed evaluations: {counts['completed_evaluations']}")
    print(
        "API/evaluation failures: "
        f"{counts['api_or_evaluation_failures']}"
    )
    print(
        "Intentionally incorrect cases: "
        f"{counts['intentionally_incorrect_cases']}"
    )
    print(
        "Required root-error detections passed: "
        f"{counts['required_root_error_detections_passed']}"
    )
    print(
        "Required root-error detections failed: "
        f"{counts['required_root_error_detections_failed']}"
    )
    print(
        "Intentionally correct cases: "
        f"{counts['intentionally_correct_cases']}"
    )
    print(
        "False-positive tests passed: "
        f"{counts['false_positive_tests_passed']}"
    )
    print(
        "False-positive tests failed: "
        f"{counts['false_positive_tests_failed']}"
    )
    print(SEPARATOR)


def save_results(started_at, results, aggregate_counts):
    output = {
        "run_metadata": {
            "runner": "Engineering AI Evaluator Benchmark v1",
            "started_at_utc": started_at,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "benchmark_case_count": len(results),
        },
        "case_results": results,
        "aggregate_counts": aggregate_counts,
    }

    RESULTS_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main():
    started_at = datetime.now(timezone.utc).isoformat()
    cases = load_benchmark_cases()
    results = []

    for case in cases:
        try:
            result = evaluate_benchmark_case(case)
        except Exception as error:
            result = create_failure_result(case, error)

        results.append(result)
        print_case_result(result)

    aggregate_counts = build_aggregate_counts(cases, results)
    print_final_summary(aggregate_counts)
    save_results(started_at, results, aggregate_counts)
    print(f"Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
