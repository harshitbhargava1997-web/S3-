"""
components/ui.py
------------------
Shared, mobile-first UI building blocks used across every page: page setup,
custom CSS, cards, progress bars, and small presentational helpers.

Keeping these in one place means every screen looks and feels consistent
without repeating markup.
"""

from __future__ import annotations

import streamlit as st

PRIMARY = "#2F6F5E"       # calm growth green
PRIMARY_DARK = "#1F4D40"
ACCENT = "#E8A33D"        # warm amber for highlights, used sparingly
BG = "#FAFAF7"
CARD_BG = "#FFFFFF"
TEXT = "#1F2937"
MUTED = "#6B7280"
BORDER = "#E5E7EB"


def inject_global_css() -> None:
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {BG};
            }}
            html, body, [class*="css"] {{
                font-size: 17px;
            }}
            .pd-card {{
                background: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 16px;
                padding: 1.25rem 1.25rem;
                margin-bottom: 1rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            }}
            .pd-card-highlight {{
                background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%);
                color: white;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1rem;
            }}
            .pd-card-highlight h3, .pd-card-highlight p {{
                color: white !important;
            }}
            .pd-eyebrow {{
                text-transform: uppercase;
                letter-spacing: 0.06em;
                font-size: 0.75rem;
                font-weight: 600;
                color: {MUTED};
                margin-bottom: 0.25rem;
            }}
            .pd-eyebrow-light {{
                text-transform: uppercase;
                letter-spacing: 0.06em;
                font-size: 0.75rem;
                font-weight: 600;
                color: rgba(255,255,255,0.85);
                margin-bottom: 0.25rem;
            }}
            .pd-progress-track {{
                background: {BORDER};
                border-radius: 999px;
                height: 10px;
                width: 100%;
                overflow: hidden;
                margin: 0.5rem 0;
            }}
            .pd-progress-fill {{
                background: {ACCENT};
                height: 100%;
                border-radius: 999px;
            }}
            .pd-badge {{
                display: inline-block;
                padding: 0.15rem 0.6rem;
                border-radius: 999px;
                font-size: 0.75rem;
                font-weight: 600;
            }}
            .pd-badge-locked {{ background: #F3F4F6; color: {MUTED}; }}
            .pd-badge-progress {{ background: #FEF3C7; color: #92400E; }}
            .pd-badge-done {{ background: #D1FAE5; color: #065F46; }}
            .pd-muted {{ color: {MUTED}; font-size: 0.9rem; }}
            .pd-divider {{
                border: none;
                border-top: 1px solid {BORDER};
                margin: 1rem 0;
            }}
            .stButton > button {{
                border-radius: 12px;
                padding: 0.6rem 1rem;
                font-weight: 600;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_setup(title: str, icon: str = "🌱") -> None:
    st.set_page_config(page_title=f"{title} · Teacher Learning", page_icon=icon, layout="centered")
    inject_global_css()


def demo_mode_banner(flags: dict[str, bool]) -> None:
    """flags: {"Supabase": True/False, "AI": ..., ...} — True means demo/unconfigured."""
    active = [name for name, is_demo in flags.items() if is_demo]
    if active:
        st.info(f"🧪 Demo Mode active for: {', '.join(active)}. The app works fully with sample data.")


def progress_bar(percent: int, label: str | None = None) -> None:
    percent = max(0, min(100, percent))
    label_html = f'<div class="pd-muted">{label}</div>' if label else ""
    st.markdown(
        f"""
        {label_html}
        <div class="pd-progress-track">
            <div class="pd-progress-fill" style="width:{percent}%;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    mapping = {
        "not_started": ('<span class="pd-badge pd-badge-locked">Not Started</span>'),
        "coming_soon": ('<span class="pd-badge pd-badge-locked">Coming Soon</span>'),
        "locked": ('<span class="pd-badge pd-badge-locked">Locked</span>'),
        "learning": ('<span class="pd-badge pd-badge-progress">In Progress</span>'),
        "understanding_check": ('<span class="pd-badge pd-badge-progress">In Progress</span>'),
        "practical_thinking": ('<span class="pd-badge pd-badge-progress">In Progress</span>'),
        "reflection": ('<span class="pd-badge pd-badge-progress">In Progress</span>'),
        "ai_feedback": ('<span class="pd-badge pd-badge-progress">In Progress</span>'),
        "final_assessment": ('<span class="pd-badge pd-badge-progress">In Progress</span>'),
        "completed": ('<span class="pd-badge pd-badge-done">Completed</span>'),
    }
    return mapping.get(status, '<span class="pd-badge pd-badge-locked">Not Started</span>')


def card_open(highlight: bool = False) -> None:
    cls = "pd-card-highlight" if highlight else "pd-card"
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)


def card_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def growth_message(modules_completed: int, reflections_completed: int) -> str:
    """A short, professional (non-childish) motivational message based on progress."""
    if modules_completed == 0 and reflections_completed == 0:
        return "Every strong teacher started with a single reflection. You're ready to begin."
    if modules_completed == 0 and reflections_completed > 0:
        return "You're building a habit of reflection — one of the strongest predictors of growth as a teacher."
    if modules_completed >= 1 and modules_completed < 3:
        return "You're developing a clearer way of thinking about your lessons. Keep going."
    return "Your consistency is shaping how you plan and reflect on teaching. That's real professional growth."
