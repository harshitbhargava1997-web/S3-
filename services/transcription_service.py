import os
import io

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


def transcribe_audio(audio_bytes: bytes) -> str:

    api_key = get_secret(
        "STT_API_KEY"
    )

    base_url = get_secret(
        "STT_BASE_URL"
    )

    model = get_secret(
        "STT_MODEL"
    )

    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if not api_key or not base_url or not model:

        return """
I will first introduce the topic using an example.
I want students to understand the main idea.
I will explain the concept and ask questions.
Students will participate in a classroom activity
and then practise using the workbook.
At the end I will ask questions to check whether
they understood the lesson.
""".strip()

    # --------------------------------------------------------
    # PROVIDER REQUEST
    # --------------------------------------------------------

    try:

        import requests

        files = {
            "file": (
                "reflection.wav",
                io.BytesIO(audio_bytes),
                "audio/wav",
            )
        }

        data = {
            "model": model,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
        }

        response = requests.post(
            f"{base_url.rstrip('/')}/audio/transcriptions",
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

        response.raise_for_status()

        result = response.json()

        return result.get(
            "text",
            "",
        )

    except Exception as exc:

        raise RuntimeError(
            f"Speech-to-text provider error: {exc}"
        )
