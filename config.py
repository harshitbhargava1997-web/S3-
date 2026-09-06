"""
config.py
----------
Central configuration layer for the Teacher Learning (Part A) application.

All external service credentials are read from either:
  1. Streamlit secrets (.streamlit/secrets.toml), or
  2. Environment variables

No credentials are ever hard-coded. If a given service's credentials are not
present, the corresponding `*_CONFIGURED` flag will be False and the relevant
service module will fall back to Demo Mode.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    import streamlit as st
    _HAS_STREAMLIT = True
except ImportError:  # pragma: no cover
    _HAS_STREAMLIT = False


def _get(key: str, default: Optional[str] = None) -> Optional[str]:
    """Look up a config value from st.secrets first, then environment vars."""
    if _HAS_STREAMLIT:
        try:
            if key in st.secrets:
                return st.secrets[key]
        except Exception:
            # st.secrets raises if no secrets.toml exists at all — that's fine.
            pass
    return os.environ.get(key, default)


@dataclass(frozen=True)
class Settings:
    # Supabase
    SUPABASE_URL: Optional[str] = _get("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = _get("SUPABASE_KEY")

    # Cloudflare R2
    R2_ENDPOINT_URL: Optional[str] = _get("R2_ENDPOINT_URL")
    R2_ACCESS_KEY_ID: Optional[str] = _get("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY: Optional[str] = _get("R2_SECRET_ACCESS_KEY")
    R2_BUCKET_NAME: Optional[str] = _get("R2_BUCKET_NAME")

    # AI provider (any OpenAI-compatible chat/completions endpoint)
    AI_API_KEY: Optional[str] = _get("AI_API_KEY")
    AI_BASE_URL: Optional[str] = _get("AI_BASE_URL", "https://api.openai.com/v1")
    AI_MODEL: Optional[str] = _get("AI_MODEL", "gpt-4o-mini")

    # Speech-to-text provider (any OpenAI-compatible /audio/transcriptions endpoint)
    STT_API_KEY: Optional[str] = _get("STT_API_KEY")
    STT_BASE_URL: Optional[str] = _get("STT_BASE_URL", "https://api.openai.com/v1")
    STT_MODEL: Optional[str] = _get("STT_MODEL", "whisper-1")

    # Part B (existing Classroom Implementation / Evidence Portal)
    PART_B_URL: Optional[str] = _get("PART_B_URL", "https://example.com/part-b")

    # App-level
    PASS_PERCENTAGE: int = int(_get("PASS_PERCENTAGE", "70"))
    MAX_AUDIO_MB: int = int(_get("MAX_AUDIO_MB", "25"))

    @property
    def SUPABASE_CONFIGURED(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)

    @property
    def R2_CONFIGURED(self) -> bool:
        return bool(
            self.R2_ENDPOINT_URL
            and self.R2_ACCESS_KEY_ID
            and self.R2_SECRET_ACCESS_KEY
            and self.R2_BUCKET_NAME
        )

    @property
    def AI_CONFIGURED(self) -> bool:
        return bool(self.AI_API_KEY)

    @property
    def STT_CONFIGURED(self) -> bool:
        return bool(self.STT_API_KEY)

    @property
    def FULLY_CONFIGURED(self) -> bool:
        return (
            self.SUPABASE_CONFIGURED
            and self.R2_CONFIGURED
            and self.AI_CONFIGURED
            and self.STT_CONFIGURED
        )


settings = Settings()

# Allowed audio upload types (kept small & safe on purpose)
ALLOWED_AUDIO_TYPES = ["wav", "mp3", "m4a", "ogg", "webm"]

# Demo teacher identity used across the app when Supabase / auth isn't wired up yet
DEMO_TEACHER = {
    "teacher_id": "demo-teacher-001",
    "teacher_name": "Demo Teacher",
    "school": "Sunrise Public School",
    "state_zone": "Zone 3",
    "role": "Primary Teacher",
}
