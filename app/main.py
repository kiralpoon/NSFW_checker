"""FastAPI application exposing NSFW detection endpoints and web UI."""

from __future__ import annotations

import base64

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import settings
from app.nsfw_checker import check_nsfw


class ImageBase64Request(BaseModel):
    """Request body for submitting base64-encoded images."""

    image_base64: str


app = FastAPI(
    title="NSFW Image Detection API",
    description="Check if images contain NSFW content using OpenAI moderation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
async def read_root() -> FileResponse:
    """Serve the browser-based testing interface."""

    return FileResponse("static/index.html")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint required by Cloud Run."""

    return {"status": "healthy"}


@app.post("/check-image")
async def check_image(file: UploadFile = File(...)) -> JSONResponse:
    """Check an uploaded image file for NSFW content."""

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_bytes = await file.read()
        max_bytes = settings.max_file_size_mb * 1024 * 1024
        if len(image_bytes) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB",
            )
        result = check_nsfw(image_bytes)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/check-image-base64")
async def check_image_base64(request: ImageBase64Request) -> JSONResponse:
    """Check a base64-encoded image string for NSFW content."""

    try:
        image_bytes = base64.b64decode(request.image_base64)
        max_bytes = settings.max_file_size_mb * 1024 * 1024
        if len(image_bytes) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB",
            )
        result = check_nsfw(image_bytes)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc)) from exc
