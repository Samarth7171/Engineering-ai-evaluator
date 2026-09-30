import math

import streamlit as st

from evaluator.deterministic_checks import (
    evaluate_numerical_answer,
    evaluate_unit,
)
from evaluator.llm_evaluator import EvaluationError, evaluate_solution


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Engineering AI Evaluator",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Engineering AI Evaluator")

st.write(
    "Evaluate AI-generated engineering solutions for reasoning, "
    "equations, calculations, units, assumptions, and physical plausibility."
)

st.divider()


# ==================================================
# SHARED FUNCTION
# ==================================================

def display_reasoning_evaluation(reasoning):
    """
    Display the LLM engineering reasoning evaluation.

    Used by Engineering Evaluation to present the
    structured reasoning result.
    """

    st.subheader("📋 Overall Summary")

    st.write(
        reasoning.get(
            "summary",
            "No summary was returned.",
        )
    )

    dimension_labels = {
        "problem_understanding": "Problem Understanding",
        "engineering_method": "Engineering Method",
        "mathematical_execution": "Mathematical Execution",
        "engineering_validity": "Engineering Validity",
        "final_response_quality": "Final Response Quality",
    }

    status_labels = {
        "correct": "Correct",
        "partially_correct": "Partially Correct",
        "incorrect": "Incorrect",
        "not_applicable": "Not Applicable",
    }

    errors = reasoning.get("errors", [])

    if errors:
        st.subheader("❌ Identified Errors")

        for error in errors:
            category = error.get("category", "")
            category_label = dimension_labels.get(
                category,
                category.replace("_", " ").title(),
            )

            st.markdown(f"**{category_label}**")
            st.write(error.get("description", ""))
            st.write(
                "**Why it matters:** "
                f"{error.get('why_it_matters', '')}"
            )

    else:
        st.success(
            "No major reasoning errors were identified."
        )

    st.subheader("🔍 Detailed Evaluation")

    rubric = reasoning.get("rubric", {})

    for key, title in dimension_labels.items():

        dimension = rubric.get(key, {})
        status = dimension.get("status", "")
        status_label = status_labels.get(
            status,
            status.replace("_", " ").title(),
        )

        with st.expander(title):

            st.write(f"**Status:** {status_label}")

            st.write(
                dimension.get(
                    "explanation",
                    "No evaluation available.",
                )
            )

    st.subheader("✅ Corrected / Improved Solution")

    st.write(
        reasoning.get(
            "corrected_solution",
            "No corrected solution was returned.",
        )
    )


# ==================================================
# ENGINEERING EVALUATION
# ==================================================

st.subheader("Engineering Evaluation")

st.caption(
    "Evaluate any engineering problem. "
    "Optionally provide trusted reference values for "
    "deterministic verification."
)

domain = st.selectbox(
    "Engineering Domain",
    [
        "Fluid Mechanics",
        "Aerodynamics",
        "Thermodynamics",
        "Engineering Mathematics",
        "Basic Propulsion",
    ],
)

question = st.text_area(
    "Engineering Problem",
    placeholder="Enter the engineering problem here...",
    height=150,
)

candidate_solution = st.text_area(
    "AI-Generated Solution",
    placeholder="Paste the AI-generated solution here...",
    height=250,
)

st.subheader("Trusted Reference (Optional)")

st.caption(
    "Use values from a trusted source, such as a verified solution, "
    "textbook, instructor solution, or known reference—not from the "
    "evaluator itself. Leave both fields blank if no trusted reference "
    "is available."
)

expected_value_input = st.text_input(
    "Optional expected numerical value",
    placeholder="Example: 1531.25",
)

expected_unit_input = st.text_input(
    "Optional expected unit",
    placeholder="Example: Pa",
)

evaluate_button = st.button(
    "Evaluate Solution",
    type="primary",
)

