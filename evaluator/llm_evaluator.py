import os
import json

from dotenv import load_dotenv
from openai import OpenAI


# --------------------------------------------------
# 1. LOAD API KEY
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY was not found in .env")


# --------------------------------------------------
# 2. CONNECT TO OPENROUTER
# --------------------------------------------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    timeout=45.0,
    max_retries=1,
)


# --------------------------------------------------
# 3. ENGINEERING EVALUATION FUNCTION
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
Evaluate the engineering solution.
The engineering reasoning evaluation must still run normally for
conceptual or non-numerical questions.

Evaluate:

- problem understanding
- approach
- equations and formulas
- mathematical reasoning
- numerical calculations
- units
- assumptions
- physical plausibility
- final answer
- explanation quality

Identify specific errors and explain WHY they are errors.

Do not assume that the candidate solution is incorrect.
If the solution is correct, clearly state that it is correct
and do not invent errors.

Do not simply say something is wrong.
Explain the engineering reasoning behind the evaluation.

After identifying errors, provide a corrected or improved solution.

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

    response = client.chat.completions.create(
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

                                "problem_understanding": {
                                    "type": "string"
                                },

                                "approach": {
                                    "type": "string"
                                },

                                "equations": {
                                    "type": "string"
                                },

                                "calculations": {
                                    "type": "string"
                                },

                                "units": {
                                    "type": "string"
                                },

                                "assumptions": {
                                    "type": "string"
                                },

                                "physical_plausibility": {
                                    "type": "string"
                                },

                                "final_answer": {
                                    "type": "string"
                                },

                                "explanation_quality": {
                                    "type": "string"
                                },

                                "errors": {
                                    "type": "array",

                                    "items": {
                                        "type": "string"
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
                                "problem_understanding",
                                "approach",
                                "equations",
                                "calculations",
                                "units",
                                "assumptions",
                                "physical_plausibility",
                                "final_answer",
                                "explanation_quality",
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

    raw_response = response.choices[0].message.content

    if not raw_response:
        raise ValueError(
            "The LLM returned an empty response."
        )

    try:
        evaluation = json.loads(raw_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            "The LLM returned an invalid structured response."
        ) from error

    return evaluation
