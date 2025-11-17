import base64
import os
from io import BytesIO

import pytest
from httpx import AsyncClient
from PIL import Image

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app import nsfw_checker  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def image_bytes() -> bytes:
    image = Image.new("RGB", (10, 10), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_check_image_safe(client: AsyncClient, image_bytes: bytes, monkeypatch: pytest.MonkeyPatch):
    def fake_moderation(_image_bytes: bytes):
        return {
            "flagged": False,
            "categories": {"sexual": False, "self-harm": False},
            "category_scores": {"sexual": 0.02, "self-harm": 0.01},
        }

    monkeypatch.setattr(nsfw_checker, "check_image_with_openai", fake_moderation)

    response = await client.post(
        "/check-image",
        files={"file": ("safe.png", image_bytes, "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Safe"
    assert payload["reason"] == "No concerning content detected"
    assert payload["confidence"] == pytest.approx(0.98, rel=1e-2)


@pytest.mark.asyncio
async def test_check_image_not_safe(client: AsyncClient, image_bytes: bytes, monkeypatch: pytest.MonkeyPatch):
    def fake_moderation(_image_bytes: bytes):
        return {
            "flagged": True,
            "categories": {"sexual": True, "self-harm": False},
            "category_scores": {"sexual": 0.92, "self-harm": 0.01},
        }

    monkeypatch.setattr(nsfw_checker, "check_image_with_openai", fake_moderation)

    response = await client.post(
        "/check-image",
        files={"file": ("unsafe.png", image_bytes, "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Not Safe"
    assert "Sexual content" in payload["reason"]
    assert payload["confidence"] == pytest.approx(0.92, rel=1e-3)


@pytest.mark.asyncio
async def test_check_image_base64(client: AsyncClient, image_bytes: bytes, monkeypatch: pytest.MonkeyPatch):
    def fake_moderation(_image_bytes: bytes):
        return {
            "flagged": False,
            "categories": {"sexual": False},
            "category_scores": {"sexual": 0.05},
        }

    monkeypatch.setattr(nsfw_checker, "check_image_with_openai", fake_moderation)

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    response = await client.post("/check-image-base64", json={"image_base64": encoded})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Safe"
    assert "No concerning" in payload["reason"]
