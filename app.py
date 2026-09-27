import json


with open("benchmark/questions.json", "r") as file:
    benchmark_data = json.load(file)


first_problem = benchmark_data[0]

print("Domain:", first_problem["domain"])
print("Question:", first_problem["question"])
print("Expected Answer:", first_problem["expected_answer"])
print("Expected Unit:", first_problem["expected_unit"])