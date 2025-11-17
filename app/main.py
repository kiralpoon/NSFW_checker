"""FastAPI application exposing NSFW detection endpoints and web UI."""

from __future__ import annotations

import base64

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.nsfw_checker import check_nsfw


class ImageBase64Request(BaseModel):
    """Request body for submitting base64-encoded images."""

    image_base64: str


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="NSFW Image Detection API",
    description="Check if images contain NSFW content using OpenAI moderation",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - use specific origins in production, allow all in development
cors_origins = (
    [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    if settings.cors_origins
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True if cors_origins != ["*"] else False,
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
@limiter.limit(settings.rate_limit)
async def check_image(request: Request, file: UploadFile = File(...)) -> JSONResponse:
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
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@app.post("/check-image-base64")
@limiter.limit(settings.rate_limit)
async def check_image_base64(
    request: Request, body: ImageBase64Request
) -> JSONResponse:
    """Check a base64-encoded image string for NSFW content."""

    try:
        image_bytes = base64.b64decode(body.image_base64, validate=True)
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
        raise HTTPException(status_code=500, detail="Internal server error") from exc
