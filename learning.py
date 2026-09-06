"""
components/learning.py
------------------------
Renders the short, interactive learning sessions for a module (Session X of N),
including the lightweight "thinking question" interaction described in the
product spec. Progress is persisted through services/supabase_service.py.
"""

from __future__ import annotations

import streamlit as st

from components import ui
from services import supabase_service as db


def _session_answer_key(module_id: str, session_id: int) -> str:
    return f"answered_{module_id}_{session_id}"


def render_learning_sessions(teacher_id: str, module_id: str, sessions: list[dict]) -> bool:
    """
    Renders the current learning session for this module.
    Returns True once all sessions have been completed (so the caller can
    move the teacher on to the reflection step).
    """
    progress = db.get_progress(teacher_id, module_id)
    current_index = int(progress.get("current_session") or 0)
    total = len(sessions)

    if current_index >= total:
        return True  # already finished all sessions

    session = sessions[current_index]

    ui.card_open()
    st.markdown(f'<div class="pd-eyebrow">Module · Session {current_index + 1} of {total}</div>', unsafe_allow_html=True)
    st.subheader(session["title"])
    ui.progress_bar(int(((current_index) / total) * 100))
    st.write(session["explanation"])

    st.markdown("**Example**")
    st.write(session["example"])
    ui.card_close()

    ui.card_open()
    st.markdown("💡 **Think**")
    tq = session["thinking_question"]
    st.write(tq["prompt"])

    answer_key = _session_answer_key(module_id, session["id"])
    already_answered = answer_key in st.session_state

    choice = st.radio(
        "Choose one:",
        options=list(range(len(tq["options"]))),
        format_func=lambda i: tq["options"][i],
        key=f"radio_{answer_key}",
        index=st.session_state.get(answer_key, {}).get("choice") if already_answered else None,
    )

    if st.button("Check my thinking", key=f"check_{answer_key}", disabled=already_answered):
        st.session_state[answer_key] = {"choice": choice}
        st.rerun()

    if already_answered:
        chosen = st.session_state[answer_key]["choice"]
        if chosen == tq["correct_index"]:
            st.success(tq["feedback_correct"])
        else:
            st.warning(tq["feedback_incorrect"])
        st.markdown(f"**Takeaway:** {session['takeaway']}")

        button_label = "Continue" if current_index < total - 1 else "Continue to Reflection"
        if st.button(f"✓ {button_label}", type="primary", key=f"continue_{answer_key}"):
            new_index = current_index + 1
            new_status = "learning" if new_index < total else "reflection"
            db.upsert_progress(
                teacher_id, module_id,
                {
                    "current_session": new_index,
                    "progress_percent": int((new_index / total) * 100),
                    "module_status": new_status,
                    "started_at": progress.get("started_at") or db.now(),
                },
            )
            st.rerun()

    ui.card_close()
    return False
