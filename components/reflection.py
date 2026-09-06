import streamlit as st

from services.transcription_service import transcribe_audio
from services.ai_service import (
    extract_reflection,
    evaluate_reflection,
)


def render_reflection(module):

    st.markdown("## 🎙️ Your Classroom Thinking")

    st.write(
        "Think about one lesson you are going to teach "
        "and explain how you would approach it using "
        "the six-part framework."
    )

    st.caption(
        "Speak naturally for 1–2 minutes. "
        "You do not need to speak perfectly."
    )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    audio = st.audio_input(
        "Record your reflection",
        sample_rate=16000,
    )

    uploaded = st.file_uploader(
        "Or upload an audio recording",
        type=[
            "wav",
            "mp3",
            "m4a",
            "ogg",
        ],
    )

    # --------------------------------------------------------
    # LESSON CONTEXT
    # --------------------------------------------------------

    st.markdown("### Lesson Context")

    col1, col2 = st.columns(2)

    grade = col1.text_input(
        "Grade",
        key="reflection_grade",
    )

    subject = col2.text_input(
        "Subject",
        key="reflection_subject",
    )

    col1, col2 = st.columns(2)

    lesson_plan = col1.text_input(
        "Lesson Plan Number",
        key="reflection_lp",
    )

    topic = col2.text_input(
        "Topic / Chapter",
        key="reflection_topic",
    )

    book = st.text_input(
        "Book / Workbook",
        key="reflection_book",
    )

    page = st.text_input(
        "Relevant Page / Section",
        key="reflection_page",
    )

    # --------------------------------------------------------
    # TRANSCRIPTION
    # --------------------------------------------------------

    transcript = st.session_state.get(
        "reflection_transcript",
        "",
    )

    if audio:

        st.audio(audio)

        if st.button(
            "Convert Voice to Text",
            use_container_width=True,
        ):

            try:

                audio_bytes = audio.getvalue()

                transcript = transcribe_audio(
                    audio_bytes
                )

                st.session_state[
                    "reflection_transcript"
                ] = transcript

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Transcription failed: {exc}"
                )

    elif uploaded:

        st.audio(uploaded)

        if st.button(
            "Convert Uploaded Audio to Text",
            use_container_width=True,
        ):

            try:

                transcript = transcribe_audio(
                    uploaded.getvalue()
                )

                st.session_state[
                    "reflection_transcript"
                ] = transcript

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Transcription failed: {exc}"
                )

    # --------------------------------------------------------
    # MANUAL TRANSCRIPT
    # --------------------------------------------------------

    st.markdown("### Transcript")

    transcript = st.text_area(
        "Review or edit your transcript",
        value=transcript,
        height=160,
        key="reflection_transcript_editor",
    )

    if st.button(
        "Structure My Reflection →",
        type="primary",
        use_container_width=True,
    ):

        if not transcript.strip():

            st.warning(
                "Please record/upload an audio reflection "
                "or enter your transcript."
            )

            return

        structured = extract_reflection(
            transcript=transcript,
            context={
                "grade": grade,
                "subject": subject,
                "lesson_plan_number": lesson_plan,
                "topic": topic,
                "book": book,
                "page_section": page,
            },
        )

        structured["transcript"] = transcript

        st.session_state.reflection = structured

        st.session_state.reflection_confirmed = False

        st.rerun()

    # --------------------------------------------------------
    # STRUCTURED REFLECTION
    # --------------------------------------------------------

    if st.session_state.reflection:

        render_structured_reflection(
            module
        )


