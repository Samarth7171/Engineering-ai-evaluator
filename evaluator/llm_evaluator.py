import os
import json

from dotenv import load_dotenv
from openai import (
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
)


# --------------------------------------------------
# 1. CONTROLLED EVALUATION ERRORS
# --------------------------------------------------


class EvaluationError(Exception):
    """Base exception for failures the evaluator can report safely."""


class EvaluationConfigurationError(EvaluationError):
    """The evaluation provider is not configured or cannot authenticate."""


class EvaluationRequestError(EvaluationError):
    """The provider request failed or timed out."""


class EvaluationResponseError(EvaluationError):
    """The provider returned an invalid structured evaluation."""


# --------------------------------------------------
# 2. CONNECT TO OPENROUTER LAZILY
# --------------------------------------------------


_client = None


def _get_client():
    global _client

    if _client is not None:
        return _client

    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise EvaluationConfigurationError(
            "The evaluation service is not configured. "
            "Please contact the application administrator."
        )

    _client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=45.0,
        max_retries=1,
    )

    return _client


# --------------------------------------------------
# 3. VALIDATE STRUCTURED RESPONSES
# --------------------------------------------------


RUBRIC_DIMENSIONS = {
    "problem_understanding",
    "engineering_method",
    "mathematical_execution",
    "engineering_validity",
    "final_response_quality",
}

RUBRIC_STATUSES = {
    "correct",
    "partially_correct",
    "incorrect",
    "not_applicable",
}


def _invalid_response():
    return EvaluationResponseError(
        "The evaluation service returned an invalid structured response. "
        "Please retry."
    )


def parse_evaluation_response(raw_response):
    """Parse and validate the evaluator's structured JSON response."""

    if not isinstance(raw_response, str) or not raw_response.strip():
        raise EvaluationResponseError(
            "The evaluation service returned an empty response. "
            "Please retry."
        )

    try:
        evaluation = json.loads(raw_response)
    except json.JSONDecodeError as error:
        raise _invalid_response() from error

    if not isinstance(evaluation, dict):
        raise _invalid_response()

    extracted_answer = evaluation.get("extracted_answer")
    reasoning_evaluation = evaluation.get("reasoning_evaluation")

    if not isinstance(extracted_answer, dict):
        raise _invalid_response()

    required_extracted_fields = {
        "has_numerical_answer",
        "value",
        "unit",
    }

    if not required_extracted_fields <= set(extracted_answer):
        raise _invalid_response()

    has_numerical_answer = extracted_answer["has_numerical_answer"]
    value = extracted_answer["value"]
    unit = extracted_answer["unit"]

    if not isinstance(has_numerical_answer, bool):
        raise _invalid_response()

    if value is not None and (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
    ):
        raise _invalid_response()

    if unit is not None and not isinstance(unit, str):
        raise _invalid_response()

    if has_numerical_answer and value is None:
        raise _invalid_response()

    if not has_numerical_answer and (value is not None or unit is not None):
        raise _invalid_response()

    if not isinstance(reasoning_evaluation, dict):
        raise _invalid_response()

    rubric = reasoning_evaluation.get("rubric")
    errors = reasoning_evaluation.get("errors")

    if not isinstance(rubric, dict):
        raise _invalid_response()

    if not RUBRIC_DIMENSIONS <= set(rubric):
        raise _invalid_response()

    for dimension_name in RUBRIC_DIMENSIONS:
        dimension = rubric.get(dimension_name)

        if not isinstance(dimension, dict):
            raise _invalid_response()

        if dimension.get("status") not in RUBRIC_STATUSES:
            raise _invalid_response()

        if not isinstance(dimension.get("explanation"), str):
            raise _invalid_response()

    if not isinstance(errors, list):
        raise _invalid_response()

    for error in errors:
        if not isinstance(error, dict):
            raise _invalid_response()

        if error.get("category") not in RUBRIC_DIMENSIONS:
            raise _invalid_response()

        if not isinstance(error.get("description"), str):
            raise _invalid_response()

        if not isinstance(error.get("why_it_matters"), str):
            raise _invalid_response()

    if not isinstance(reasoning_evaluation.get("corrected_solution"), str):
        raise _invalid_response()

    if not isinstance(reasoning_evaluation.get("summary"), str):
        raise _invalid_response()

    return evaluation


