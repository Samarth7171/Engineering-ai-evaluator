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
    Evaluate an engineering solution using an LLM.

    Parameters:
        question: The engineering problem.
        candidate_solution: The proposed AI-generated solution.
        domain: The engineering subject/domain.

    Returns:
        A Python dictionary containing the structured evaluation.
    """

    # --------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------

    system_prompt = """
You are an engineering solution evaluator.

Your job is to carefully evaluate a proposed solution to an
engineering problem.

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

Do not assume that the candidate solution is correct.

Do not simply say that something is wrong.
Explain the engineering reasoning behind the evaluation.

After identifying errors, provide a corrected solution.

Do not invent information that is not supported by the problem.
"""

    # --------------------------------------------------
    # USER PROMPT
    # --------------------------------------------------

    user_prompt = f"""
ENGINEERING DOMAIN:

{domain}


ENGINEERING QUESTION:

{question}


CANDIDATE SOLUTION:

{candidate_solution}


Evaluate the candidate solution.
"""

    # --------------------------------------------------
    # CALL THE LLM
    # --------------------------------------------------

    response = client.chat.completions.create(
        model="openrouter/free",

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
            }
        }
    )

    # --------------------------------------------------
    # GET RESPONSE FROM LLM
    # --------------------------------------------------

    raw_response = response.choices[0].message.content

    if not raw_response:
        raise ValueError("The LLM returned an empty response.")

    # --------------------------------------------------
    # CONVERT JSON TEXT → PYTHON DICTIONARY
    # --------------------------------------------------

    try:
        evaluation = json.loads(raw_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            "The LLM returned an invalid structured response."
        ) from error

    # --------------------------------------------------
    # RETURN RESULT TO APP.PY
    # --------------------------------------------------

    return evaluation