import json

from evaluator.deterministic_checks import evaluate_numerical_answer


# Load our engineering benchmark
with open("benchmark/questions.json", "r") as file:
    benchmark_data = json.load(file)


# Select the first benchmark problem
problem = benchmark_data[0]


# Imagine this answer came from an AI
candidate_answer = 3062.50


# Evaluate the AI answer
result = evaluate_numerical_answer(
    expected=problem["expected_answer"],
    candidate=candidate_answer,
    tolerance=2,
)


print("Question:")
print(problem["question"])

print("\nExpected Answer:")
print(problem["expected_answer"], problem["expected_unit"])

print("\nCandidate Answer:")
print(candidate_answer, problem["expected_unit"])

print("\nEvaluation:")
print(result)