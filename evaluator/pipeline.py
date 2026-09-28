import json
from pathlib import Path

from evaluator.deterministic_checks import evaluate_numerical_answer
from evaluator.llm_evaluator import evaluate_solution


# --------------------------------------------------
# LOAD ONE BENCHMARK PROBLEM
# --------------------------------------------------

def load_benchmark_problem(problem_id):
    """
    Load one engineering problem from the benchmark
    using its unique problem ID.
    """

    project_root = Path(__file__).resolve().parent.parent
    benchmark_path = project_root / "benchmark" / "questions.json"

    with open(
        benchmark_path,
        "r",
        encoding="utf-8"
    ) as file:

        benchmark_data = json.load(file)

    for problem in benchmark_data:

        if problem["id"] == problem_id:
            return problem

    raise ValueError(
        f"Benchmark problem '{problem_id}' was not found."
    )


# --------------------------------------------------
# RUN COMPLETE BENCHMARK EVALUATION
# --------------------------------------------------

def run_benchmark_evaluation(
    problem_id,
    candidate_solution
):
    """
    Run the hybrid engineering evaluation pipeline.

    The LLM performs:
    - final answer extraction
    - engineering reasoning evaluation

    Python performs:
    - deterministic numerical verification
    """

    # --------------------------------------------------
    # STEP 1: LOAD TRUSTED BENCHMARK
    # --------------------------------------------------

    problem = load_benchmark_problem(
        problem_id
    )


    # --------------------------------------------------
    # STEP 2: ONE LLM CALL
    # --------------------------------------------------

    llm_result = evaluate_solution(
        question=problem["question"],
        candidate_solution=candidate_solution,
        domain=problem["domain"],
    )


    # --------------------------------------------------
    # STEP 3: SEPARATE THE TWO LLM OUTPUTS
    # --------------------------------------------------

    extracted_answer = llm_result[
        "extracted_answer"
    ]

    reasoning_evaluation = llm_result[
        "reasoning_evaluation"
    ]


    # --------------------------------------------------
    # STEP 4: DETERMINISTIC PYTHON CHECK
    # --------------------------------------------------

    numerical_check = evaluate_numerical_answer(
        expected=problem["expected_answer"],
        candidate=extracted_answer["value"],
        tolerance=2,
    )


    # --------------------------------------------------
    # STEP 5: COMBINE EVERYTHING
    # --------------------------------------------------

    result = {
        "problem": problem,

        "extracted_answer":
            extracted_answer,

        "numerical_check":
            numerical_check,

        "reasoning_evaluation":
            reasoning_evaluation,
    }

    return result


# --------------------------------------------------
# TEMPORARY DEVELOPMENT TEST
# --------------------------------------------------

if __name__ == "__main__":

    test_solution = """
    Dynamic pressure is calculated using:

    q = rho * V^2

    q = 1.225 * 50^2

    q = 3062.5 Pa

    Therefore, the dynamic pressure is 3062.5 Pa.
    """

    result = run_benchmark_evaluation(
        problem_id="fluid_001",
        candidate_solution=test_solution,
    )


    print("\nExtracted answer:")
    print(
        result["extracted_answer"]
    )


    print("\nDeterministic numerical check:")
    print(
        result["numerical_check"]
    )


    print("\nLLM reasoning summary:")
    print(
        result[
            "reasoning_evaluation"
        ]["summary"]
    )