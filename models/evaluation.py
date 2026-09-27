from dataclasses import dataclass


@dataclass
class Evaluation:
    problem_understanding: str
    approach: str
    equations: str
    calculations: str
    units: str
    assumptions: str
    physical_plausibility: str
    final_answer: str
    explanation_quality: str
    errors: list[str]
    corrected_solution: str
    summary: str