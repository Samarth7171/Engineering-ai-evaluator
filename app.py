import streamlit as st

from evaluator.llm_evaluator import evaluate_solution


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Engineering AI Evaluator",
    page_icon="⚙️",
    layout="wide",
)


# --------------------------------------------------
# 2. PAGE HEADER
# --------------------------------------------------

st.title("⚙️ Engineering AI Evaluator")

st.write(
    "Evaluate AI-generated engineering solutions for "
    "reasoning, equations, calculations, units, assumptions, "
    "and physical plausibility."
)

st.divider()


# --------------------------------------------------
# 3. DOMAIN SELECTION
# --------------------------------------------------

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


# --------------------------------------------------
# 4. ENGINEERING QUESTION
# --------------------------------------------------

question = st.text_area(
    "Engineering Problem",
    placeholder="Enter the engineering problem here...",
    height=150,
)


# --------------------------------------------------
# 5. CANDIDATE SOLUTION
# --------------------------------------------------

candidate_solution = st.text_area(
    "AI-Generated Solution",
    placeholder="Paste the AI-generated solution here...",
    height=250,
)


# --------------------------------------------------
# 6. EVALUATE BUTTON
# --------------------------------------------------

evaluate_button = st.button(
    "Evaluate Solution",
    type="primary",
)


# --------------------------------------------------
# 7. RUN EVALUATION
# --------------------------------------------------

if evaluate_button:

    # Make sure a question was entered
    if not question.strip():

        st.warning(
            "Please enter an engineering problem."
        )

    # Make sure a solution was entered
    elif not candidate_solution.strip():

        st.warning(
            "Please enter an AI-generated solution."
        )

    else:

        try:

            # ------------------------------------------
            # CALL OUR AI EVALUATOR
            # ------------------------------------------

            with st.spinner(
                "Evaluating engineering solution..."
            ):

                evaluation = evaluate_solution(
                    question=question,
                    candidate_solution=candidate_solution,
                    domain=domain,
                )


            # ------------------------------------------
            # DEBUG CHECK
            # ------------------------------------------

            if evaluation is None:

                st.error(
                    "The evaluator returned no result."
                )

                st.info(
                    "This means evaluate_solution() returned None. "
                    "The problem is inside llm_evaluator.py, "
                    "not the Streamlit interface."
                )

                st.stop()


            # ------------------------------------------
            # MAKE SURE RESULT IS A DICTIONARY
            # ------------------------------------------

            if not isinstance(evaluation, dict):

                st.error(
                    "The evaluator returned an unexpected result."
                )

                st.write(
                    "Returned value:"
                )

                st.write(evaluation)

                st.stop()


            # ------------------------------------------
            # DISPLAY RESULTS
            # ------------------------------------------

            st.divider()

            st.header(
                "Engineering Evaluation"
            )


            # ------------------------------------------
            # OVERALL SUMMARY
            # ------------------------------------------

            st.subheader(
                "📋 Overall Summary"
            )

            st.write(
                evaluation.get(
                    "summary",
                    "No summary was returned."
                )
            )


            # ------------------------------------------
            # IDENTIFIED ERRORS
            # ------------------------------------------

            st.subheader(
                "❌ Identified Errors"
            )

            errors = evaluation.get(
                "errors",
                []
            )

            if errors:

                for error in errors:

                    st.write(
                        f"• {error}"
                    )

            else:

                st.success(
                    "No major errors were identified."
                )


            # ------------------------------------------
            # DETAILED EVALUATION
            # ------------------------------------------

            st.subheader(
                "🔍 Detailed Evaluation"
            )


            with st.expander(
                "Problem Understanding"
            ):

                st.write(
                    evaluation.get(
                        "problem_understanding",
                        "No evaluation available."
                    )
                )


            with st.expander(
                "Approach"
            ):

                st.write(
                    evaluation.get(
                        "approach",
                        "No evaluation available."
                    )
                )


            with st.expander(
                "Equations"
            ):

                st.write(
                    evaluation.get(
                        "equations",
                        "No evaluation available."
                    )
                )


            with st.expander(
                "Calculations"
            ):

                st.write(
                    evaluation.get(
                        "calculations",
                        "No evaluation available."
                    )
                )


            with st.expander(
                "Units"
            ):

                st.write(
                    evaluation.get(
                        "units",
                        "No evaluation available."
                    )
                )


            with st.expander(
                "Assumptions"
            ):

                st.write(
                    evaluation.get(
                        "assumptions",
                        "No evaluation available."
                    )
                )


            with st.expander(
                "Physical Plausibility"
            ):

                st.write(
                    evaluation.get(
                        "physical_plausibility",
                        "No evaluation available."
                    )
                )


            with st.expander(
                "Final Answer"
            ):

                st.write(
                    evaluation.get(
                        "final_answer",
                        "No evaluation available."
                    )
                )


            with st.expander(
                "Explanation Quality"
            ):

                st.write(
                    evaluation.get(
                        "explanation_quality",
                        "No evaluation available."
                    )
                )


            # ------------------------------------------
            # CORRECTED SOLUTION
            # ------------------------------------------

            st.subheader(
                "✅ Corrected / Improved Solution"
            )

            st.write(
                evaluation.get(
                    "corrected_solution",
                    "No corrected solution was returned."
                )
            )


        # --------------------------------------------------
        # ERROR HANDLING
        # --------------------------------------------------

        except Exception as error:

            st.error(
                "The evaluation could not be completed."
            )

            st.write(
                "Technical error:"
            )

            st.code(
                str(error)
            )