import json
from collections import Counter
from pathlib import Path

import pytest


BENCHMARK_PATH = (
    Path(__file__).resolve().parents[1]
    / "benchmark"
    / "questions.json"
)

REQUIRED_FIELDS = {
    "id",
    "domain",
    "difficulty",
    "question",
    "reference_solution",
    "candidate_solution",
    "candidate_is_correct",
    "injected_error",
    "expected_error_categories",
    "expected_numerical_answer",
    "expected_unit",
    "important_assumptions",
    "notes",
}

ALLOWED_DOMAINS = {
    "Fluid Mechanics",
    "Aerodynamics",
    "Thermodynamics",
    "Engineering Mathematics",
    "Basic Propulsion",
}

ALLOWED_DIFFICULTIES = {
    "Easy",
    "Medium",
}

ALLOWED_ERROR_CATEGORIES = {
    "problem_understanding",
    "engineering_method",
    "mathematical_execution",
    "engineering_validity",
    "final_response_quality",
}


@pytest.fixture(scope="module")
def benchmark_cases():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def test_benchmark_json_loads_as_a_list(benchmark_cases):
    assert isinstance(benchmark_cases, list)


def test_benchmark_contains_exactly_ten_cases(benchmark_cases):
    assert len(benchmark_cases) == 10


def test_every_case_contains_required_fields(benchmark_cases):
    for case in benchmark_cases:
        assert REQUIRED_FIELDS <= set(case)


def test_case_ids_are_unique(benchmark_cases):
    ids = [case["id"] for case in benchmark_cases]

    assert len(ids) == len(set(ids))


def test_only_allowed_domains_are_used(benchmark_cases):
    domains = {case["domain"] for case in benchmark_cases}

    assert domains <= ALLOWED_DOMAINS


def test_each_domain_has_exactly_two_cases(benchmark_cases):
    domain_counts = Counter(case["domain"] for case in benchmark_cases)

    assert set(domain_counts) == ALLOWED_DOMAINS
    assert all(count == 2 for count in domain_counts.values())


def test_only_allowed_difficulties_are_used(benchmark_cases):
    difficulties = {case["difficulty"] for case in benchmark_cases}

    assert difficulties <= ALLOWED_DIFFICULTIES


def test_only_allowed_error_categories_are_used(benchmark_cases):
    categories = {
        category
        for case in benchmark_cases
        for category in case["expected_error_categories"]
    }

    assert categories <= ALLOWED_ERROR_CATEGORIES


def test_correct_candidates_have_no_injected_errors(benchmark_cases):
    correct_cases = [
        case for case in benchmark_cases if case["candidate_is_correct"]
    ]

    for case in correct_cases:
        assert case["injected_error"] is None
        assert case["expected_error_categories"] == []


def test_incorrect_candidates_have_expected_errors(benchmark_cases):
    incorrect_cases = [
        case for case in benchmark_cases if not case["candidate_is_correct"]
    ]

    for case in incorrect_cases:
        assert case["injected_error"] is not None
        assert case["expected_error_categories"]


def test_reference_value_and_unit_may_be_null(benchmark_cases):
    for case in benchmark_cases:
        expected_value = case["expected_numerical_answer"]
        expected_unit = case["expected_unit"]

        assert expected_value is None or (
            isinstance(expected_value, (int, float))
            and not isinstance(expected_value, bool)
        )
        assert expected_unit is None or isinstance(expected_unit, str)


def test_benchmark_v1_candidate_composition(benchmark_cases):
    correct_count = sum(
        case["candidate_is_correct"] for case in benchmark_cases
    )
    incorrect_count = len(benchmark_cases) - correct_count

    assert len(benchmark_cases) == 10
    assert correct_count == 4
    assert incorrect_count == 6
