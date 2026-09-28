def calculate_absolute_error(expected, candidate):
    """Calculate the numerical difference between two values."""
    return abs(expected - candidate)


def calculate_percentage_error(expected, candidate):
    """Calculate percentage error relative to the expected value."""
    if expected == 0:
        return None

    absolute_error = calculate_absolute_error(expected, candidate)
    return (absolute_error / abs(expected)) * 100


def evaluate_numerical_answer(expected, candidate, tolerance=2):
    """Evaluate a candidate numerical answer against a reference answer."""

    absolute_error = calculate_absolute_error(expected, candidate)
    percentage_error = calculate_percentage_error(expected, candidate)

    if percentage_error is None:
        within_tolerance = absolute_error == 0
    else:
        within_tolerance = percentage_error <= tolerance

    return {
        "expected": expected,
        "candidate": candidate,
        "absolute_error": absolute_error,
        "percentage_error": percentage_error,
        "tolerance": tolerance,
        "within_tolerance": within_tolerance,
    }