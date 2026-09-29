import streamlit as st

from evaluator.llm_evaluator import evaluate_solution


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

    errors = reasoning.get("errors", [])

    if errors:
        st.subheader("❌ Identified Errors")

        for error in errors:
            st.write(f"• {error}")

    else:
        st.success(
            "No major reasoning errors were identified."
        )

    st.subheader("🔍 Detailed Evaluation")

    sections = {
        "Problem Understanding": "problem_understanding",
        "Approach": "approach",
        "Equations": "equations",
        "Calculations": "calculations",
        "Units": "units",
        "Assumptions": "assumptions",
        "Physical Plausibility": "physical_plausibility",
        "Final Answer": "final_answer",
        "Explanation Quality": "explanation_quality",
    }

    for title, key in sections.items():

        with st.expander(title):

            st.write(
                reasoning.get(
                    key,
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
    "The evaluator uses LLM-based engineering reasoning "
    "because no trusted reference answer is supplied."
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

evaluate_button = st.button(
    "Evaluate Solution",
    type="primary",
)

if evaluate_button:

    if not question.strip():

        st.warning(
            "Please enter an engineering problem."
        )

    elif not candidate_solution.strip():

        st.warning(
            "Please enter an AI-generated solution."
        )

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

            st.divider()

            st.header(
                "Engineering Evaluation"
            )

            st.caption(
                "Extracted final answer: "
                f"{extracted['value']} "
                f"{extracted['unit']}"
            )

            display_reasoning_evaluation(
                reasoning
            )

        except Exception as error:

            st.error(
                "The evaluation could not be completed."
            )

            st.write("Technical error:")

            st.code(str(error))
