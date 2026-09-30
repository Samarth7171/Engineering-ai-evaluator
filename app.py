import math

import streamlit as st

from evaluator.deterministic_checks import (
    evaluate_numerical_answer,
    evaluate_unit,
)
from evaluator.llm_evaluator import EvaluationError, evaluate_solution


st.set_page_config(
    page_title="Engineering AI Evaluator",
    page_icon="⚙️",
    layout="wide",
)


st.markdown(
    """
    <style>
        :root {
            --ink: #edf2f7;
            --muted: #91a0b5;
            --line: rgba(145, 160, 181, 0.18);
            --line-strong: rgba(214, 144, 56, 0.36);
            --surface: rgba(9, 19, 32, 0.78);
            --surface-strong: rgba(12, 25, 42, 0.94);
            --canvas: #050b13;
            --accent: #d78a35;
            --accent-bright: #f0a74f;
        }

        .stApp {
            background-color: var(--canvas);
            background-image:
                radial-gradient(
                    circle at 77% -8%,
                    rgba(215, 138, 53, 0.11),
                    transparent 30rem
                ),
                radial-gradient(
                    circle at 14% 8%,
                    rgba(58, 96, 138, 0.14),
                    transparent 34rem
                ),
                radial-gradient(
                    circle at 1px 1px,
                    rgba(181, 199, 220, 0.07) 0.7px,
                    transparent 0.8px
                ),
                linear-gradient(
                    rgba(93, 116, 145, 0.025) 1px,
                    transparent 1px
                ),
                linear-gradient(
                    90deg,
                    rgba(93, 116, 145, 0.025) 1px,
                    transparent 1px
                );
            background-size: auto, auto, 72px 72px, 48px 48px, 48px 48px;
            color: var(--ink);
        }

        .block-container {
            max-width: 1240px;
            padding-top: 1.65rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            color: var(--ink);
            letter-spacing: -0.015em;
        }

        h1 {
            font-size: 2rem !important;
            margin-bottom: 0.2rem !important;
        }

        h2 {
            font-size: 1.45rem !important;
            margin-top: 1.5rem !important;
        }

        h3 {
            font-size: 1.08rem !important;
        }

        [data-testid="stCaptionContainer"] {
            color: var(--muted);
        }

        p, li, label {
            color: #d7e0ea;
        }

        hr {
            border-color: var(--line) !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--surface);
            border-color: var(--line) !important;
            border-radius: 0.4rem;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
        }

        [data-testid="stExpander"] {
            background: var(--surface);
            border-color: var(--line) !important;
            border-radius: 0.4rem;
        }

        [data-testid="stExpander"] summary p,
        [data-testid="stWidgetLabel"] p {
            color: #dce5ef !important;
            font-weight: 600;
        }

        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input,
        [data-baseweb="select"] > div {
            background: rgba(4, 11, 20, 0.84) !important;
            border-color: rgba(137, 158, 184, 0.24) !important;
            color: #edf2f7 !important;
            border-radius: 0.3rem !important;
        }

        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stTextInput"] input:focus {
            border-color: rgba(215, 138, 53, 0.72) !important;
            box-shadow: 0 0 0 1px rgba(215, 138, 53, 0.22) !important;
        }

        [data-testid="stTextArea"] textarea::placeholder,
        [data-testid="stTextInput"] input::placeholder {
            color: #66768a !important;
        }

        .stButton > button[kind="primary"] {
            background: var(--accent);
            border-color: var(--accent);
            color: #130d06;
            border-radius: 0.3rem;
            font-weight: 760;
            letter-spacing: 0.055em;
            min-height: 2.8rem;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--accent-bright);
            border-color: var(--accent-bright);
            color: #130d06;
        }

        [data-testid="stMetric"] {
            min-height: 6rem;
            padding: 0.8rem 0.85rem;
            background: rgba(4, 12, 21, 0.72);
            border: 1px solid var(--line);
            border-radius: 0.3rem;
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.065em;
        }

        [data-testid="stMetricValue"] {
            color: #f2f5f8;
        }

        [data-testid="stAlert"] {
            background: rgba(10, 23, 38, 0.92);
            border-color: var(--line) !important;
            color: #dce5ef;
        }

        .mission-header {
            position: relative;
            overflow: hidden;
            min-height: 10rem;
            padding: 1.5rem 1.7rem;
            border: 1px solid var(--line);
            border-top: 2px solid rgba(215, 138, 53, 0.62);
            border-radius: 0.45rem;
            background:
                linear-gradient(
                    105deg,
                    rgba(12, 26, 44, 0.96),
                    rgba(5, 13, 24, 0.78)
                );
        }

        .mission-header::before {
            content: "";
            position: absolute;
            width: 25rem;
            height: 8rem;
            right: -6rem;
            top: 0.7rem;
            border: 1px solid rgba(215, 138, 53, 0.18);
            border-radius: 50%;
            transform: rotate(-11deg);
            pointer-events: none;
        }

        .mission-header::after {
            content: "";
            position: absolute;
            width: 14rem;
            right: 1.4rem;
            top: 4.7rem;
            border-top: 1px solid rgba(142, 165, 192, 0.18);
            box-shadow: 4rem -1.6rem 0 -0.5px rgba(215, 138, 53, 0.3);
            transform: rotate(-11deg);
            pointer-events: none;
        }

        .mission-kicker {
            position: relative;
            z-index: 1;
            color: #d78a35;
            font-size: 0.7rem;
            font-weight: 760;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        .mission-title-row {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 0.55rem 0 0.35rem;
        }

        .mission-title {
            margin: 0;
            color: #f4f7fa;
            font-size: clamp(1.65rem, 3vw, 2.5rem);
            font-weight: 720;
            letter-spacing: 0.025em;
        }

        .mission-subtitle {
            position: relative;
            z-index: 1;
            max-width: 47rem;
            margin: 0;
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .product-badge {
            display: inline-block;
            padding: 0.3rem 0.58rem;
            border: 1px solid rgba(215, 138, 53, 0.38);
            border-radius: 999px;
            background: rgba(215, 138, 53, 0.08);
            color: #e4a155;
            font-size: 0.68rem;
            font-weight: 760;
            letter-spacing: 0.08em;
            white-space: nowrap;
        }

        .section-label {
            color: #d78a35;
            font-size: 0.67rem;
            font-weight: 760;
            letter-spacing: 0.15em;
            margin-bottom: -0.7rem;
            text-transform: uppercase;
        }

        .panel-id {
            margin-bottom: 0.35rem;
            color: #8292a7;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .analysis-band {
            margin: 1.65rem 0 0.7rem;
            padding: 0.55rem 0.7rem;
            border-left: 2px solid var(--accent);
            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
            color: #aebdce;
            background: rgba(8, 18, 31, 0.54);
            font-size: 0.68rem;
            font-weight: 760;
            letter-spacing: 0.14em;
        }

        .status-badge {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.04em;
        }

        .status-correct {
            background: rgba(49, 160, 102, 0.16);
            border: 1px solid rgba(72, 187, 120, 0.28);
            color: #78d6a5;
        }

        .status-partially-correct {
            background: rgba(215, 138, 53, 0.15);
            border: 1px solid rgba(215, 138, 53, 0.3);
            color: #edaa5f;
        }

        .status-incorrect {
            background: rgba(181, 75, 75, 0.17);
            border: 1px solid rgba(205, 94, 94, 0.3);
            color: #e08a8a;
        }

        .status-not-applicable {
            background: rgba(126, 142, 162, 0.13);
            border: 1px solid rgba(126, 142, 162, 0.22);
            color: #a6b1bf;
        }

        .issue-label {
            color: #d9903e;
            font-size: 0.75rem;
            font-weight: 750;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 1.25rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .mission-header::before,
            .mission-header::after {
                opacity: 0.45;
            }

            .mission-title-row {
                align-items: flex-start;
                flex-direction: column;
                gap: 0.5rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


DIMENSION_LABELS = {
    "problem_understanding": "Problem Understanding",
    "engineering_method": "Engineering Method",
    "mathematical_execution": "Mathematical Execution",
    "engineering_validity": "Engineering Validity",
    "final_response_quality": "Final Response Quality",
}

STATUS_LABELS = {
    "correct": "CORRECT",
    "partially_correct": "PARTIALLY CORRECT",
    "incorrect": "INCORRECT",
    "not_applicable": "NOT APPLICABLE",
}

STATUS_CLASSES = {
    "correct": "status-correct",
    "partially_correct": "status-partially-correct",
    "incorrect": "status-incorrect",
    "not_applicable": "status-not-applicable",
}


def humanize_category(category):
    return DIMENSION_LABELS.get(
        category,
        category.replace("_", " ").title(),
    )


def display_status_badge(status):
    label = STATUS_LABELS.get(
        status,
        status.replace("_", " ").upper(),
    )
    css_class = STATUS_CLASSES.get(status, "status-not-applicable")

    st.markdown(
        f'<span class="status-badge {css_class}">{label}</span>',
        unsafe_allow_html=True,
    )


def display_reasoning_evaluation(reasoning):
    st.markdown(
        '<div class="section-label">Assessment</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Overall Assessment")

    with st.container(border=True):
        st.write(
            reasoning.get(
                "summary",
                "No summary was returned.",
            )
        )

    errors = reasoning.get("errors", [])

    st.markdown(
        '<div class="section-label">Issue Detection</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Identified Issues")

    if errors:
        for error in errors:
            category_label = humanize_category(
                error.get("category", "")
            )

            with st.container(border=True):
                st.markdown(
                    '<div class="issue-label">Issue</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{category_label}**")
                st.write(error.get("description", ""))
                st.caption("Why it matters")
                st.write(error.get("why_it_matters", ""))

    else:
        st.success("No major reasoning errors were identified.")

    st.markdown(
        '<div class="section-label">Rubric</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Rubric Evaluation")

    rubric = reasoning.get("rubric", {})

    for key, title in DIMENSION_LABELS.items():
        dimension = rubric.get(key, {})
        status = dimension.get("status", "")

        with st.expander(title):
            display_status_badge(status)
            st.write(
                dimension.get(
                    "explanation",
                    "No evaluation available.",
                )
            )


def display_deterministic_verification(
    expected_value,
    expected_unit,
    extracted,
):
    st.markdown(
        '<div class="analysis-band">DETERMINISTIC VERIFICATION</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-label">Deterministic Check</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Deterministic Verification")
    st.info("Uses only the trusted reference supplied by the user.")

    if expected_value is not None:
        st.markdown("#### Numerical comparison")

        candidate_value = extracted.get("value")
        has_numerical_answer = extracted.get(
            "has_numerical_answer",
            False,
        )

        if has_numerical_answer and candidate_value is not None:
            numerical_check = evaluate_numerical_answer(
                expected=expected_value,
                candidate=candidate_value,
                tolerance=2,
            )

            percentage_error = numerical_check["percentage_error"]
            percentage_text = (
                "N/A"
                if percentage_error is None
                else f"{percentage_error:.2f}%"
            )
            result_text = (
                "PASS"
                if numerical_check["within_tolerance"]
                else "FAIL"
            )

            metric_columns = st.columns(6)
            metric_columns[0].metric(
                "Expected",
                numerical_check["expected"],
            )
            metric_columns[1].metric(
                "Candidate",
                numerical_check["candidate"],
            )
            metric_columns[2].metric(
                "Absolute Error",
                numerical_check["absolute_error"],
            )
            metric_columns[3].metric(
                "Percentage Error",
                percentage_text,
            )
            metric_columns[4].metric("Tolerance", "2%")
            metric_columns[5].metric("Result", result_text)

            if numerical_check["within_tolerance"]:
                st.success("PASS — Within the current 2% MVP tolerance.")
            else:
                st.error("FAIL — Outside the current 2% MVP tolerance.")

        else:
            st.info(
                "Numerical comparison could not be performed because "
                "the candidate did not have an extracted numerical answer."
            )

        st.caption(
            "The current MVP uses a 2% numerical tolerance. "
            "This is not a universal engineering standard."
        )

    if expected_unit is not None:
        st.markdown("#### Unit comparison")

        candidate_unit = extracted.get("unit")

        if (
            isinstance(candidate_unit, str)
            and candidate_unit.strip()
        ):
            unit_check = evaluate_unit(
                expected_unit=expected_unit,
                candidate_unit=candidate_unit,
            )
            result_text = (
                "MATCH" if unit_check["units_match"] else "MISMATCH"
            )

            unit_columns = st.columns(3)
            unit_columns[0].metric(
                "Expected Unit",
                unit_check["expected_unit"],
            )
            unit_columns[1].metric(
                "Candidate Unit",
                unit_check["candidate_unit"],
            )
            unit_columns[2].metric("Result", result_text)

            if unit_check["units_match"]:
                st.success("MATCH — Units match.")
            else:
                st.error("MISMATCH — Units do not match.")

        else:
            st.info(
                "Unit comparison could not be performed because the "
                "candidate did not have an extracted unit."
            )

        st.caption(
            "Equivalent unit expressions and unit conversions are not "
            "fully recognized in the current MVP."
        )


def display_corrected_solution(reasoning):
    st.markdown(
        '<div class="section-label">Corrected Solution</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Corrected / Improved Solution")

    with st.container(border=True):
        st.write(
            reasoning.get(
                "corrected_solution",
                "No corrected solution was returned.",
            )
        )
        st.caption(
            "This solution is AI-generated and should not be treated "
            "as independently verified ground truth."
        )


st.markdown(
    """
    <section class="mission-header">
        <div class="mission-kicker">
            Engineering Intelligence / Evaluation System
        </div>
        <div class="mission-title-row">
            <h1 class="mission-title">ENGINEERING AI EVALUATOR</h1>
            <span class="product-badge">MVP • RUBRIC V1</span>
        </div>
        <p class="mission-subtitle">
            Structured evaluation of engineering solutions using AI reasoning
            and deterministic verification.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.markdown(
    '<div class="section-label">Mission Input / Configuration</div>',
    unsafe_allow_html=True,
)
st.subheader("Engineering Evaluation")

st.markdown(
    '<div class="panel-id">Configuration / Domain</div>',
    unsafe_allow_html=True,
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

problem_column, solution_column = st.columns(2, gap="large")

with problem_column:
    st.markdown(
        '<div class="panel-id">01 / Problem</div>',
        unsafe_allow_html=True,
    )
    question = st.text_area(
        "Engineering Problem",
        placeholder="Enter the engineering problem here...",
        height=260,
    )
    st.caption(
        "Include the known quantities, assumptions, and requested result."
    )

with solution_column:
    st.markdown(
        '<div class="panel-id">02 / Candidate Solution</div>',
        unsafe_allow_html=True,
    )
    candidate_solution = st.text_area(
        "Candidate / AI Solution",
        placeholder="Paste the candidate engineering solution here...",
        height=260,
    )
    st.caption(
        "The candidate solution may come from a student or an AI system."
    )

with st.expander("Trusted Reference — Optional"):
    st.caption(
        "Provide a verified expected value/unit if available. These values "
        "are used only for deterministic comparison and are not sent to "
        "the LLM."
    )

    expected_value_column, expected_unit_column = st.columns(2)

    with expected_value_column:
        expected_value_input = st.text_input(
            "Expected numerical value",
            placeholder="Example: 1531.25",
        )

    with expected_unit_column:
        expected_unit_input = st.text_input(
            "Expected unit",
            placeholder="Example: Pa",
        )

action_spacer, action_column = st.columns([3, 1])

with action_column:
    evaluate_button = st.button(
        "RUN EVALUATION",
        type="primary",
        use_container_width=True,
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
        st.warning("Please enter an engineering problem.")
    elif not candidate_solution.strip():
        st.warning("Please enter a candidate or AI-generated solution.")
    elif expected_value_error:
        st.warning(expected_value_error)
    else:
        try:
            with st.spinner("Evaluating engineering solution..."):
                result = evaluate_solution(
                    question=question,
                    candidate_solution=candidate_solution,
                    domain=domain,
                )

            reasoning = result["reasoning_evaluation"]
            extracted = result["extracted_answer"]

            st.divider()
            st.markdown(
                '<div class="section-label">Analysis / Result</div>',
                unsafe_allow_html=True,
            )
            st.header("Evaluation Result")

            if extracted["has_numerical_answer"]:
                answer_text = str(extracted["value"])

                if extracted.get("unit"):
                    answer_text += f" {extracted['unit']}"

                with st.container(border=True):
                    st.metric("Extracted final answer", answer_text)
                    st.caption(
                        "Candidate answer extracted by the evaluator; "
                        "not a trusted reference value."
                    )
            else:
                st.info("No numerical final answer detected.")

            st.markdown(
                '<div class="analysis-band">AI REASONING EVALUATION</div>',
                unsafe_allow_html=True,
            )
            display_reasoning_evaluation(reasoning)

            if has_trusted_reference:
                st.divider()
                display_deterministic_verification(
                    expected_value=expected_value,
                    expected_unit=expected_unit,
                    extracted=extracted,
                )

            st.divider()
            display_corrected_solution(reasoning)

        except EvaluationError:
            st.error(
                "The evaluation could not be completed. "
                "Please retry in a moment."
            )
