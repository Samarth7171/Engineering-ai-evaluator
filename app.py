from models.evaluation import Evaluation


test_evaluation = Evaluation(
    problem_understanding="Correct",
    approach="Partially correct",
    equations="Incorrect",
    calculations="Correct based on the equation used",
    units="Correct",
    assumptions="Acceptable",
    physical_plausibility="Incorrect result due to formula error",
    final_answer="Incorrect",
    explanation_quality="Clear but technically incorrect",
    errors=[
        "Dynamic pressure equation is missing the 1/2 factor.",
        "Final answer is twice the correct value."
    ],
    corrected_solution="q = 0.5 × 1.225 × 50² = 1531.25 Pa",
    summary="The method is reasonable, but the governing equation is incorrect."
)

print(test_evaluation)