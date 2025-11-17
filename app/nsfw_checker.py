"""Core NSFW detection logic integrating with OpenAI's moderation services."""

from __future__ import annotations

import base64
import json
from io import BytesIO
from typing import Any, Dict, Tuple

from PIL import Image
from openai import BadRequestError, OpenAI

from app.config import settings


client = OpenAI(api_key=settings.openai_api_key)


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Encode raw image bytes to a base64 string."""

    return base64.b64encode(image_bytes).decode("utf-8")


def detect_image_mime_type(image_bytes: bytes) -> str:
    """Detect the MIME type of an image from its bytes."""

    with Image.open(BytesIO(image_bytes)) as img:
        format_to_mime = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "GIF": "image/gif",
            "WEBP": "image/webp",
            "BMP": "image/bmp",
            "TIFF": "image/tiff",
        }
        return format_to_mime.get(img.format or "JPEG", "image/jpeg")


def _normalize_result(result: Any) -> Dict[str, Any]:
    """Convert OpenAI SDK objects into a serialisable dictionary."""

    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "to_dict"):
        return result.to_dict()
    if hasattr(result, "dict"):
        return result.dict()
    if hasattr(result, "json"):
        return json.loads(result.json())
    if isinstance(result, dict):
        return result
    return {"result": result}


def _fallback_moderation_via_chat(image_bytes: bytes) -> Dict[str, Any]:
    """Fallback when direct image moderation is unavailable."""

    mime_type = detect_image_mime_type(image_bytes)
    data_uri = f"data:{mime_type};base64,{encode_image_to_base64(image_bytes)}"
    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a content moderation assistant. Describe images factually.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Provide an objective description of this image."},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            },
        ],
        max_tokens=300,
    )
    description = chat_response.choices[0].message.content or ""
    moderation_response = client.moderations.create(
        model="omni-moderation-latest",
        input=description,
    )
    return _normalize_result(moderation_response.results[0])


def check_image_with_openai(image_bytes: bytes) -> Dict[str, Any]:
    """Send an image to OpenAI moderation and return the parsed result."""

    mime_type = detect_image_mime_type(image_bytes)
    data_uri = f"data:{mime_type};base64,{encode_image_to_base64(image_bytes)}"
    try:
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=data_uri,
        )
        result = response.results[0]
        return _normalize_result(result)
    except BadRequestError as error:
        message = str(error).lower()
        if "invalid input" in message or "image" in message:
            return _fallback_moderation_via_chat(image_bytes)
        raise


def apply_custom_rules(moderation_result: Dict[str, Any]) -> Tuple[str, str, float]:
    """Apply business rules on top of moderation results."""

    categories: Dict[str, Any] = dict(moderation_result.get("categories", {}))
    scores: Dict[str, float] = dict(moderation_result.get("category_scores", {}))
    flagged = bool(moderation_result.get("flagged"))

    triggered_categories = [name for name, value in categories.items() if value]
    if flagged and triggered_categories:
        minor_categories = [c for c in triggered_categories if "minor" in c.lower()]
        if minor_categories:
            return "Not Safe", "Content may involve minors", 0.95
        if any(c for c in triggered_categories if "sexual" in c.lower()):
            sexual_score = float(scores.get("sexual", 0.95))
            return "Not Safe", "Sexual content detected", min(max(sexual_score, 0.85), 1.0)
        joined = ", ".join(triggered_categories)
        return "Not Safe", f"Flagged categories: {joined}", 0.85

    sexual_score = float(scores.get("sexual", 0.0))
    if sexual_score > 0.7:
        return "Not Safe", "High probability of sexual content", sexual_score

    max_score = max(scores.values(), default=0.0)
    confidence = max(0.0, min(1.0, 1.0 - max_score))
    return "Safe", "No concerning content detected", confidence


def check_nsfw(image_bytes: bytes) -> Dict[str, Any]:
    """Main entry point for NSFW detection pipeline."""

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
        moderation_result = check_image_with_openai(image_bytes)
        status, reason, confidence = apply_custom_rules(moderation_result)
        return {
            "status": status,
            "reason": reason,
            "confidence": round(confidence, 3),
            "categories": moderation_result.get("categories", {}),
            "category_scores": moderation_result.get("category_scores", {}),
        }
    except Exception as exc:  # pylint: disable=broad-except
        return {
            "status": "Error",
            "reason": str(exc),
            "confidence": 0.0,
            "categories": {},
            "category_scores": {},
        }
