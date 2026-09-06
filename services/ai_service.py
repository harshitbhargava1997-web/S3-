import json
import os

import streamlit as st


def get_secret(name: str, default: str = "") -> str:

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


# ============================================================
# DEMO EXTRACTION
# ============================================================

def demo_extraction(transcript, context):

    return {

        "what": {

            "grade": context.get(
                "grade"
            ) or "Not mentioned",

            "subject": context.get(
                "subject"
            ) or "Not mentioned",

            "lesson_plan_number": context.get(
                "lesson_plan_number"
            ) or "Not mentioned",

            "topic": context.get(
                "topic"
            ) or "Not mentioned",

            "book": context.get(
                "book"
            ) or "Not mentioned",

            "page_or_section": context.get(
                "page_section"
            ) or "Not mentioned",
        },

        "why": {

            "learning_objective":
                "Students will understand the main idea and apply it.",

            "bloom_level":
                "Apply",

            "objective_quality":
                "Developing",
        },

        "teacher_activity":
            "Introduce the concept with an example and ask questions.",

        "student_activity":
            "Students participate and apply the concept through a classroom activity.",

        "practice_apply":
            "Students practise using the workbook.",

        "review":
            "Ask questions to check understanding.",
    }


# ============================================================
# EXTRACTION
# ============================================================

def extract_reflection(
    transcript: str,
    context: dict,
):

    api_key = get_secret(
        "AI_API_KEY"
    )

    base_url = get_secret(
        "AI_BASE_URL"
    )

    model = get_secret(
        "AI_MODEL"
    )

    if not api_key or not base_url or not model:

        return demo_extraction(
            transcript,
            context,
        )

    system_prompt = """
You are a pedagogical reflection extraction assistant.

Extract only what the teacher actually said.

Never hallucinate.

If something is missing, return:
"Not mentioned"

Do not improve the teacher's meaning.

Return valid JSON only.

Required structure:

{
  "what": {
    "grade": "",
    "subject": "",
    "lesson_plan_number": "",
    "topic": "",
    "book": "",
    "page_or_section": ""
  },
  "why": {
    "learning_objective": "",
    "bloom_level": "",
    "objective_quality": ""
  },
  "teacher_activity": "",
  "student_activity": "",
  "practice_apply": "",
  "review": ""
}
"""

    user_prompt = f"""
Teacher transcript:

{transcript}

Additional manually entered context:

{json.dumps(context, ensure_ascii=False)}
"""

    try:

        import requests

        response = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": 0,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
            },
            timeout=120,
        )

        response.raise_for_status()

        payload = response.json()

        content = payload[
            "choices"
        ][0]["message"]["content"]

        return json.loads(content)

    except Exception:

        # Safe fallback rather than losing the teacher's reflection.
        return demo_extraction(
            transcript,
            context,
        )


# ============================================================
# DEMO EVALUATION
# ============================================================

def demo_evaluation(reflection):

    return {

        "what_you_did_well":
            "Your reflection connects teacher action with student learning and includes a way to check understanding.",

        "think_about":
            "Make the learning objective even more observable by describing exactly what students will do to demonstrate learning.",

        "one_practical_suggestion":
            "Before the lesson, decide on one short student response or task that will give you immediate evidence of understanding.",

        "overall_score":
            3,
    }


# ============================================================
# EVALUATION
# ============================================================

def evaluate_reflection(
    reflection: dict,
):

    api_key = get_secret(
        "AI_API_KEY"
    )

    base_url = get_secret(
        "AI_BASE_URL"
    )

    model = get_secret(
        "AI_MODEL"
    )

    if not api_key or not base_url or not model:

        return demo_evaluation(
            reflection
        )

    system_prompt = """
You are a pedagogical coach for teachers.

You are NOT an examiner.

Evaluate the teacher's confirmed reflection.

Use this rubric:

Learning Objective
Bloom's Alignment
Teacher Activity
Student Participation
Practice & Application
Review / Checking Learning
Overall Pedagogical Alignment

Each score must be from 0 to 4:

0 = Not demonstrated
1 = Weak
2 = Developing
3 = Good
4 = Strong

Return:

{
  "scores": {
    "learning_objective": 0,
    "bloom_alignment": 0,
    "teacher_activity": 0,
    "student_participation": 0,
    "practice_application": 0,
    "review": 0,
    "overall_alignment": 0
  },
  "what_you_did_well": "",
  "think_about": "",
  "one_practical_suggestion": "",
  "overall_score": 0
}

Do not invent classroom practices.

Clearly distinguish suggestions from what the teacher actually said.
"""

    try:

        import requests

        response = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            reflection,
                            ensure_ascii=False,
                        ),
                    },
                ],
            },
            timeout=120,
        )

        response.raise_for_status()

        payload = response.json()

        content = payload[
            "choices"
        ][0]["message"]["content"]

        return json.loads(content)

    except Exception:

        return demo_evaluation(
            reflection
        )
