# --------------------------------------------------
# NUMERICAL CHECKS
# --------------------------------------------------

def calculate_absolute_error(expected, candidate):
    """Calculate the numerical difference between two values."""
    return abs(expected - candidate)


def calculate_percentage_error(expected, candidate):
    """Calculate percentage error relative to the expected value."""

    if expected == 0:
        return None

    absolute_error = calculate_absolute_error(
        expected,
        candidate
    )

    return (
        absolute_error / abs(expected)
    ) * 100


def evaluate_numerical_answer(
    expected,
    candidate,
    tolerance=2
):
    """
    Evaluate a candidate numerical answer
    against a reference answer.
    """

    absolute_error = calculate_absolute_error(
        expected,
        candidate
    )

    percentage_error = calculate_percentage_error(
        expected,
        candidate
    )

    if percentage_error is None:
        within_tolerance = absolute_error == 0

    else:
        within_tolerance = (
            percentage_error <= tolerance
        )

    return {
        "expected": expected,
        "candidate": candidate,
        "absolute_error": absolute_error,
        "percentage_error": percentage_error,
        "tolerance": tolerance,
        "within_tolerance": within_tolerance,
    }


# --------------------------------------------------
# UNIT CHECKS
# --------------------------------------------------

def normalize_unit(unit):
    """
    Prepare a unit string for simple comparison.

    Example:
        " Pa " -> "pa"
        "M/S"  -> "m/s"
    """

    return unit.strip().lower()


def evaluate_unit(expected_unit, candidate_unit):
    """
    Compare the candidate unit with
    the expected benchmark unit.

    This is currently a simple exact comparison
    after basic normalization.
    """

    normalized_expected = normalize_unit(
        expected_unit
    )

    normalized_candidate = normalize_unit(
        candidate_unit
    )

    units_match = (
        normalized_expected
        == normalized_candidate
    )

    return {
        "expected_unit": expected_unit,
        "candidate_unit": candidate_unit,
        "units_match": units_match,
    }


# --------------------------------------------------
# TEMPORARY DEVELOPMENT TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\nCorrect unit test:")

    correct_unit = evaluate_unit(
        expected_unit="Pa",
        candidate_unit="Pa",
    )

    print(correct_unit)


    print("\nWrong unit test:")

    wrong_unit = evaluate_unit(
        expected_unit="Pa",
        candidate_unit="m/s",
    )

    print(wrong_unit)