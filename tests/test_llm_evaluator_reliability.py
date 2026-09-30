import json

import pytest
from openai import OpenAIError

import evaluator.llm_evaluator as llm_evaluator
from evaluator.llm_evaluator import (
    EvaluationConfigurationError,
    EvaluationError,
    EvaluationRequestError,
    EvaluationResponseError,
    parse_evaluation_response,
)


RUBRIC_DIMENSIONS = [
    "problem_understanding",
    "engineering_method",
    "mathematical_execution",
    "engineering_validity",
    "final_response_quality",
]


def valid_evaluation():
    return {
        "extracted_answer": {
            "has_numerical_answer": False,
            "value": None,
            "unit": None,
        },
        "reasoning_evaluation": {
            "rubric": {
                dimension: {
                    "status": "correct",
                    "explanation": "The candidate handled this dimension.",
                }
                for dimension in RUBRIC_DIMENSIONS
            },
            "errors": [],
            "corrected_solution": "No correction is needed.",
            "summary": "The response is correct.",
        },
    }


@pytest.mark.parametrize(
    "exception_type",
    [
        EvaluationConfigurationError,
        EvaluationRequestError,
        EvaluationResponseError,
    ],
)
def test_controlled_errors_share_evaluation_error_base(exception_type):
    assert issubclass(exception_type, EvaluationError)


def test_missing_configuration_raises_controlled_error(monkeypatch):
    monkeypatch.setattr(llm_evaluator, "_client", None)
    monkeypatch.setattr(llm_evaluator, "load_dotenv", lambda: None)
    monkeypatch.setattr(llm_evaluator.os, "getenv", lambda name: None)

    with pytest.raises(EvaluationConfigurationError):
        llm_evaluator._get_client()


def test_provider_error_is_converted_without_exposing_details(monkeypatch):
    class FailingCompletions:
        def create(self, **request_options):
            raise OpenAIError("sensitive provider details")

    class FakeChat:
        completions = FailingCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(
        llm_evaluator,
        "_get_client",
        lambda: FakeClient(),
    )

    with pytest.raises(EvaluationRequestError) as captured:
        llm_evaluator._request_evaluation(model="test-model")

    assert "sensitive provider details" not in str(captured.value)
    assert "Please retry" in str(captured.value)


def test_valid_structured_response_is_parsed():
    expected = valid_evaluation()

    assert parse_evaluation_response(json.dumps(expected)) == expected


@pytest.mark.parametrize("raw_response", ["", "   "])
def test_empty_response_raises_controlled_error(raw_response):
    with pytest.raises(EvaluationResponseError):
        parse_evaluation_response(raw_response)


def test_invalid_json_raises_controlled_error():
    with pytest.raises(EvaluationResponseError):
        parse_evaluation_response("not valid JSON")


def test_missing_required_structure_is_rejected():
    response = valid_evaluation()
    del response["reasoning_evaluation"]["summary"]

    with pytest.raises(EvaluationResponseError):
        parse_evaluation_response(json.dumps(response))


def test_invalid_rubric_status_is_rejected():
    response = valid_evaluation()
    response["reasoning_evaluation"]["rubric"][
        "engineering_method"
    ]["status"] = "unknown"

    with pytest.raises(EvaluationResponseError):
        parse_evaluation_response(json.dumps(response))


def test_malformed_structured_error_is_rejected():
    response = valid_evaluation()
    response["reasoning_evaluation"]["errors"] = [
        {
            "category": "engineering_method",
            "description": "Wrong governing equation.",
        }
    ]

    with pytest.raises(EvaluationResponseError):
        parse_evaluation_response(json.dumps(response))


def test_inconsistent_non_numerical_extraction_is_rejected():
    response = valid_evaluation()
    response["extracted_answer"]["value"] = 10

    with pytest.raises(EvaluationResponseError):
        parse_evaluation_response(json.dumps(response))
