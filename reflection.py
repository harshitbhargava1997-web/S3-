"""
components/reflection.py
--------------------------
Implements the most important feature of the app: the voice reflection flow.

Flow:
    Record / Upload  ->  Transcript  ->  AI-structured extraction
    ->  Teacher edits & confirms  ->  AI pedagogical coaching feedback

The AI never sees its extraction auto-submitted — the teacher always reviews
and confirms first (section 20 of the product spec is treated as mandatory).
"""

from __future__ import annotations

import copy

import streamlit as st

from components import ui
from config import settings, ALLOWED_AUDIO_TYPES
from services import ai_service, r2_service, supabase_service as db, transcription_service


def _state_key(module_id: str, name: str) -> str:
    return f"reflection__{module_id}__{name}"


def _get(module_id: str, name: str, default=None):
    return st.session_state.get(_state_key(module_id, name), default)


def _set(module_id: str, name: str, value) -> None:
    st.session_state[_state_key(module_id, name)] = value


def reset_reflection_state(module_id: str) -> None:
    for name in ["stage", "audio_bytes", "transcript", "extracted", "reflection_id", "feedback"]:
        st.session_state.pop(_state_key(module_id, name), None)


def render_reflection_flow(teacher_id: str, module_id: str, module_name: str, reflection_prompt: str) -> bool:
    """
    Renders whichever step of the reflection flow the teacher is currently on.
    Returns True once AI feedback has been shown and the teacher is ready to
    move on to the Final Assessment.
    """
    stage = _get(module_id, "stage", "record")

    if stage == "record":
        _render_record_stage(module_id, reflection_prompt)
        return False
    if stage == "transcript":
        _render_transcript_stage(teacher_id, module_id)
        return False
    if stage == "edit":
        _render_edit_stage(teacher_id, module_id, module_name)
        return False
    if stage == "feedback":
        return _render_feedback_stage(module_id)

    return False


