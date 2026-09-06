"""
components/progress.py
------------------------
Helpers for computing and rendering progress: module completion screens,
final-assessment scoring, and growth summaries used on Home and My Growth.
"""

from __future__ import annotations

import streamlit as st

from components import ui
from config import settings
from modules import module_registry
from services import supabase_service as db


def score_assessment(questions: list[dict], answers: dict[str, int]) -> dict:
    """answers: {question_id: chosen_option_index}"""
    total = len(questions)
    correct = 0
    for q in questions:
        if answers.get(q["id"]) == q["correct_index"]:
            correct += 1
    percentage = round((correct / total) * 100, 1) if total else 0.0
    passed = percentage >= settings.PASS_PERCENTAGE
    return {"score": correct, "total": total, "percentage": percentage, "passed": passed}


def render_final_assessment(teacher_id: str, module_id: str, module_name: str, questions: list[dict], next_module_id: str | None) -> bool:
    """Renders the final assessment. Returns True once the teacher has passed
    and the module is marked completed."""
    ui.card_open()
    st.markdown('<div class="pd-eyebrow">Final Assessment</div>', unsafe_allow_html=True)
    st.subheader(f"Check Your Understanding: {module_name}")
    st.caption(f"You'll need {settings.PASS_PERCENTAGE}% or higher to complete this module. You can retake it if needed.")
    ui.card_close()

    answers_key = f"assessment_answers_{module_id}"
    if answers_key not in st.session_state:
        st.session_state[answers_key] = {}

    with st.form(key=f"assessment_form_{module_id}"):
        for i, q in enumerate(questions):
            ui.card_open()
            st.markdown(f"**{i + 1}. {q['prompt']}**")
            choice = st.radio(
                "Choose one:", options=list(range(len(q["options"]))),
                format_func=lambda idx, opts=q["options"]: opts[idx],
                key=f"aq_{module_id}_{q['id']}", index=None, label_visibility="collapsed",
            )
            st.session_state[answers_key][q["id"]] = choice
            ui.card_close()

        submitted = st.form_submit_button("Submit Assessment", type="primary")

    if not submitted:
        return False

    answers = st.session_state[answers_key]
    if any(v is None for v in answers.values()):
        st.warning("Please answer every question before submitting.")
        return False

    result = score_assessment(questions, answers)
    db.save_assessment({
        "teacher_id": teacher_id,
        "module_id": module_id,
        "score": result["score"],
        "percentage": result["percentage"],
        "passed": result["passed"],
        "answers_json": answers,
    })

    if result["passed"]:
        db.upsert_progress(teacher_id, module_id, {
            "module_status": "completed",
            "progress_percent": 100,
            "completed_at": db.now(),
        })
        st.session_state[f"just_completed_{module_id}"] = result
        st.rerun()
    else:
        st.error(
            f"You scored {result['percentage']}%, just under the {settings.PASS_PERCENTAGE}% needed to "
            "complete this module. Take a moment to review, then try again — this isn't a one-shot test."
        )
        del st.session_state[answers_key]
    return False


def render_module_completion(teacher_id: str, module_id: str, module_name: str, next_module_id: str | None) -> None:
    result = st.session_state.get(f"just_completed_{module_id}")
    reflections = db.get_reflections(teacher_id, module_id)
    latest_reflection = reflections[0] if reflections else None

    ui.card_open(highlight=True)
    st.markdown("### 🎉 Module Completed")
    st.write(f"You've completed **{module_name}**.")
    ui.card_close()

    ui.card_open()
    st.markdown("**Learning Summary**")
    st.write("You worked through all learning sessions and the six-part lesson planning framework.")

    if latest_reflection:
        st.markdown("**Reflection Summary**")
        st.write(
            f"Topic: {latest_reflection.get('lesson_topic', 'Not mentioned')} · "
            f"Grade: {latest_reflection.get('lesson_grade', 'Not mentioned')}"
        )

    if result:
        st.markdown("**Assessment Score**")
        st.write(f"{result['score']} / {result['total']} correct ({result['percentage']}%)")

    if latest_reflection and latest_reflection.get("ai_feedback"):
        st.markdown("**Key Growth Area**")
        st.write(latest_reflection["ai_feedback"].get("think_about", "Keep reflecting regularly on your lessons."))
    ui.card_close()

    next_module = module_registry.get_module(next_module_id) if next_module_id else None
    if next_module:
        ui.card_open()
        st.markdown("**Next Recommended Module**")
        st.write(f"{next_module['name']} — {next_module['description']}")
        if next_module["status"] == "coming_soon":
            st.caption("Coming soon.")
        ui.card_close()


def render_growth_summary_card(teacher_id: str) -> None:
    stats = db.get_growth_stats(teacher_id)
    ui.card_open()
    st.markdown('<div class="pd-eyebrow">My Progress</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Modules Completed", stats["modules_completed"])
        st.metric("Reflections Completed", stats["reflections_completed"])
    with col2:
        st.metric("Modules In Progress", stats["modules_in_progress"])
        avg = stats["assessment_average"]
        st.metric("Assessment Average", f"{avg}%" if avg is not None else "—")

    st.markdown(
        f'<p class="pd-muted" style="margin-top:0.5rem;">{ui.growth_message(stats["modules_completed"], stats["reflections_completed"])}</p>',
        unsafe_allow_html=True,
    )
    ui.card_close()
