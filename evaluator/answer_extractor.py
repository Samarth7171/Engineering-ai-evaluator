import json
from pathlib import Path

from evaluator.llm_evaluator import client
from evaluator.deterministic_checks import evaluate_numerical_answer


# --------------------------------------------------
# ANSWER EXTRACTION FUNCTION
# --------------------------------------------------

def extract_final_answer(candidate_solution):
    """
    Extract the final numerical answer and unit
    from an engineering solution.

    Example output:
    {
        "value": 3062.5,
        "unit": "Pa"
    }
    """

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
                "content": (
                    "You extract the final numerical answer from "
                    "an engineering solution. Extract the answer "
                    "stated as the final result, not intermediate values."
                ),
            },
            {
                "role": "user",
                "content": candidate_solution,
            },
        ],

        response_format={
            "type": "json_schema",

            "json_schema": {
                "name": "final_answer_extraction",

                "strict": True,

                "schema": {
                    "type": "object",

                    "properties": {
                        "value": {
                            "type": "number"
                        },

                        "unit": {
                            "type": "string"
                        }
                    },

                    "required": [
                        "value",
                        "unit"
                    ],

                    "additionalProperties": False
                }
            }
        }
    )

    # Get the response from the LLM
    raw_response = response.choices[0].message.content

    # Make sure the LLM returned something
    if not raw_response:
        raise ValueError(
            "The answer extractor returned an empty response."
        )

    # Convert JSON text into a Python dictionary
    extracted_answer = json.loads(raw_response)

    return extracted_answer


# --------------------------------------------------
# TEMPORARY DEVELOPMENT TEST
# --------------------------------------------------

if __name__ == "__main__":

    # --------------------------------------------------
    # STEP 1: FIND THE PROJECT ROOT
    # --------------------------------------------------

    project_root = Path(__file__).resolve().parent.parent

    benchmark_path = (
        project_root
        / "benchmark"
        / "questions.json"
    )


    # --------------------------------------------------
    # STEP 2: LOAD THE BENCHMARK DATA
    # --------------------------------------------------

    with open(
        benchmark_path,
        "r",
        encoding="utf-8"
    ) as file:

        benchmark_data = json.load(file)


    # --------------------------------------------------
    # STEP 3: SELECT FIRST BENCHMARK PROBLEM
    # --------------------------------------------------

    problem = benchmark_data[0]


    print("\nBenchmark question:")
    print(problem["question"])

    print("\nExpected answer:")
    print(
        problem["expected_answer"],
        problem["expected_unit"]
    )


    # --------------------------------------------------
    # STEP 4: CREATE TEST CANDIDATE SOLUTION
    # --------------------------------------------------

    test_solution = """
    Dynamic pressure is calculated using:

    q = rho * V^2

    q = 1.225 * 50^2

    q = 3062.5 Pa

    Therefore, the dynamic pressure is 3062.5 Pa.
    """


    # --------------------------------------------------
    # STEP 5: EXTRACT CANDIDATE FINAL ANSWER
    # --------------------------------------------------

    extracted_answer = extract_final_answer(
        test_solution
    )

    print("\nExtracted answer:")

    print(
        extracted_answer["value"],
        extracted_answer["unit"]
    )


    # --------------------------------------------------
    # STEP 6: RUN DETERMINISTIC NUMERICAL CHECK
    # --------------------------------------------------

    numerical_evaluation = evaluate_numerical_answer(
        expected=problem["expected_answer"],
        candidate=extracted_answer["value"],
        tolerance=2,
    )


    # --------------------------------------------------
    # STEP 7: DISPLAY NUMERICAL EVALUATION
    # --------------------------------------------------

    print("\nNumerical evaluation:")

    print(numerical_evaluation)