def _render_record_stage(module_id: str, reflection_prompt: str) -> None:
    ui.card_open()
    st.markdown('<div class="pd-eyebrow">Your Classroom Thinking</div>', unsafe_allow_html=True)
    st.subheader("🎙️ Reflect on a Lesson")
    st.write(reflection_prompt)
    st.caption("Speak naturally. You don't need to write anything. Aim for 1–2 minutes.")

    audio_value = st.audio_input("Record your reflection")

    st.markdown('<p class="pd-muted">or</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload an audio file instead", type=ALLOWED_AUDIO_TYPES)

    audio_bytes = None
    filename = "reflection.wav"

    if audio_value is not None:
        audio_bytes = audio_value.getvalue()
    elif uploaded is not None:
        max_bytes = settings.MAX_AUDIO_MB * 1024 * 1024
        if uploaded.size > max_bytes:
            st.error(f"That file is too large. Please keep uploads under {settings.MAX_AUDIO_MB} MB.")
        else:
            audio_bytes = uploaded.getvalue()
            filename = uploaded.name

    if audio_bytes:
        st.audio(audio_bytes)
        if st.button("Continue with this recording", type="primary"):
            _set(module_id, "audio_bytes", audio_bytes)
            _set(module_id, "filename", filename)
            _set(module_id, "stage", "transcript")
            st.rerun()

    ui.card_close()


def _render_transcript_stage(teacher_id: str, module_id: str) -> None:
    ui.card_open()
    st.markdown('<div class="pd-eyebrow">Step 2 of 4</div>', unsafe_allow_html=True)
    st.subheader("Your Transcript")

    if _get(module_id, "transcript") is None:
        with st.spinner("Converting your reflection into text..."):
            audio_bytes = _get(module_id, "audio_bytes")
            filename = _get(module_id, "filename", "reflection.wav")
            result = transcription_service.transcribe_audio(audio_bytes, filename)
            _set(module_id, "transcript", result["transcript"])
            _set(module_id, "transcript_demo", result["demo"])

    if _get(module_id, "transcript_demo"):
        st.caption("🧪 Demo transcript shown (speech-to-text isn't connected yet).")

    transcript = st.text_area(
        "Here's what we heard. You can correct anything before continuing.",
        value=_get(module_id, "transcript", ""),
        height=200,
    )
    _set(module_id, "transcript", transcript)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Re-record"):
            reset_reflection_state(module_id)
            st.rerun()
    with col2:
        if st.button("Continue", type="primary"):
            with st.spinner("Organizing your thinking into the six-part framework..."):
                audio_meta = r2_service.upload_audio(
                    _get(module_id, "audio_bytes") or b"",
                    teacher_id, module_id, _get(module_id, "filename", "reflection.wav"),
                )
                _set(module_id, "audio_path", audio_meta["path"])

                extraction = ai_service.extract_reflection(transcript)
                _set(module_id, "extracted", extraction["data"])
                _set(module_id, "extraction_demo", extraction["demo"])
            _set(module_id, "stage", "edit")
            st.rerun()

    ui.card_close()


def _render_edit_stage(teacher_id: str, module_id: str, module_name: str) -> None:
    extracted = copy.deepcopy(_get(module_id, "extracted"))

    ui.card_open()
    st.markdown('<div class="pd-eyebrow">Step 3 of 4</div>', unsafe_allow_html=True)
    st.subheader("Here's what I understood from your reflection")
    if _get(module_id, "extraction_demo"):
        st.caption("🧪 Demo extraction shown (AI service isn't connected yet). Feel free to edit freely.")
    st.caption("Please review and correct anything that isn't quite right — nothing is saved until you confirm.")
    ui.card_close()

    ui.card_open()
    st.markdown("**WHAT**")
    c1, c2 = st.columns(2)
    with c1:
        extracted["what"]["grade"] = st.text_input("Grade", extracted["what"].get("grade", ""))
        extracted["what"]["subject"] = st.text_input("Subject", extracted["what"].get("subject", ""))
        extracted["what"]["lesson_plan_number"] = st.text_input("Lesson Plan Number", extracted["what"].get("lesson_plan_number", ""))
    with c2:
        extracted["what"]["topic"] = st.text_input("Topic / Chapter", extracted["what"].get("topic", ""))
        extracted["what"]["book"] = st.text_input("Book / Workbook", extracted["what"].get("book", ""))
        extracted["what"]["page_or_section"] = st.text_input("Page / Section", extracted["what"].get("page_or_section", ""))
    ui.card_close()

    ui.card_open()
    st.markdown("**WHY**")
    extracted["why"]["learning_objective"] = st.text_area("Learning Objective", extracted["why"].get("learning_objective", ""), height=80)
    from modules.module_1_lesson_planning import BLOOMS_LEVELS
    current_bloom = extracted["why"].get("bloom_level", "Not mentioned")
    bloom_options = BLOOMS_LEVELS + ["Not mentioned"]
    bloom_index = bloom_options.index(current_bloom) if current_bloom in bloom_options else len(bloom_options) - 1
    extracted["why"]["bloom_level"] = st.selectbox("Bloom's Level", bloom_options, index=bloom_index)
    extracted["why"]["objective_quality"] = st.text_input("Objective Quality (optional notes)", extracted["why"].get("objective_quality", ""))
    ui.card_close()

    ui.card_open()
    st.markdown("**HOW — TEACHER ACTIVITY**")
    extracted["teacher_activity"] = st.text_area("Teacher Activity", extracted.get("teacher_activity", ""), height=90, label_visibility="collapsed")

    st.markdown("**STUDENT ACTIVITY**")
    extracted["student_activity"] = st.text_area("Student Activity", extracted.get("student_activity", ""), height=90, label_visibility="collapsed")

    st.markdown("**PRACTICE & APPLY**")
    extracted["practice_apply"] = st.text_area("Practice & Apply", extracted.get("practice_apply", ""), height=90, label_visibility="collapsed")

    st.markdown("**REVIEW**")
    extracted["review"] = st.text_area("Review", extracted.get("review", ""), height=90, label_visibility="collapsed")
    ui.card_close()

    _set(module_id, "extracted", extracted)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Start Over"):
            reset_reflection_state(module_id)
            st.rerun()
    with col2:
        if st.button("Confirm Reflection", type="primary"):
            reflection_payload = {
                "teacher_id": teacher_id,
                "module_id": module_id,
                "module_name": module_name,
                "lesson_grade": extracted["what"].get("grade"),
                "lesson_subject": extracted["what"].get("subject"),
                "lesson_plan_number": extracted["what"].get("lesson_plan_number"),
                "lesson_topic": extracted["what"].get("topic"),
                "book": extracted["what"].get("book"),
                "page_section": extracted["what"].get("page_or_section"),
                "voice_note_path": _get(module_id, "audio_path"),
                "transcript": _get(module_id, "transcript"),
                "learning_objective": extracted["why"].get("learning_objective"),
                "bloom_level": extracted["why"].get("bloom_level"),
                "objective_quality": extracted["why"].get("objective_quality"),
                "teacher_activity": extracted.get("teacher_activity"),
                "student_activity": extracted.get("student_activity"),
                "practice_apply": extracted.get("practice_apply"),
                "review": extracted.get("review"),
                "teacher_confirmed": True,
                "module_status": "ai_feedback",
            }

            with st.spinner("Preparing your pedagogical feedback..."):
                evaluation = ai_service.evaluate_reflection(extracted)
                reflection_payload["ai_feedback"] = evaluation["data"]
                reflection_payload["ai_score"] = evaluation["data"]["overall_score"]
                reflection_payload["ai_evaluation_json"] = evaluation["data"]

                saved = db.create_reflection(reflection_payload)
                db.upsert_progress(teacher_id, module_id, {"module_status": "ai_feedback"})

            _set(module_id, "reflection_id", saved.get("id"))
            _set(module_id, "feedback", evaluation["data"])
            _set(module_id, "feedback_demo", evaluation["demo"])
            _set(module_id, "stage", "feedback")
            st.rerun()

    ui.card_close()


def _render_feedback_stage(module_id: str) -> bool:
    feedback = _get(module_id, "feedback", {})

    ui.card_open(highlight=True)
    st.markdown('<div class="pd-eyebrow-light">Step 4 of 4</div>', unsafe_allow_html=True)
    st.markdown("### 🌱 Your Pedagogical Feedback")
    if _get(module_id, "feedback_demo"):
        st.caption("🧪 Demo coaching feedback shown (AI service isn't connected yet).")
    ui.card_close()

    ui.card_open()
    st.markdown("**What You Did Well**")
    st.write(feedback.get("what_you_did_well", ""))
    st.markdown("**Think About**")
    st.write(feedback.get("think_about", ""))
    st.markdown("**One Practical Suggestion**")
    st.write(feedback.get("one_practical_suggestion", ""))

    with st.expander("See detailed rubric scores (0–4 scale)"):
        scores = feedback.get("scores", {})
        labels = {
            "learning_objective": "Learning Objective",
            "blooms_alignment": "Bloom's Alignment",
            "teacher_activity": "Teacher Activity",
            "student_participation": "Student Participation",
            "practice_application": "Practice & Application",
            "review_checking_learning": "Review / Checking Learning",
            "overall_pedagogical_alignment": "Overall Pedagogical Alignment",
        }
        for key, label in labels.items():
            st.write(f"{label}: {scores.get(key, '—')} / 4")
    ui.card_close()

    if st.button("Continue to Final Assessment →", type="primary"):
        return True
    return False