def render_structured_reflection(module):

    reflection = st.session_state.reflection

    st.divider()

    st.markdown(
        "## ✍️ Here's What I Understood"
    )

    st.caption(
        "Review the information carefully. "
        "You can edit anything before confirming."
    )

    # --------------------------------------------------------
    # WHAT
    # --------------------------------------------------------

    st.markdown("### 1. WHAT")

    reflection["what"]["grade"] = st.text_input(
        "Grade",
        reflection["what"].get("grade", ""),
        key="structured_grade",
    )

    reflection["what"]["subject"] = st.text_input(
        "Subject",
        reflection["what"].get("subject", ""),
        key="structured_subject",
    )

    reflection["what"]["lesson_plan_number"] = st.text_input(
        "Lesson Plan Number",
        reflection["what"].get(
            "lesson_plan_number",
            "",
        ),
        key="structured_lp",
    )

    reflection["what"]["topic"] = st.text_input(
        "Topic / Chapter",
        reflection["what"].get(
            "topic",
            "",
        ),
        key="structured_topic",
    )

    reflection["what"]["book"] = st.text_input(
        "Book / Workbook",
        reflection["what"].get(
            "book",
            "",
        ),
        key="structured_book",
    )

    reflection["what"]["page_or_section"] = st.text_input(
        "Page / Section",
        reflection["what"].get(
            "page_or_section",
            "",
        ),
        key="structured_page",
    )

    # --------------------------------------------------------
    # WHY
    # --------------------------------------------------------

    st.markdown("### 2. WHY")

    reflection["why"]["learning_objective"] = st.text_area(
        "Learning Objective",
        reflection["why"].get(
            "learning_objective",
            "",
        ),
        key="structured_objective",
    )

    bloom_options = [
        "Remember",
        "Understand",
        "Apply",
        "Analyse",
        "Evaluate",
        "Create",
        "Not mentioned",
    ]

    current_bloom = reflection["why"].get(
        "bloom_level",
        "Not mentioned",
    )

    if current_bloom not in bloom_options:

        current_bloom = "Not mentioned"

    reflection["why"]["bloom_level"] = st.selectbox(
        "Bloom Level",
        bloom_options,
        index=bloom_options.index(
            current_bloom
        ),
        key="structured_bloom",
    )

    reflection["why"]["objective_quality"] = st.text_input(
        "Objective Quality",
        reflection["why"].get(
            "objective_quality",
            "Not mentioned",
        ),
        key="structured_quality",
    )

    # --------------------------------------------------------
    # HOW
    # --------------------------------------------------------

    st.markdown("### 3. HOW — Teacher Activity")

    reflection["teacher_activity"] = st.text_area(
        "Teacher Activity",
        reflection.get(
            "teacher_activity",
            "",
        ),
        key="structured_teacher",
    )

    # --------------------------------------------------------
    # STUDENT ACTIVITY
    # --------------------------------------------------------

    st.markdown("### 4. STUDENT ACTIVITY")

    reflection["student_activity"] = st.text_area(
        "Student Activity",
        reflection.get(
            "student_activity",
            "",
        ),
        key="structured_student",
    )

    # --------------------------------------------------------
    # PRACTICE
    # --------------------------------------------------------

    st.markdown("### 5. PRACTICE & APPLY")

    reflection["practice_apply"] = st.text_area(
        "Practice & Application",
        reflection.get(
            "practice_apply",
            "",
        ),
        key="structured_practice",
    )

    # --------------------------------------------------------
    # REVIEW
    # --------------------------------------------------------

    st.markdown("### 6. REVIEW")

    reflection["review"] = st.text_area(
        "Review / Check Learning",
        reflection.get(
            "review",
            "",
        ),
        key="structured_review",
    )

    # --------------------------------------------------------
    # CONFIRM
    # --------------------------------------------------------

    if st.button(
        "Confirm Reflection",
        type="primary",
        use_container_width=True,
    ):

        st.session_state.reflection_confirmed = True

        st.session_state.reflection = reflection

        st.rerun()

    # --------------------------------------------------------
    # AI FEEDBACK
    # --------------------------------------------------------

    if st.session_state.reflection_confirmed:

        render_feedback(
            reflection
        )


def render_feedback(reflection):

    st.divider()

    st.markdown(
        "## 🌱 Your Pedagogical Feedback"
    )

    try:

        evaluation = evaluate_reflection(
            reflection
        )

    except Exception as exc:

        st.error(
            f"Feedback could not be generated: {exc}"
        )

        return

    st.markdown(
        "### What You Did Well"
    )

    st.success(
        evaluation.get(
            "what_you_did_well",
            "Your reflection shows thoughtful planning.",
        )
    )

    st.markdown(
        "### Think About"
    )

    st.info(
        evaluation.get(
            "think_about",
            "Consider making the student outcome more observable.",
        )
    )

    st.markdown(
        "### One Practical Suggestion"
    )

    st.warning(
        evaluation.get(
            "one_practical_suggestion",
            "Choose one short task that gives immediate evidence of learning.",
        )
    )

    if evaluation.get("overall_score") is not None:

        st.metric(
            "Pedagogical Alignment",
            f"{evaluation['overall_score']}/4",
        )

    st.caption(
        "The AI is acting as a pedagogical coach, "
        "not an examiner."
    )