if evaluate_button:

    expected_value_text = expected_value_input.strip()
    expected_unit = expected_unit_input.strip() or None
    expected_value = None
    expected_value_error = None

    if expected_value_text:

        try:
            expected_value = float(expected_value_text)

        except ValueError:
            expected_value_error = (
                "Enter a valid finite number for the optional "
                "expected numerical value."
            )

        else:
            if not math.isfinite(expected_value):
                expected_value_error = (
                    "Enter a valid finite number for the optional "
                    "expected numerical value."
                )

    has_trusted_reference = bool(
        expected_value_text or expected_unit
    )

    if not question.strip():

        st.warning(
            "Please enter an engineering problem."
        )

    elif not candidate_solution.strip():

        st.warning(
            "Please enter an AI-generated solution."
        )

    elif expected_value_error:

        st.warning(expected_value_error)

    else:

        try:

            with st.spinner(
                "Evaluating engineering solution..."
            ):

                result = evaluate_solution(
                    question=question,
                    candidate_solution=candidate_solution,
                    domain=domain,
                )

            reasoning = result[
                "reasoning_evaluation"
            ]

            extracted = result[
                "extracted_answer"
            ]

            has_numerical_answer = extracted[
                "has_numerical_answer"
            ]

            st.divider()

            st.header(
                "Engineering Evaluation"
            )

            if has_numerical_answer:

                st.caption(
                    "Extracted final answer: "
                    f"{extracted['value']} "
                    f"{extracted['unit']}"
                )

            else:

                st.caption(
                    "No numerical final answer detected — "
                    "evaluating engineering reasoning."
                )

            display_reasoning_evaluation(
                reasoning
            )

            if has_trusted_reference:

                st.divider()

                st.subheader(
                    "Trusted Reference Verification — Deterministic"
                )

                st.caption(
                    "Only the expected value and unit supplied by you "
                    "are treated as trusted. The candidate answer was "
                    "extracted by the evaluator and is not trusted "
                    "ground truth."
                )

                if expected_value is not None:

                    st.markdown("**Numerical Verification**")

                    st.caption(
                        "The current MVP uses a default 2% tolerance. "
                        "This is not a universal engineering standard."
                    )

                    candidate_value = extracted.get("value")

                    if (
                        has_numerical_answer
                        and candidate_value is not None
                    ):

                        numerical_check = evaluate_numerical_answer(
                            expected=expected_value,
                            candidate=candidate_value,
                            tolerance=2,
                        )

                        st.write(
                            "Trusted expected value: "
                            f"{numerical_check['expected']}"
                        )

                        st.write(
                            "Extracted candidate value: "
                            f"{numerical_check['candidate']}"
                        )

                        st.write(
                            "Absolute error: "
                            f"{numerical_check['absolute_error']}"
                        )

                        percentage_error = numerical_check[
                            "percentage_error"
                        ]

                        if percentage_error is None:
                            st.write(
                                "Percentage error: Not available when "
                                "the trusted expected value is zero."
                            )

                        else:
                            st.write(
                                "Percentage error: "
                                f"{percentage_error:.2f}%"
                            )

                        if numerical_check["within_tolerance"]:
                            st.success(
                                "PASS — Within the current 2% "
                                "MVP tolerance."
                            )

                        else:
                            st.error(
                                "FAIL — Outside the current 2% "
                                "MVP tolerance."
                            )

                    else:
                        st.info(
                            "Numerical comparison could not be "
                            "performed because the candidate did not "
                            "have an extracted numerical answer."
                        )

                if expected_unit is not None:

                    st.markdown("**Unit Verification**")

                    st.caption(
                        "The current MVP performs normalized string "
                        "comparison and does not yet recognize all "
                        "physically equivalent units or conversions."
                    )

                    candidate_unit = extracted.get("unit")

                    if (
                        isinstance(candidate_unit, str)
                        and candidate_unit.strip()
                    ):

                        unit_check = evaluate_unit(
                            expected_unit=expected_unit,
                            candidate_unit=candidate_unit,
                        )

                        st.write(
                            "Trusted expected unit: "
                            f"{unit_check['expected_unit']}"
                        )

                        st.write(
                            "Extracted candidate unit: "
                            f"{unit_check['candidate_unit']}"
                        )

                        if unit_check["units_match"]:
                            st.success("MATCH — Units match.")

                        else:
                            st.error("MISMATCH — Units do not match.")

                    else:
                        st.info(
                            "Unit comparison could not be performed "
                            "because the candidate did not have an "
                            "extracted unit."
                        )

        except EvaluationError:

            st.error(
                "The evaluation could not be completed. "
                "Please retry in a moment."
            )
