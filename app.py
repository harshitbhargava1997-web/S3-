import streamlit as st

from modules.module_registry import MODULES
from components.ui import inject_css
from services.supabase_service import is_supabase_configured


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Teacher Learning",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_css()


# ============================================================
# SESSION STATE
# ============================================================

def initialize_state():

    defaults = {
        "page": "Home",

        "teacher": {
            "teacher_id": "DEMO-001",
            "name": "Demo Teacher",
            "school": "Demo School",
            "role": "Teacher",
            "state_zone": "Demo Zone",
        },

        "selected_module": "module_1",

        "current_session": 0,

        "completed_sessions": {},

        "reflection": None,

        "reflection_confirmed": False,

        "assessment_answers": {},

        "assessment_submitted": False,

        "assessment_score": None,

        "demo_mode": True,
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


initialize_state()


# ============================================================
# CONSTANTS
# ============================================================

PART_B_URL = st.secrets.get(
    "PART_B_URL",
    "https://your-part-b-portal.example.com"
)


# ============================================================
# HELPERS
# ============================================================

def go_to(page):

    st.session_state.page = page
    st.rerun()


def get_selected_module():

    module_id = st.session_state.selected_module

    return MODULES.get(module_id)


def module_progress(module_id):

    module = MODULES[module_id]

    total = len(module["sessions"])

    completed = sum(
        1
        for session_id in st.session_state.completed_sessions.get(
            module_id,
            []
        )
    )

    if total == 0:
        return 0

    return int((completed / total) * 100)


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.markdown("## 🌱 Teacher Learning")

        st.caption(
            "Learn • Think • Reflect • Understand • Apply • Improve"
        )

        st.divider()

        pages = [
            "🏠 Home",
            "📚 Learning",
            "📈 My Growth",
            "👤 My Profile",
        ]

        current_label = {
            "Home": "🏠 Home",
            "Learning": "📚 Learning",
            "My Growth": "📈 My Growth",
            "My Profile": "👤 My Profile",
        }.get(
            st.session_state.page,
            "🏠 Home"
        )

        selected = st.radio(
            "Navigation",
            pages,
            index=pages.index(current_label),
            label_visibility="collapsed",
        )

        page_map = {
            "🏠 Home": "Home",
            "📚 Learning": "Learning",
            "📈 My Growth": "My Growth",
            "👤 My Profile": "My Profile",
        }

        st.session_state.page = page_map[selected]

        st.divider()

        if st.button(
            "🔗 Apply in Classroom",
            use_container_width=True,
        ):

            st.session_state.page = "Part B"

            st.rerun()

        st.divider()

        if is_supabase_configured():

            st.success("Connected")

        else:

            st.info("Demo Mode")

        st.caption(
            "Part A — Teacher Professional Development"
        )


# ============================================================
# TOP HEADER
# ============================================================

def render_header():

    st.markdown(
        """
        <div class="app-header">
            <div class="app-title">🌱 Teacher Learning</div>
            <div class="app-subtitle">
                Learn • Think • Reflect • Understand • Apply • Improve
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HOME
# ============================================================

def render_home():

    render_header()

    teacher = st.session_state.teacher

    first_name = teacher["name"].split()[0]

    module = get_selected_module()

    progress = module_progress(module["id"])

    st.markdown(
        f"""
        <div class="welcome-card">
            <div class="small-label">WELCOME BACK</div>
            <h1>{first_name} 👋</h1>
            <p>Your professional learning journey continues.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Continue Learning")

    with st.container(border=True):

        st.markdown(
            f"#### {module['icon']} {module['title']}"
        )

        st.write(module["description"])

        st.progress(
            progress / 100,
            text=f"{progress}% complete"
        )

        completed = st.session_state.completed_sessions.get(
            module["id"],
            []
        )

        if len(completed) < len(module["sessions"]):

            next_session = len(completed)

            if next_session >= len(module["sessions"]):

                next_session = len(module["sessions"]) - 1

            st.caption(
                f"Continue with Session {next_session + 1}: "
                f"{module['sessions'][next_session]['title']}"
            )

        else:

            st.success("Learning sessions completed.")

        if st.button(
            "Continue Learning →",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.current_session = min(
                len(completed),
                len(module["sessions"]) - 1,
            )

            go_to("Learning")

    st.markdown("### Today's Learning")

    with st.container(border=True):

        st.markdown("🎙️ **Classroom Thinking**")

        st.write(
            "Think about one lesson you are going to teach. "
            "How would you approach it using the six-part framework?"
        )

        if st.button(
            "Start Reflection",
            use_container_width=True,
        ):

            st.session_state.current_session = len(
                module["sessions"]
            )

            go_to("Learning")

    st.markdown("### My Progress")

    c1, c2, c3 = st.columns(3)

    completed_count = len(
        st.session_state.completed_sessions.get(
            module["id"],
            []
        )
    )

    c1.metric(
        "Sessions",
        f"{completed_count}/{len(module['sessions'])}"
    )

    c2.metric(
        "Reflection",
        "Done"
        if st.session_state.reflection_confirmed
        else "Not yet",
    )

    if st.session_state.assessment_score is not None:

        c3.metric(
            "Assessment",
            f"{st.session_state.assessment_score}%"
        )

    else:

        c3.metric(
            "Assessment",
            "Not yet"
        )

    st.markdown("### Your Learning Journey")

    journey = [
        ("📖", "Learn"),
        ("💡", "Think"),
        ("🎙️", "Reflect"),
        ("🧠", "Understand"),
        ("🏫", "Apply"),
        ("🌱", "Improve"),
    ]

    cols = st.columns(len(journey))

    for col, (icon, label) in zip(cols, journey):

        with col:

            st.markdown(
                f"""
                <div class="journey-item">
                    <div class="journey-icon">{icon}</div>
                    <div>{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# LEARNING
# ============================================================

def render_learning():

    render_header()

    module = get_selected_module()

    st.markdown(
        f"## {module['icon']} {module['title']}"
    )

    st.caption(module["description"])

    progress = module_progress(module["id"])

    st.progress(
        progress / 100,
        text=f"Module progress: {progress}%"
    )

    tabs = st.tabs(
        [
            "📖 Learn",
            "🎙️ Think & Reflect",
            "📝 Assessment",
        ]
    )

    with tabs[0]:

        render_learning_sessions(module)

    with tabs[1]:

        from components.reflection import render_reflection

        render_reflection(module)

    with tabs[2]:

        render_assessment(module)


# ============================================================
# LEARNING SESSIONS
# ============================================================

def render_learning_sessions(module):

    sessions = module["sessions"]

    completed = st.session_state.completed_sessions.get(
        module["id"],
        []
    )

    current = st.session_state.current_session

    if current >= len(sessions):

        st.success(
            "🎉 You have completed all learning sessions."
        )

        st.info(
            "Continue to Think & Reflect using the tab above."
        )

        return

    session = sessions[current]

    st.caption(
        f"Session {current + 1} of {len(sessions)}"
    )

    st.markdown(
        f"## {session['title']}"
    )

    st.write(
        session["content"]
    )

    st.markdown("### 💡 Think")

    st.write(
        session["question"]
    )

    selected = st.radio(
        "Choose your answer",
        session["options"],
        key=f"session_answer_{module['id']}_{current}",
        label_visibility="collapsed",
    )

    if st.button(
        "Check Answer",
        key=f"check_{module['id']}_{current}",
        type="primary",
        use_container_width=True,
    ):

        answer_index = session["options"].index(
            selected
        )

        if answer_index == session["answer"]:

            if module["id"] not in st.session_state.completed_sessions:

                st.session_state.completed_sessions[
                    module["id"]
                ] = []

            if current not in st.session_state.completed_sessions[
                module["id"]
            ]:

                st.session_state.completed_sessions[
                    module["id"]
                ].append(current)

            st.success(
                "Correct. " + session["feedback"]
            )

        else:

            st.error(
                "Not quite. Think again about the principle "
                "from this session."
            )

    if current in completed:

        st.divider()

        if current < len(sessions) - 1:

            if st.button(
                "Next Session →",
                use_container_width=True,
            ):

                st.session_state.current_session = current + 1

                st.rerun()

        else:

            st.success(
                "All seven learning sessions are complete."
            )

            if st.button(
                "Continue to Reflection →",
                use_container_width=True,
            ):

                st.session_state.current_session = len(sessions)

                st.rerun()


# ============================================================
# ASSESSMENT
# ============================================================

def render_assessment(module):

    sessions = module["sessions"]

    completed = st.session_state.completed_sessions.get(
        module["id"],
        []
    )

    if len(completed) < len(sessions):

        st.info(
            "Complete all learning sessions before taking "
            "the final assessment."
        )

        return

    st.markdown("## 📝 Final Assessment")

    st.write(
        "Check how well you understand the principles "
        "from this module."
    )

    for index, question in enumerate(
        module["assessment"]
    ):

        st.markdown(
            f"**{index + 1}. {question['question']}**"
        )

        selected = st.radio(
            "Answer",
            question["options"],
            key=f"assessment_{module['id']}_{index}",
            index=None,
            label_visibility="collapsed",
        )

        if selected is not None:

            st.session_state.assessment_answers[
                index
            ] = question["options"].index(selected)

    if st.button(
        "Submit Assessment",
        type="primary",
        use_container_width=True,
    ):

        correct = 0

        for index, question in enumerate(
            module["assessment"]
        ):

            selected = st.session_state.assessment_answers.get(
                index
            )

            if selected == question["answer"]:

                correct += 1

        total = len(module["assessment"])

        percentage = round(
            (correct / total) * 100
        )

        st.session_state.assessment_score = percentage

        st.session_state.assessment_submitted = True

        st.rerun()

    if st.session_state.assessment_submitted:

        score = st.session_state.assessment_score

        st.divider()

        if score >= 70:

            st.success(
                f"🎉 Passed — {score}%"
            )

            if len(completed) == len(sessions):

                st.markdown(
                    """
                    ### 🌱 Module Completed

                    You have completed the learning sessions,
                    reflection journey and assessment.

                    Your next step is to apply the thinking
                    in your classroom.
                    """
                )

        else:

            st.error(
                f"{score}% — Review the module and try again."
            )

        st.caption(
            "Pass threshold: 70%"
        )


# ============================================================
# GROWTH
# ============================================================

def render_growth():

    render_header()

    st.markdown("## 📈 My Growth")

    module = get_selected_module()

    progress = module_progress(
        module["id"]
    )

    st.progress(
        progress / 100,
        text=f"Overall learning progress: {progress}%"
    )

    c1, c2, c3 = st.columns(3)

    completed = st.session_state.completed_sessions.get(
        module["id"],
        []
    )

    c1.metric(
        "Sessions",
        f"{len(completed)}/{len(module['sessions'])}"
    )

    c2.metric(
        "Reflection",
        "Completed"
        if st.session_state.reflection_confirmed
        else "Not yet",
    )

    c3.metric(
        "Assessment",
        f"{st.session_state.assessment_score}%"
        if st.session_state.assessment_score is not None
        else "Not yet",
    )

    st.markdown("### Module Progress")

    with st.container(border=True):

        st.markdown(
            f"**{module['icon']} {module['title']}**"
        )

        st.progress(
            progress / 100
        )

        if (
            progress == 100
            and st.session_state.assessment_score is not None
            and st.session_state.assessment_score >= 70
        ):

            st.success("Completed")

        else:

            st.caption("In progress")

    st.markdown("### Reflection History")

    if st.session_state.reflection:

        reflection = st.session_state.reflection

        with st.container(border=True):

            st.caption(
                datetime.now().strftime("%d %b %Y")
            )

            st.markdown(
                f"**{module['title']}**"
            )

            st.write(
                f"{reflection.get('subject', 'Not mentioned')} "
                f"• {reflection.get('topic', 'Not mentioned')}"
            )

            st.caption(
                "Confirmed reflection"
                if st.session_state.reflection_confirmed
                else "Draft"
            )

    else:

        st.info(
            "Your reflection history will appear here."
        )


# ============================================================
# PROFILE
# ============================================================

def render_profile():

    render_header()

    st.markdown("## 👤 My Profile")

    teacher = st.session_state.teacher

    teacher["name"] = st.text_input(
        "Teacher Name",
        teacher["name"]
    )

    teacher["teacher_id"] = st.text_input(
        "Teacher ID",
        teacher["teacher_id"]
    )

    teacher["school"] = st.text_input(
        "School",
        teacher["school"]
    )

    teacher["role"] = st.text_input(
        "Role",
        teacher["role"]
    )

    teacher["state_zone"] = st.text_input(
        "State / Zone",
        teacher["state_zone"]
    )

    st.caption(
        "In production, these details can be populated "
        "from your existing teacher roster."
    )


# ============================================================
# PART B
# ============================================================

def render_part_b():

    render_header()

    st.markdown("## 🏫 Apply in Classroom")

    st.write(
        "Part A helps you learn and reflect. "
        "Your existing Part B portal handles classroom "
        "implementation and evidence."
    )

    st.link_button(
        "Open Classroom Implementation Portal →",
        PART_B_URL,
        use_container_width=True,
    )


# ============================================================
# MAIN
# ============================================================

render_sidebar()

page = st.session_state.page

if page == "Home":

    render_home()

elif page == "Learning":

    render_learning()

elif page == "My Growth":

    render_growth()

elif page == "My Profile":

    render_profile()

elif page == "Part B":

    render_part_b()