def _request_evaluation(**request_options):
    try:
        return _get_client().chat.completions.create(**request_options)
    except EvaluationError:
        raise
    except AuthenticationError as error:
        raise EvaluationConfigurationError(
            "The evaluation service could not authenticate with its "
            "provider. Please contact the application administrator."
        ) from error
    except APITimeoutError as error:
        raise EvaluationRequestError(
            "The evaluation service timed out. Please retry."
        ) from error
    except OpenAIError as error:
        raise EvaluationRequestError(
            "The evaluation service request failed. Please retry."
        ) from error

# --------------------------------------------------
# 4. ENGINEERING EVALUATION FUNCTION
# --------------------------------------------------

def evaluate_solution(question, candidate_solution, domain):
    """
    Evaluate an engineering solution and, when present,
    extract its final numerical answer using one LLM call.

    Returns:
        {
            "extracted_answer": {
                "has_numerical_answer": boolean,
                "value": number or null,
                "unit": string or null
            },
            "reasoning_evaluation": {
                ...
            }
        }
    """

    system_prompt = """
You are an engineering solution evaluator.

You have TWO tasks.

TASK 1:
Determine whether the candidate clearly states a final numerical answer.
If a final numerical answer exists, set has_numerical_answer to true,
extract the final result rather than an intermediate calculation, and
extract its unit exactly as used by the candidate.
If no final numerical answer exists, set has_numerical_answer to false
and return null for both value and unit.
Do not invent a numerical answer merely to satisfy the extraction structure.

TASK 2:
Evaluate the engineering solution using Engineering Evaluation Rubric v1.
The engineering reasoning evaluation must still run normally for
conceptual or non-numerical questions.

Evaluate exactly these five rubric dimensions:

- Problem Understanding: Did the candidate correctly understand the given
  information, requested quantity/concept, and meaning of the problem?
- Engineering Method: Are the chosen engineering principles, approach,
  governing equations, formulas, and assumptions appropriate?
- Mathematical Execution: Are substitution, algebra, arithmetic, equation
  manipulation, and numerical calculations correct?
- Engineering Validity: Are units, dimensions, signs, assumptions, magnitude,
  and physical behavior reasonable?
- Final Response Quality: Does the final response actually answer the question
  clearly, correctly, relevantly, and with adequate support?

For each dimension, return a status and explanation. Status must be one of:
correct, partially_correct, incorrect, or not_applicable.
Use not_applicable when a dimension genuinely does not apply. Do not invent
calculations or errors simply to evaluate every dimension.

Identify specific meaningful errors using structured error objects. Each error
must include its rubric category, a description, and why it matters. If no
meaningful errors are identified, return an empty errors array.

Do not assume that the candidate solution is incorrect.
If the solution is correct, clearly state that it is correct
and do not invent errors.

Do not simply say something is wrong.
Explain the engineering reasoning behind the evaluation.

After identifying errors, provide an improved or corrected solution generated
by the evaluator. This corrected solution is not guaranteed ground truth.

Do not invent information that is not supported by the problem.
"""

    user_prompt = f"""
ENGINEERING DOMAIN:

{domain}


ENGINEERING QUESTION:

{question}


CANDIDATE SOLUTION:

{candidate_solution}


Extract the final answer and evaluate the candidate solution.
"""

    response = _request_evaluation(
        model="dots-studio/dots-3-note-preview:free",

        extra_body={
            "provider": {
                "require_parameters": True
            }
        },

        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],

        response_format={
            "type": "json_schema",

            "json_schema": {
                "name": "engineering_evaluation",

                "strict": True,

                "schema": {
                    "type": "object",

                    "properties": {

                        "extracted_answer": {
                            "type": "object",

                            "properties": {
                                "has_numerical_answer": {
                                    "type": "boolean"
                                },

                                "value": {
                                    "type": [
                                        "number",
                                        "null"
                                    ]
                                },

                                "unit": {
                                    "type": [
                                        "string",
                                        "null"
                                    ]
                                }
                            },

                            "required": [
                                "has_numerical_answer",
                                "value",
                                "unit"
                            ],

                            "additionalProperties": False
                        },

                        "reasoning_evaluation": {
                            "type": "object",

                            "properties": {

                                "rubric": {
                                    "type": "object",

                                    "properties": {
                                        "problem_understanding": {
                                            "type": "object",
                                            "properties": {
                                                "status": {
                                                    "type": "string",
                                                    "enum": [
                                                        "correct",
                                                        "partially_correct",
                                                        "incorrect",
                                                        "not_applicable"
                                                    ]
                                                },
                                                "explanation": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "status",
                                                "explanation"
                                            ],
                                            "additionalProperties": False
                                        },

                                        "engineering_method": {
                                            "type": "object",
                                            "properties": {
                                                "status": {
                                                    "type": "string",
                                                    "enum": [
                                                        "correct",
                                                        "partially_correct",
                                                        "incorrect",
                                                        "not_applicable"
                                                    ]
                                                },
                                                "explanation": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "status",
                                                "explanation"
                                            ],
                                            "additionalProperties": False
                                        },

                                        "mathematical_execution": {
                                            "type": "object",
                                            "properties": {
                                                "status": {
                                                    "type": "string",
                                                    "enum": [
                                                        "correct",
                                                        "partially_correct",
                                                        "incorrect",
                                                        "not_applicable"
                                                    ]
                                                },
                                                "explanation": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "status",
                                                "explanation"
                                            ],
                                            "additionalProperties": False
                                        },

                                        "engineering_validity": {
                                            "type": "object",
                                            "properties": {
                                                "status": {
                                                    "type": "string",
                                                    "enum": [
                                                        "correct",
                                                        "partially_correct",
                                                        "incorrect",
                                                        "not_applicable"
                                                    ]
                                                },
                                                "explanation": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "status",
                                                "explanation"
                                            ],
                                            "additionalProperties": False
                                        },

                                        "final_response_quality": {
                                            "type": "object",
                                            "properties": {
                                                "status": {
                                                    "type": "string",
                                                    "enum": [
                                                        "correct",
                                                        "partially_correct",
                                                        "incorrect",
                                                        "not_applicable"
                                                    ]
                                                },
                                                "explanation": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": [
                                                "status",
                                                "explanation"
                                            ],
                                            "additionalProperties": False
                                        }
                                    },

                                    "required": [
                                        "problem_understanding",
                                        "engineering_method",
                                        "mathematical_execution",
                                        "engineering_validity",
                                        "final_response_quality"
                                    ],

                                    "additionalProperties": False
                                },

                                "errors": {
                                    "type": "array",

                                    "items": {
                                        "type": "object",

                                        "properties": {
                                            "category": {
                                                "type": "string",
                                                "enum": [
                                                    "problem_understanding",
                                                    "engineering_method",
                                                    "mathematical_execution",
                                                    "engineering_validity",
                                                    "final_response_quality"
                                                ]
                                            },

                                            "description": {
                                                "type": "string"
                                            },

                                            "why_it_matters": {
                                                "type": "string"
                                            }
                                        },

                                        "required": [
                                            "category",
                                            "description",
                                            "why_it_matters"
                                        ],

                                        "additionalProperties": False
                                    }
                                },

                                "corrected_solution": {
                                    "type": "string"
                                },

                                "summary": {
                                    "type": "string"
                                }
                            },

                            "required": [
                                "rubric",
                                "errors",
                                "corrected_solution",
                                "summary"
                            ],

                            "additionalProperties": False
                        }
                    },

                    "required": [
                        "extracted_answer",
                        "reasoning_evaluation"
                    ],

                    "additionalProperties": False
                }
            }
        }
    )

    try:
        raw_response = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as error:
        raise _invalid_response() from error

    return parse_evaluation_response(raw_response)
