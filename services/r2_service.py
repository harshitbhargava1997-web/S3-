import os
from datetime import datetime

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


def is_r2_configured() -> bool:

    required = [

        "R2_ENDPOINT_URL",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY",
        "R2_BUCKET_NAME",

    ]

    return all(
        get_secret(key)
        for key in required
    )


def get_client():

    if not is_r2_configured():

        return None

    import boto3

    return boto3.client(
        "s3",
        endpoint_url=get_secret(
            "R2_ENDPOINT_URL"
        ),
        aws_access_key_id=get_secret(
            "R2_ACCESS_KEY_ID"
        ),
        aws_secret_access_key=get_secret(
            "R2_SECRET_ACCESS_KEY"
        ),
        region_name="auto",
    )


def upload_audio(
    audio_bytes: bytes,
    teacher_id: str,
    filename: str = "reflection.wav",
):

    client = get_client()

    if client is None:

        return None

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    key = (
        f"pd/module_1/"
        f"teacher/{teacher_id}/"
        f"{today}/"
        f"{filename}"
    )

    client.put_object(
        Bucket=get_secret(
            "R2_BUCKET_NAME"
        ),
        Key=key,
        Body=audio_bytes,
        ContentType="audio/wav",
    )

    return key


def generate_signed_url(
    key: str,
    expires: int = 3600,
):

    client = get_client()

    if client is None:

        return None

    return client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket":
                get_secret(
                    "R2_BUCKET_NAME"
                ),
            "Key":
                key,
        },
        ExpiresIn=expires,
    )
