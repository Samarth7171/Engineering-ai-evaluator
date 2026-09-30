import pytest

from evaluator.deterministic_checks import (
    calculate_absolute_error,
    calculate_percentage_error,
    evaluate_numerical_answer,
    evaluate_unit,
    normalize_unit,
)


@pytest.mark.parametrize(
    ("expected", "candidate", "absolute_error"),
    [
        (100, 105, 5),
        (105, 100, 5),
    ],
)
def test_calculate_absolute_error_is_positive(
    expected,
    candidate,
    absolute_error,
):
    assert calculate_absolute_error(expected, candidate) == absolute_error


def test_calculate_percentage_error():
    result = calculate_percentage_error(expected=200, candidate=220)

    assert result == pytest.approx(10.0)


@pytest.mark.parametrize(
    ("candidate", "within_tolerance"),
    [
        (101, True),
        (102, True),
        (103, False),
    ],
)
def test_evaluate_numerical_answer_uses_inclusive_two_percent_tolerance(
    candidate,
    within_tolerance,
):
    result = evaluate_numerical_answer(
        expected=100,
        candidate=candidate,
        tolerance=2,
    )

    assert result["within_tolerance"] is within_tolerance


@pytest.mark.parametrize(
    ("candidate", "absolute_error", "within_tolerance"),
    [
        (0, 0, True),
        (1, 1, False),
    ],
)
def test_evaluate_numerical_answer_handles_zero_expected_value(
    candidate,
    absolute_error,
    within_tolerance,
):
    result = evaluate_numerical_answer(
        expected=0,
        candidate=candidate,
    )

    assert result["absolute_error"] == absolute_error
    assert result["percentage_error"] is None
    assert result["within_tolerance"] is within_tolerance


@pytest.mark.parametrize("unit", ["Pa", "pa", " PA "])
def test_normalize_unit_handles_case_and_surrounding_whitespace(unit):
    assert normalize_unit(unit) == "pa"


def test_evaluate_unit_matches_normalized_strings():
    result = evaluate_unit(expected_unit="Pa", candidate_unit="pa")

    assert result["units_match"] is True


def test_evaluate_unit_rejects_different_strings():
    result = evaluate_unit(expected_unit="Pa", candidate_unit="m/s")

    assert result["units_match"] is False
