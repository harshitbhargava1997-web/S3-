"""
app.py
-------
Home screen for the Teacher Learning (Part A) application.

This is intentionally the entry point Streamlit runs first; the other
sections (Learning, My Growth, My Profile) live under pages/ and appear
automatically in the sidebar navigation.
"""

from __future__ import annotations

import streamlit as st

from components import ui
from config import settings, DEMO_TEACHER
from modules import module_registry
from services import supabase_service as db

ui.page_setup("Home", icon="🌱")


def get_current_teacher_id() -> str:
    if "teacher_id" not in st.session_state:
        st.session_state["teacher_id"] = DEMO_TEACHER["teacher_id"]
    return st.session_state["teacher_id"]


teacher_id = get_current_teacher_id()
profile = db.get_or_create_profile(teacher_id)

ui.demo_mode_banner({
    "Database": db.is_demo_mode(),
})

# ---------------------------------------------------------------------------
# Welcome
# ---------------------------------------------------------------------------

first_name = (profile.get("teacher_name") or "Teacher").split(" ")[0]
st.markdown(f"## Welcome back, {first_name} 👋")
st.caption("Learn → Think → Reflect → Understand → Apply → Improve")

# ---------------------------------------------------------------------------
# Continue Learning
# ---------------------------------------------------------------------------

active_module = module_registry.get_first_available_module()
module_progress = db.get_progress(teacher_id, active_module["id"])
status = module_progress.get("module_status", "not_started")
percent = int(module_progress.get("progress_percent") or 0)

ui.card_open(highlight=True)
st.markdown('<div class="pd-eyebrow-light">Continue Learning</div>', unsafe_allow_html=True)
st.markdown(f"### {active_module['name']}")
if status == "not_started":
    st.write("You haven't started this module yet. Ready when you are.")
else:
    session_num = int(module_progress.get("current_session") or 0) + 1
    st.write(f"You're on session {min(session_num, 7)} of 7.")
ui.progress_bar(percent)
if st.button("Continue →", type="primary", key="home_continue"):
    st.switch_page("pages/2_Learning.py")
ui.card_close()

# ---------------------------------------------------------------------------
# Today's Learning
# ---------------------------------------------------------------------------

ui.card_open()
st.markdown('<div class="pd-eyebrow">Today\'s Learning</div>', unsafe_allow_html=True)
st.markdown("**Today's Reflection**")
st.write(
    "Think about the last lesson you taught. What would you keep exactly the "
    "same, and what would you approach differently next time?"
)
ui.card_close()

# ---------------------------------------------------------------------------
# My Progress
# ---------------------------------------------------------------------------

from components import progress as progress_component  # noqa: E402
progress_component.render_growth_summary_card(teacher_id)

# ---------------------------------------------------------------------------
# Apply in Classroom
# ---------------------------------------------------------------------------

ui.card_open()
st.markdown('<div class="pd-eyebrow">Ready to Apply This?</div>', unsafe_allow_html=True)
st.write("Once you've learned and reflected, take it into your classroom.")
st.link_button("Apply in Classroom ↗", settings.PART_B_URL, use_container_width=True)
ui.card_close()
