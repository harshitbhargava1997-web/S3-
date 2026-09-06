import os

import streamlit as st


def get_secret(
    name: str,
    default: str = "",
) -> str:

    try:

        return st.secrets.get(
            name,
            os.getenv(name, default),
        )

    except Exception:

        return os.getenv(
            name,
            default,
        )


def is_supabase_configured() -> bool:

    url = get_secret(
        "SUPABASE_URL"
    )

    key = get_secret(
        "SUPABASE_KEY"
    )

    return bool(
        url and key
    )


def get_client():

    if not is_supabase_configured():

        return None

    from supabase import create_client

    return create_client(
        get_secret("SUPABASE_URL"),
        get_secret("SUPABASE_KEY"),
    )


# ============================================================
# PROFILE
# ============================================================

def save_teacher_profile(
    teacher: dict,
):

    client = get_client()

    if client is None:

        return None

    payload = {
        "teacher_id": teacher["teacher_id"],
        "teacher_name": teacher["name"],
        "school": teacher.get("school"),
        "state_zone": teacher.get("state_zone"),
        "role": teacher.get("role"),
    }

    return client.table(
        "teacher_pd_profiles"
    ).upsert(
        payload,
        on_conflict="teacher_id",
    ).execute()


# ============================================================
# PROGRESS
# ============================================================

def save_progress(
    teacher_id: str,
    module_id: str,
    module_status: str,
    current_session: int,
    progress_percent: int,
):

    client = get_client()

    if client is None:

        return None

    payload = {
        "teacher_id": teacher_id,
        "module_id": module_id,
        "module_status": module_status,
        "current_session": current_session,
        "progress_percent": progress_percent,
    }

    return client.table(
        "teacher_pd_progress"
    ).upsert(
        payload,
        on_conflict="teacher_id,module_id",
    ).execute()


# ============================================================
# REFLECTION
# ============================================================

def save_reflection(
    teacher_id: str,
    reflection: dict,
):

    client = get_client()

    if client is None:

        return None

    payload = {
        "teacher_id": teacher_id,

        "module_id": "module_1",

        "module_name":
            "Foundation of Effective Lesson Planning",

        "lesson_grade":
            reflection["what"].get("grade"),

        "lesson_subject":
            reflection["what"].get("subject"),

        "lesson_plan_number":
            reflection["what"].get(
                "lesson_plan_number"
            ),

        "lesson_topic":
            reflection["what"].get("topic"),

        "book":
            reflection["what"].get("book"),

        "page_section":
            reflection["what"].get(
                "page_or_section"
            ),

        "transcript":
            reflection.get("transcript"),

        "learning_objective":
            reflection["why"].get(
                "learning_objective"
            ),

        "bloom_level":
            reflection["why"].get(
                "bloom_level"
            ),

        "objective_quality":
            reflection["why"].get(
                "objective_quality"
            ),

        "teacher_activity":
            reflection.get(
                "teacher_activity"
            ),

        "student_activity":
            reflection.get(
                "student_activity"
            ),

        "practice_apply":
            reflection.get(
                "practice_apply"
            ),

        "review":
            reflection.get(
                "review"
            ),

        "teacher_confirmed":
            True,

        "module_status":
            "reflection_completed",
    }

    return client.table(
        "teacher_pd_reflections"
    ).insert(
        payload
    ).execute()


# ============================================================
# ASSESSMENT
# ============================================================

def save_assessment(
    teacher_id: str,
    score: int,
    percentage: float,
    passed: bool,
    answers: dict,
):

    client = get_client()

    if client is None:

        return None

    payload = {

        "teacher_id":
            teacher_id,

        "module_id":
            "module_1",

        "score":
            score,

        "percentage":
            percentage,

        "passed":
            passed,

        "answers_json":
            answers,
    }

    return client.table(
        "teacher_pd_assessments"
    ).insert(
        payload
    ).execute()
