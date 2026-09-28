import json
from pathlib import Path

from evaluator.answer_extractor import extract_final_answer
from evaluator.deterministic_checks import evaluate_numerical_answer
from evaluator.llm_evaluator import evaluate_solution


def load_benchmark_problem(problem_id):
    """
    Load one engineering problem from the benchmark
    using its unique problem ID.
    """

    project_root = Path(__file__).resolve().parent.parent
    benchmark_path = project_root / "benchmark" / "questions.json"

    with open(benchmark_path, "r", encoding="utf-8") as file:
        benchmark_data = json.load(file)

    for problem in benchmark_data:
        if problem["id"] == problem_id:
            return problem

    raise ValueError(
        f"Benchmark problem '{problem_id}' was not found."
    )


def run_benchmark_evaluation(problem_id, candidate_solution):
    """
    Run the complete evaluation pipeline for one
    benchmark engineering problem.
    """

    # 1. Load trusted benchmark information
    problem = load_benchmark_problem(problem_id)

    # 2. Extract candidate's final numerical answer
    extracted_answer = extract_final_answer(
        candidate_solution
    )

    # 3. Compare candidate number with trusted answer
    numerical_check = evaluate_numerical_answer(
        expected=problem["expected_answer"],
        candidate=extracted_answer["value"],
        tolerance=2,
    )

    # 4. Ask the LLM to evaluate engineering reasoning
    reasoning_evaluation = evaluate_solution(
        question=problem["question"],
        candidate_solution=candidate_solution,
        domain=problem["domain"],
    )

    # 5. Combine everything into one result
    result = {
        "problem": problem,
        "extracted_answer": extracted_answer,
        "numerical_check": numerical_check,
        "reasoning_evaluation": reasoning_evaluation,
    }

    return result


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
    print(result["extracted_answer"])

    print("\nDeterministic numerical check:")
    print(result["numerical_check"])

    print("\nLLM reasoning summary:")
    print(result["reasoning_evaluation"]["summary"])