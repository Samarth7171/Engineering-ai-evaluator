import streamlit as st

from evaluator.llm_evaluator import evaluate_solution
from evaluator.pipeline import (
    load_benchmark_problem,
    run_benchmark_evaluation,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Engineering AI Evaluator",
    page_icon="⚙️",
    layout="wide",
)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("⚙️ Engineering AI Evaluator")

st.write(
    "Evaluate AI-generated engineering solutions for reasoning, "
    "equations, calculations, units, assumptions, and physical plausibility."
)

st.divider()


# --------------------------------------------------
# EVALUATION MODE
# --------------------------------------------------

evaluation_mode = st.radio(
    "Evaluation Mode",
    [
        "Free Evaluation",
        "Benchmark Evaluation",
    ],
    horizontal=True,
)


# ==================================================
# FREE EVALUATION MODE
# ==================================================

if evaluation_mode == "Free Evaluation":

    st.subheader("Free Engineering Evaluation")

    st.caption(
        "Evaluate any engineering problem. "
        "This mode currently uses LLM-based reasoning evaluation."
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

                    evaluation = evaluate_solution(
                        question=question,
                        candidate_solution=candidate_solution,
                        domain=domain,
                    )

                st.divider()

                st.header("Engineering Evaluation")

                # --------------------------------------
                # SUMMARY
                # --------------------------------------

                st.subheader("📋 Overall Summary")

                st.write(
                    evaluation.get(
                        "summary",
                        "No summary was returned.",
                    )
                )


                # --------------------------------------
                # ERRORS
                # --------------------------------------

                st.subheader("❌ Identified Errors")

                errors = evaluation.get(
                    "errors",
                    [],
                )

                if errors:

                    for error in errors:
                        st.write(f"• {error}")

                else:

                    st.success(
                        "No major errors were identified."
                    )


                # --------------------------------------
                # DETAILED EVALUATION
                # --------------------------------------

                st.subheader(
                    "🔍 Detailed Evaluation"
                )

                sections = {
                    "Problem Understanding":
                        "problem_understanding",

                    "Approach":
                        "approach",

                    "Equations":
                        "equations",

                    "Calculations":
                        "calculations",

                    "Units":
                        "units",

                    "Assumptions":
                        "assumptions",

                    "Physical Plausibility":
                        "physical_plausibility",

                    "Final Answer":
                        "final_answer",

                    "Explanation Quality":
                        "explanation_quality",
                }

                for title, key in sections.items():

                    with st.expander(title):

                        st.write(
                            evaluation.get(
                                key,
                                "No evaluation available.",
                            )
                        )


                # --------------------------------------
                # CORRECTED SOLUTION
                # --------------------------------------

                st.subheader(
                    "✅ Corrected / Improved Solution"
                )

                st.write(
                    evaluation.get(
                        "corrected_solution",
                        "No corrected solution was returned.",
                    )
                )


            except Exception as error:

                st.error(
                    "The evaluation could not be completed."
                )

                st.write("Technical error:")

                st.code(str(error))


# ==================================================
# BENCHMARK EVALUATION MODE
# ==================================================

else:

    st.subheader("Benchmark Evaluation")

    st.caption(
        "Evaluate a candidate solution against a trusted "
        "engineering benchmark reference."
    )


    # --------------------------------------------------
    # LOAD BENCHMARK PROBLEM
    # --------------------------------------------------

    try:

        benchmark_problem = load_benchmark_problem(
            "fluid_001"
        )

    except Exception as error:

        st.error(
            "The benchmark problem could not be loaded."
        )

        st.code(str(error))

        st.stop()


    # --------------------------------------------------
    # DISPLAY BENCHMARK INFORMATION
    # --------------------------------------------------

    st.write(
        f"**Domain:** "
        f"{benchmark_problem['domain']}"
    )

    st.write(
        f"**Difficulty:** "
        f"{benchmark_problem['difficulty']}"
    )

    st.write("**Engineering Problem:**")

    st.info(
        benchmark_problem["question"]
    )


    # --------------------------------------------------
    # CANDIDATE SOLUTION
    # --------------------------------------------------

    candidate_solution = st.text_area(
        "Candidate / AI Solution",
        placeholder=(
            "Paste the candidate engineering "
            "solution here..."
        ),
        height=250,
    )


    benchmark_button = st.button(
        "Run Benchmark Evaluation",
        type="primary",
    )


    # --------------------------------------------------
    # RUN HYBRID PIPELINE
    # --------------------------------------------------

    if benchmark_button:

        if not candidate_solution.strip():

            st.warning(
                "Please enter a candidate solution."
            )

        else:

            try:

                with st.spinner(
                    "Running hybrid engineering evaluation..."
                ):

                    result = run_benchmark_evaluation(
                        problem_id="fluid_001",
                        candidate_solution=candidate_solution,
                    )


                reasoning = result[
                    "reasoning_evaluation"
                ]

                numerical = result[
                    "numerical_check"
                ]

                extracted = result[
                    "extracted_answer"
                ]


                # --------------------------------------
                # RESULTS
                # --------------------------------------

                st.divider()

                st.header(
                    "Benchmark Evaluation Results"
                )


                # --------------------------------------
                # NUMERICAL VERIFICATION
                # --------------------------------------

                st.subheader(
                    "🔢 Deterministic Numerical Check"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Expected Answer",
                        (
                            f"{numerical['expected']} "
                            f"{benchmark_problem['expected_unit']}"
                        ),
                    )

                with col2:

                    st.metric(
                        "Extracted Candidate Answer",
                        (
                            f"{extracted['value']} "
                            f"{extracted['unit']}"
                        ),
                    )


                percentage_error = numerical[
                    "percentage_error"
                ]

                if percentage_error is not None:

                    st.write(
                        "**Percentage Error:** "
                        f"{percentage_error:.2f}%"
                    )


                if numerical["within_tolerance"]:

                    st.success(
                        "The numerical answer is within "
                        "the current tolerance."
                    )

                else:

                    st.error(
                        "The numerical answer is outside "
                        "the current tolerance."
                    )


                # --------------------------------------
                # LLM REASONING
                # --------------------------------------

                st.subheader(
                    "🧠 Engineering Reasoning Evaluation"
                )

                st.write(
                    reasoning.get(
                        "summary",
                        "No summary was returned.",
                    )
                )


                # --------------------------------------
                # ERRORS
                # --------------------------------------

                st.subheader(
                    "❌ Identified Errors"
                )

                errors = reasoning.get(
                    "errors",
                    [],
                )

                if errors:

                    for error in errors:
                        st.write(f"• {error}")

                else:

                    st.success(
                        "No major reasoning errors "
                        "were identified."
                    )


                # --------------------------------------
                # DETAILED EVALUATION
                # --------------------------------------

                st.subheader(
                    "🔍 Detailed Evaluation"
                )

                sections = {
                    "Problem Understanding":
                        "problem_understanding",

                    "Approach":
                        "approach",

                    "Equations":
                        "equations",

                    "Calculations":
                        "calculations",

                    "Units":
                        "units",

                    "Assumptions":
                        "assumptions",

                    "Physical Plausibility":
                        "physical_plausibility",

                    "Final Answer":
                        "final_answer",

                    "Explanation Quality":
                        "explanation_quality",
                }

                for title, key in sections.items():

                    with st.expander(title):

                        st.write(
                            reasoning.get(
                                key,
                                "No evaluation available.",
                            )
                        )


                # --------------------------------------
                # CORRECTED SOLUTION
                # --------------------------------------

                st.subheader(
                    "✅ Corrected / Improved Solution"
                )

                st.write(
                    reasoning.get(
                        "corrected_solution",
                        "No corrected solution was returned.",
                    )
                )


            except Exception as error:

                st.error(
                    "The benchmark evaluation "
                    "could not be completed."
                )

                st.write("Technical error:")

                st.code(str(error))