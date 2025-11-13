# NSFW Image Detection API with OpenAI Moderation and GCP Deployment

This ExecPlan is a living document. The sections Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective must be kept up to date as work proceeds.

This document must be maintained in accordance with .agent/PLANS.md in the repository root.


## Purpose / Big Picture

After completing this work, users will be able to send an image to a web API endpoint and receive a JSON response indicating whether the image is "Safe" or "Not Safe" based on NSFW (Not Safe For Work) content detection. The system will block sexually explicit content, nudity, and potentially underage subjects while applying custom rules (for example, male topless images may be acceptable while female topless images are not).

Users can interact with the system in multiple ways: through a simple web UI for easy browser-based testing, via command-line tools like curl for automation and scripting, or through the auto-generated API documentation at /docs for exploration and testing.

The API will be deployed to Google Cloud Platform (GCP) using Cloud Run, a serverless container platform that automatically scales based on incoming requests and charges only for actual usage. Users can verify the system works by uploading test images via the web UI, HTTP POST requests, or the interactive API documentation.


## Progress

- [ ] Set up Python project structure with FastAPI framework
- [ ] Create requirements.txt with all necessary Python packages
- [ ] Implement core NSFW checker module using OpenAI API
- [ ] Create FastAPI endpoints to accept image uploads
- [ ] Add custom rule logic for edge cases
- [ ] Create simple web UI for browser-based testing
- [ ] Configure FastAPI to serve static files and web UI
- [ ] Create Dockerfile for containerization
- [ ] Write cloudbuild.yaml for GCP deployment automation
- [ ] Configure environment variables and secrets
- [ ] Deploy to GCP Cloud Run
- [ ] Test deployed API with sample images via web UI and command line
- [ ] Document API usage in README


## Surprises & Discoveries

(This section will be populated as implementation proceeds)


## Decision Log

- Decision: Use OpenAI Moderation API as primary detection mechanism
  Rationale: Fastest path to production with reasonable accuracy. The API is maintained by OpenAI and handles most NSFW cases. We can enhance later with specialized models if needed.
  Date: 2025-11-13

- Decision: Deploy to GCP Cloud Run instead of other serverless platforms
  Rationale: User specified GCP. Cloud Run provides serverless containers with pay-per-use pricing, automatic HTTPS, and simple deployment from Docker images. No cold start concerns for moderate traffic.
  Date: 2025-11-13

- Decision: Accept images via multipart/form-data file upload and optionally base64 encoded strings
  Rationale: Covers both direct file uploads (easier for testing) and programmatic API usage (base64 in JSON). Most flexible for various client types.
  Date: 2025-11-13

- Decision: Include a simple web UI for browser-based testing
  Rationale: User requested an easy way to test without command-line tools. A single-page HTML interface with drag-and-drop file upload provides immediate visual feedback and makes the API accessible to non-technical users. FastAPI can serve static files directly without needing a separate frontend server.
  Date: 2025-11-13

- Decision: Use OpenAI Moderation API directly with images (not two-step vision approach)
  Rationale: OpenAI's moderation API now supports images directly as confirmed in official documentation. This simplifies implementation significantly, reduces API calls, lowers latency, and eliminates the complexity of the vision-model-then-moderation fallback approach. Single API call is more reliable and maintainable.
  Date: 2025-11-13

- Decision: Set file size limit to 25MB maximum
  Rationale: Prevents malicious users from uploading extremely large files that could cause memory issues or denial of service. 25MB is sufficient for high-resolution photos while protecting the service. Implemented as configurable MAX_FILE_SIZE_MB environment variable for flexibility.
  Date: 2025-11-13

- Decision: Update to November 2025 stable package versions
  Rationale: Original plan used versions from late 2023. Updating to current stable versions (FastAPI 0.115.0, OpenAI 1.51.0, Python 3.12) ensures compatibility with latest OpenAI API features including direct image moderation support, security patches, and performance improvements.
  Date: 2025-11-13

- Decision: Use Google Secret Manager as primary deployment approach
  Rationale: Storing API keys in plain environment variables exposes them in command history and Cloud Run console. Secret Manager encrypts secrets at rest, provides access logging, and follows security best practices for production deployments. Environment variables remain available for local development convenience.
  Date: 2025-11-13


## Outcomes & Retrospective

(This section will be completed after major milestones and at project completion)


## Context and Orientation

This is a new project being built from scratch. The repository currently contains planning and documentation files: Agents.md (agent configuration rules), .agent/PLANS.md (ExecPlan methodology guidelines), CLAUDE.md (guidance for Claude Code), .gitignore, and this ExecPlan. No application code has been implemented yet.

We will create a Python-based REST API using FastAPI, which is a modern Python web framework that automatically generates API documentation and handles request/response validation. The API will accept image files, send them to OpenAI's API for content moderation analysis, apply custom business rules, and return a simple classification result.

Key terms defined:

FastAPI - A Python web framework for building APIs. It uses Python type hints to validate data automatically and generates interactive documentation.

OpenAI Moderation API - A service provided by OpenAI that analyzes text and images for potentially harmful content including sexual, violent, or hateful content.

Cloud Run - Google Cloud Platform's serverless container hosting service. It runs Docker containers on demand and scales automatically from zero to many instances.

Docker - A containerization technology that packages an application with all its dependencies into a standardized unit called a container.

NSFW - "Not Safe For Work" meaning content that is inappropriate for professional or public settings, typically sexual or violent imagery.


## Plan of Work

### Milestone 1: Local API Development with Visual Testing

We will build a working API that runs on the local machine and verify it works through browser-based testing before containerization. This milestone follows Test-Driven Development principles: we create the core functionality, add a web UI for visual testing, and thoroughly validate everything works locally before moving to Docker and cloud deployment. At the end of this milestone, you will be able to access a web interface at http://localhost:8080, upload test images through your browser, and see real-time classification results from OpenAI's moderation API.

The project structure will be:

    NSFW_Checker/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py              (FastAPI application and routes)
    │   ├── nsfw_checker.py      (OpenAI integration and logic)
    │   └── config.py            (Configuration management)
    ├── static/
    │   ├── index.html           (Web UI for testing)
    │   ├── style.css            (Styling for web UI)
    │   └── script.js            (Client-side JavaScript)
    ├── tests/
    │   ├── __init__.py
    │   └── test_api.py          (Basic API tests)
    ├── .env.example             (Template for environment variables)
    ├── .dockerignore            (Files to exclude from Docker build)
    ├── .gitignore               (Files to exclude from git)
    ├── Dockerfile               (Docker container definition)
    ├── requirements.txt         (Python dependencies)
    └── README.md                (Usage documentation)

The requirements.txt file will list these Python packages: fastapi for the web framework, uvicorn with the standard extra for running the ASGI server, python-multipart for handling file uploads, openai for the official OpenAI Python client, pillow for image processing, python-dotenv to load environment variables from .env file, pydantic-settings for configuration management, pytest for testing, and httpx for making HTTP requests in tests.

The app/config.py file will create a configuration class using Pydantic's BaseSettings that loads the OpenAI API key from environment variables and validates that it exists.

The app/nsfw_checker.py file will implement the core logic with these functions: create an OpenAI client instance using the modern SDK pattern, a function to encode images to base64 which is required for OpenAI API, a function to call OpenAI's API with the image (with fallback to two-step vision plus moderation if direct image support is unavailable), a function to parse the moderation response, a function to apply custom rules based on confidence thresholds and category filtering, and finally return a simple decision of "Safe" or "Not Safe" with reasoning.

The app/main.py file will create the FastAPI application by importing FastAPI and creating an app instance, adding CORS middleware to allow browser requests, mounting the static files directory to serve the web UI, defining a GET endpoint at / that serves the web UI HTML file, defining a POST endpoint at /check-image that accepts file upload via multipart/form-data, defining a POST endpoint at /check-image-base64 that accepts JSON with base64-encoded image string, calling the nsfw_checker functions, and returning JSON response with status ("Safe" or "Not Safe"), reason, confidence (0.0-1.0), and categories. It will also add a GET endpoint at /health for health checks which is required by Cloud Run.

The tests/test_api.py file will create basic tests including testing that the health endpoint returns 200, mocking OpenAI API responses, testing safe image classification, and testing unsafe image classification.

The static directory files create a complete web UI. The static/index.html file provides the structure with file upload input, preview area, check button, and results display. The static/style.css file styles the interface with a modern, polished design including gradient backgrounds, card-style container, and color-coded results (green for safe, red for unsafe). The static/script.js file handles all client-side logic including file selection, image preview, FormData creation, fetch API calls to the backend, response parsing, and dynamic result display.

At the end of this milestone, you must verify the following through browser testing: run the API locally on port 8080 with uvicorn, open a browser and navigate to http://localhost:8080/ to see the web UI, upload a clearly safe test image (like a landscape photo) and verify you receive "Safe" status with high confidence, upload a test image with concerning content and verify you receive "Not Safe" status with appropriate reasoning, check that the API documentation is accessible at http://localhost:8080/docs, and verify the health endpoint returns healthy status. Only after confirming all visual tests pass should you proceed to containerization. This TDD approach ensures the application works correctly before adding Docker complexity.


### Milestone 2: Containerization

After verifying the application works correctly through local browser testing, we will package it into a Docker container. This milestone should only begin after you have successfully tested the web UI, uploaded multiple test images, and confirmed the API returns correct classifications. Docker ensures that the application runs the same way in development, testing, and production environments. We containerize last to avoid debugging Docker issues when the problem might be in the application code itself.

The Dockerfile will use the official Python 3.11 slim base image to keep the container size small. It will set the working directory to /app, copy requirements.txt first and install dependencies (this ordering allows Docker to cache the dependency layer), copy the application code, copy the static files directory for the web UI, expose port 8080 which is Cloud Run's default, set the PORT environment variable to 8080, and set the CMD to run the uvicorn server listening on all interfaces (0.0.0.0) on the PORT.

The .dockerignore file will exclude unnecessary files from the Docker image including .env (secrets should never be in the container image), __pycache__ and *.pyc files, .git and .gitignore, the tests/ directory, and any local virtual environments.

For local Docker testing we will build the image with the command docker build -t nsfw-checker . (the dot means use current directory), run it with docker run -p 8080:8080 -e OPENAI_API_KEY=your-key nsfw-checker (the -p maps port 8080 from container to host, -e sets environment variable), and test by sending a request to http://localhost:8080/health which should return the healthy status.

At the end of this milestone, the API will run inside a Docker container on the local machine, proving it will work in Cloud Run's container environment.


### Milestone 3: GCP Cloud Run Deployment

We will deploy the containerized API to Google Cloud Run, making it accessible via a public HTTPS URL that anyone can call. Cloud Run will automatically provide SSL certificates, scale the service based on traffic, and only charge for actual usage.

Prerequisites for this milestone include having a GCP project with billing enabled, knowing the Project ID (something like my-project-12345), knowing the Project Number (something like 123456789012), having the gcloud CLI installed and authenticated with gcloud auth login, and having the Cloud Run API enabled in the GCP project.

The optional cloudbuild.yaml file can be created for automated builds. It defines build steps for Google Cloud Build to build the Docker image using Cloud Build, push the image to Google Container Registry (GCR) at the path gcr.io/PROJECT_ID/nsfw-checker, and deploy to Cloud Run service named nsfw-checker.

The optional .gcloudignore file excludes files when deploying source code if using gcloud run deploy without pre-building Docker.

For deployment, there are two options. Option A is manual Docker deployment which is simpler and recommended for the first time. The steps are: enable required APIs with gcloud services enable run.googleapis.com containerregistry.googleapis.com, configure Docker to authenticate with GCR using gcloud auth configure-docker, tag the local image with docker tag nsfw-checker gcr.io/PROJECT_ID/nsfw-checker:v1, push to GCR with docker push gcr.io/PROJECT_ID/nsfw-checker:v1, and deploy to Cloud Run with the gcloud run deploy command specifying the image, platform managed, region us-central1, allow-unauthenticated flag for public access, set-env-vars to pass OPENAI_API_KEY, max-instances 10 to prevent unexpected costs, memory 512Mi for image processing, and timeout 60s to allow time for OpenAI API calls.

Option B is automated deployment via Cloud Build for continuous integration and deployment. Simply submit the build with gcloud builds submit --config cloudbuild.yaml and Cloud Build will build, push, and deploy automatically.

For configuration, the OpenAI API key can be set as an environment variable in Cloud Run via the console or CLI. For better security, use Google Secret Manager by creating a secret with gcloud secrets create openai-api-key --data-file=- (then paste key and press Ctrl+D), and update the Cloud Run service to mount the secret with gcloud run services update nsfw-checker --update-secrets OPENAI_API_KEY=openai-api-key:latest.

At the end of this milestone, the API will be live at a Cloud Run URL like https://nsfw-checker-abc123-uc.a.run.app. You can send requests to this URL from anywhere on the internet, and Cloud Run will automatically scale from 0 to many instances based on incoming traffic.


## Concrete Steps

### Step 1: Set up local development environment

Working directory is the project root NSFW_Checker/.

First create a Python virtual environment with python -m venv venv, then activate it. On Windows use venv\Scripts\activate and on Mac/Linux use source venv/bin/activate.

Create the requirements.txt file with these exact contents:

    fastapi==0.115.0
    uvicorn[standard]==0.30.6
    python-multipart==0.0.12
    openai==1.51.0
    pillow==10.4.0
    python-dotenv==1.0.1
    pydantic-settings==2.5.2
    pytest==8.3.3
    httpx==0.27.2

Install all dependencies with pip install -r requirements.txt.

Create the directory structure. On Windows use mkdir app tests static and type nul > app\__init__.py and similar for other files. On Mac/Linux use mkdir app tests static and touch app/__init__.py. Create these empty files: app/__init__.py, app/main.py, app/nsfw_checker.py, app/config.py, tests/__init__.py, tests/test_api.py. The static directory will hold the web UI files created in a later step.

Create .env.example file with these lines:

    OPENAI_API_KEY=sk-your-key-here
    PORT=8080
    MAX_FILE_SIZE_MB=25

Copy .env.example to .env and edit it to add your actual OpenAI API key.

Expected output: Directory structure created, dependencies installed successfully, virtual environment active and you should see (venv) in your terminal prompt.


### Step 2: Implement configuration management

Edit the file app/config.py. Import BaseSettings from pydantic_settings. Create a Settings class that inherits from BaseSettings. Add three fields: openai_api_key as a required string, port as an integer with default value 8080, and max_file_size_mb as an integer with default value 25. Inside the Settings class, create a nested Config class with env_file = ".env". Finally create a module-level variable settings = Settings() which will load and validate the configuration when imported.

This loads environment variables automatically from the .env file and validates that openai_api_key is present, raising an error if it's missing. The max_file_size_mb setting controls the maximum allowed upload size to prevent denial of service attacks.


### Step 3: Implement NSFW checker logic

Edit the file app/nsfw_checker.py. This is the core module that handles all the NSFW detection logic.

Step 3a - Imports and Setup:

Import the necessary modules: base64, BytesIO from io, Dict and Tuple from typing, Image from PIL, OpenAI from openai, and settings from app.config.

Create an OpenAI client instance at module level: client = OpenAI(api_key=settings.openai_api_key). This uses the modern OpenAI SDK pattern where you create a client instance rather than setting a global API key.

Step 3b - Image Encoding Helper:

Define encode_image_to_base64 function that takes image_bytes as bytes parameter and returns a string. Use base64.b64encode to encode the bytes and decode to string with utf-8. This converts raw image bytes into a base64-encoded string that can be sent to APIs.

Step 3c - OpenAI Moderation API Integration:

Define check_image_with_openai function that takes image_bytes and returns a Dict. This sends the image to OpenAI's moderation API for analysis.

Call encode_image_to_base64 to get the base64 string. Create a data URI in the format "data:image/jpeg;base64," followed by the base64 string. Call client.moderations.create with input set to the data URI. The OpenAI moderation API is expected to support direct image analysis as of November 2024. Extract the first result from the response and convert it to a dictionary using model_dump() or dict() conversion. Return this dictionary containing the moderation analysis.

Important: If the OpenAI moderation API does not support images directly (you may encounter errors like "invalid input type"), implement a two-step fallback approach: first use the Chat API with a vision model (like gpt-4-vision-preview) to describe the image, then call the moderation API on that text description. See the "Notes on OpenAI Moderation API Evolution" section for detailed fallback implementation guidance.

Step 3d - Custom Business Rules:

Define apply_custom_rules function that takes moderation_result dictionary and returns a Tuple of (status string, reason string, confidence float). This applies custom business logic on top of OpenAI's results to make the final classification decision.

Get the categories and scores dictionaries from the moderation_result. If the moderation_result flagged field is True, find which categories triggered by checking which ones are True. If any category contains "minor" (case-insensitive), return "Not Safe", "Content may involve minors", 0.95. If the sexual category is True, get the sexual confidence score and return "Not Safe", "Sexual content detected", and that confidence. For other violations return "Not Safe" with the triggered category names and 0.85 confidence. Even if not flagged, check if the sexual score is above 0.7 as a custom threshold and return "Not Safe" with high probability message. Otherwise return "Safe", "No concerning content detected", and compute confidence as 1.0 minus the maximum of all scores.

Step 3e - Main Entry Point Function:

Define check_nsfw function that takes image_bytes and returns a Dict. This is the main entry point that orchestrates the entire NSFW detection workflow.

Wrap everything in a try-except. Try to open the image with Image.open(BytesIO(image_bytes)) and call verify() to ensure it's a valid image. Call check_image_with_openai to get the moderation_result. Call apply_custom_rules to get status, reason, and confidence. Return a dictionary with status, reason, confidence rounded to 3 decimals, and the raw categories and category_scores from moderation_result. In the except block, catch any Exception and return a dictionary with status "Error", reason describing the error, confidence 0.0, and empty dictionaries for categories and scores.

This completes the core NSFW detection logic. The module provides a clean interface where you pass in image bytes and receive a structured decision with reasoning.


### Step 4: Create FastAPI application

Edit the file app/main.py. This creates the web API with all the endpoints.

Import FastAPI, File, UploadFile, and HTTPException from fastapi. Import JSONResponse from fastapi.responses. Import StaticFiles from fastapi.staticfiles. Import CORSMiddleware from fastapi.middleware.cors. Import BaseModel from pydantic. Import base64. Import check_nsfw from app.nsfw_checker. Import settings from app.config.

Create the app instance with FastAPI(title="NSFW Image Detection API", description="Check if images contain NSFW content using OpenAI moderation", version="1.0.0").

Add CORS middleware to allow browser-based requests. Use app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]). This enables cross-origin requests from web browsers.

Mount the static files directory. Use app.mount("/static", StaticFiles(directory="static"), name="static") to serve files from the static directory.

Define a Pydantic model class ImageBase64Request with one field: image_base64 as a string.

Define a GET endpoint at "/" that serves the web UI. Import FileResponse from fastapi.responses. Return FileResponse("static/index.html") to serve the web UI at the root path. This allows users to access the web interface directly at http://localhost:8080/.

Define a GET endpoint at "/health" decorated with @app.get that returns {"status": "healthy"}. Add a docstring explaining this is required by Cloud Run.

Define a POST endpoint at "/check-image" that takes a file parameter of type UploadFile from File(...). The function should be async. Add docstring explaining it checks uploaded image files. First check if file.content_type starts with "image/" and raise HTTPException(400, "File must be an image") if not. In a try block, await file.read() to get image_bytes. Check if the size of image_bytes exceeds settings.max_file_size_mb multiplied by 1024 * 1024 (to convert MB to bytes), and if so raise HTTPException(413, f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"). Then call check_nsfw(image_bytes) to get result, and return JSONResponse(content=result). In except block catch HTTPException and re-raise it, otherwise raise HTTPException(500) with error message.

Define a POST endpoint at "/check-image-base64" that takes a request parameter of type ImageBase64Request. The function should be async. Add docstring explaining it checks base64-encoded images. In a try block, decode the base64 string with base64.b64decode(request.image_base64) to get image_bytes. Check if the size of image_bytes exceeds settings.max_file_size_mb multiplied by 1024 * 1024, and if so raise HTTPException(413, f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"). Then call check_nsfw with those bytes, and return JSONResponse with the result. In except block catch HTTPException and re-raise it, otherwise raise HTTPException(500) with error message.

This creates the web API with endpoints for uploading images directly or sending base64-encoded images, plus health check and web UI endpoints.


### Step 4.5: Create web UI for browser-based testing

Create the web UI files that allow users to test the API through a browser interface without using command-line tools.

Edit the file static/index.html. Create a complete HTML page with a head section containing title "NSFW Image Detection API" and a link to static/style.css. In the body, create a container div with a heading "NSFW Image Detection API", a file input element with type="file" and accept="image/*", a button labeled "Check Image", a div with id="preview" to show the selected image, and a div with id="result" to display the API response. Add a script tag at the end that sources static/script.js.

Edit the file static/style.css. Add styles for the body with font-family, background-color, and padding. Style the container with max-width, margin auto, background white, padding, border-radius, and box-shadow. Style the file input and button with padding, margin, and cursor pointer. Style the preview div to display images with max-width and margin. Style the result div with padding, margin-top, border-radius, and different background colors for safe (green) and unsafe (red) statuses.

Edit the file static/script.js. Add JavaScript code that listens for file input changes and displays a preview of the selected image in the preview div. Add a click handler for the button that reads the selected file, creates a FormData object, appends the file, and sends a POST request to /check-image endpoint. Display the response in the result div, formatting it nicely with the status, reason, confidence, and categories. Show loading state while the request is in progress. Handle errors by displaying error messages in the result div.

This creates a complete web interface that users can access at http://localhost:8080/ to upload images and see the classification results visually.


### Step 5: Run locally and verify with browser testing (CRITICAL VALIDATION CHECKPOINT)

Working directory is the project root.

Start the server with uvicorn app.main:app --reload --port 8080. The --reload flag makes it restart on code changes which is useful during development.

Expected output should show:

    INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
    INFO:     Started reloader process
    INFO:     Started server process
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.

BROWSER TESTING - YOU MUST COMPLETE ALL THESE TESTS BEFORE PROCEEDING:

Test 1 - Web UI Loads: Open a web browser and visit http://localhost:8080. You should see the web UI with a professional-looking interface containing a file upload button, heading "NSFW Image Detection API", and instructions. The interface should have a gradient purple background with a white card container. If the UI doesn't load or looks broken, stop and fix the static files before continuing.

Test 2 - Safe Image Classification: Prepare a clearly safe test image such as a landscape, building, or everyday object. Click the file input, select your safe image. You should see a preview of the image appear on the page. Click "Check Image" button. The button should show "Checking..." while processing. After a few seconds, you should see a green result box with "Safe" status, high confidence (above 90%), and low category scores. If you get "Not Safe" for a clearly safe image, review the custom rules logic in nsfw_checker.py.

Test 3 - NSFW Image Classification: Prepare a test image that should be flagged (use appropriate test images that comply with OpenAI policies). Upload it through the web UI. You should see a red result box with "Not Safe" status, the reason explaining why (e.g., "Sexual content detected"), and high scores in relevant categories. If a concerning image returns "Safe", the moderation API may not be working correctly.

Test 4 - Error Handling: Try uploading a non-image file like a .txt file. You should see an error message. Try uploading an extremely large image (over 25MB if possible). You should see a file size error message.

Test 5 - API Documentation: Visit http://localhost:8080/docs. You should see the auto-generated Swagger UI documentation showing all endpoints: GET /, GET /health, POST /check-image, and POST /check-image-base64. Click "Try it out" on the /health endpoint and execute it. You should get {"status": "healthy"} response.

Test 6 - Command Line Testing (Optional): To test with curl from the command line, first prepare a test image file. Then run:

    curl -X POST http://localhost:8080/check-image -F "file=@test_image.jpg"

Replace test_image.jpg with your actual test image filename.

Expected response for a safe image (example):

    {
      "status": "Safe",
      "reason": "No concerning content detected",
      "confidence": 0.985,
      "categories": {
        "sexual": false,
        "hate": false,
        "violence": false
      },
      "category_scores": {
        "sexual": 0.012,
        "hate": 0.003,
        "violence": 0.001
      }
    }

VALIDATION CHECKPOINT: You MUST successfully complete Tests 1-5 above before proceeding to Step 6 (Docker). If any test fails, debug and fix the issue now while running locally. It is much easier to debug problems in the local Python environment than inside a Docker container. Do not skip these tests.

If you see a JSON response with status, reason, confidence and categories, the API is working correctly with OpenAI. If you get an error, check that your OPENAI_API_KEY is correctly set in the .env file and that you have network access to OpenAI's API.


### Step 6: Create Dockerfile

Create a file named Dockerfile in the project root (no extension).

Write these lines:

    # Use official Python runtime as base
    FROM python:3.11-slim
    
    # Set working directory
    WORKDIR /app
    
    # Install dependencies first (for layer caching)
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy application code
    COPY app/ ./app/
    
    # Copy static files for web UI
    COPY static/ ./static/
    
    # Cloud Run expects the app to listen on PORT env var
    ENV PORT=8080
    
    # Expose port
    EXPOSE 8080
    
    # Run the application
    CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}

The FROM line specifies Python 3.11 slim image which includes Python but has minimal extra packages. The WORKDIR sets /app as the working directory inside the container. Copying requirements.txt before the app code allows Docker to cache the pip install layer so it doesn't reinstall packages every time code changes. The --no-cache-dir flag prevents pip from storing cache which reduces image size. The ENV sets PORT to 8080 as Cloud Run requires. The EXPOSE documents which port the container listens on. The CMD runs uvicorn with --host 0.0.0.0 to listen on all network interfaces (required in containers) and uses the PORT environment variable.

Create a file named .dockerignore to exclude files from the Docker build context:

    .env
    .git
    .gitignore
    __pycache__
    *.pyc
    *.pyo
    *.pyd
    .Python
    venv/
    env/
    tests/
    .pytest_cache
    *.md
    Agents.md

This prevents secrets (.env), version control (.git), Python bytecode, virtual environments, tests, and documentation from being copied into the Docker image.

Create a .gitignore file so secrets and build artifacts aren't committed to version control:

    .env
    __pycache__/
    *.py[cod]
    *$py.class
    venv/
    .venv
    env/
    .pytest_cache/
    .coverage
    htmlcov/
    dist/
    build/
    *.egg-info/


### Step 7: Test Docker container locally

Working directory is the project root.

Build the Docker image with:

    docker build -t nsfw-checker .

The -t flag tags the image with the name "nsfw-checker" and the dot means use the current directory as the build context.

Expected output (abbreviated) should show:

    [+] Building 45.2s (10/10) FINISHED
    => [internal] load build definition
    => => transferring dockerfile
    => [internal] load .dockerignore
    ...
    => => writing image sha256:abc123...
    => => naming to docker.io/library/nsfw-checker

If the build fails, check that the Dockerfile has correct syntax and that requirements.txt exists.

Run the container locally with:

    docker run -p 8080:8080 -e OPENAI_API_KEY=your-actual-key nsfw-checker

Replace your-actual-key with your real OpenAI API key. The -p 8080:8080 maps port 8080 from the container to port 8080 on your host machine. The -e sets the environment variable.

Expected output should show:

    INFO:     Started server process [1]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:8080

Open a new terminal window and test with:

    curl http://localhost:8080/health

Expected response: {"status":"healthy"}

If this works, the Docker container is packaged correctly and ready for Cloud Run. Press Ctrl+C in the first terminal to stop the container.


### Step 8: Deploy to GCP Cloud Run

Prerequisites check before deploying. First verify gcloud CLI is installed with gcloud --version. You should see output showing the Google Cloud SDK version. Verify you're logged in with gcloud auth list. You should see your account with an asterisk indicating active. Set your project with gcloud config set project YOUR_PROJECT_ID replacing YOUR_PROJECT_ID with your actual GCP project ID.

Enable the required APIs with:

    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com

These commands may take a minute to complete.

Deployment working directory is the project root.

Configure Docker to authenticate with Google Container Registry:

    gcloud auth configure-docker

This updates your Docker configuration to use gcloud as a credential helper for gcr.io.

Tag your local image with the GCR path:

    docker tag nsfw-checker gcr.io/YOUR_PROJECT_ID/nsfw-checker:v1

Replace YOUR_PROJECT_ID with your actual GCP project ID. The gcr.io/ prefix indicates Google Container Registry, followed by your project ID, image name, and version tag v1.

Push the image to GCR:

    docker push gcr.io/YOUR_PROJECT_ID/nsfw-checker:v1

Expected output shows:

    The push refers to repository [gcr.io/YOUR_PROJECT_ID/nsfw-checker]
    abc123: Pushed
    def456: Pushed
    v1: digest: sha256:... size: 2345

This uploads all the layers to Google's container registry. The first push takes longer, subsequent pushes only upload changed layers.

Deploy to Cloud Run with:

    gcloud run deploy nsfw-checker \
      --image gcr.io/YOUR_PROJECT_ID/nsfw-checker:v1 \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars OPENAI_API_KEY=your-actual-openai-key \
      --max-instances 10 \
      --memory 512Mi \
      --cpu 1 \
      --timeout 60s \
      --port 8080

Replace YOUR_PROJECT_ID with your project ID and your-actual-openai-key with your real OpenAI API key. The command creates a new service named nsfw-checker on Cloud Run's managed platform in the us-central1 region. The --allow-unauthenticated flag makes it publicly accessible. The --set-env-vars passes the API key. The --max-instances 10 prevents runaway scaling and unexpected costs. The --memory 512Mi allocates enough memory for image processing. The --cpu 1 allocates one virtual CPU. The --timeout 60s allows enough time for OpenAI API calls. The --port 8080 tells Cloud Run which port the container listens on.

Expected output:

    Deploying container to Cloud Run service [nsfw-checker] in project [YOUR_PROJECT_ID] region [us-central1]
    ✓ Deploying... Done.
    ✓ Creating Revision...
    ✓ Routing traffic...
    Done.
    Service [nsfw-checker] revision [nsfw-checker-00001-abc] has been deployed and is serving 100 percent of traffic.
    Service URL: https://nsfw-checker-abc123xyz-uc.a.run.app

The Service URL is your live API endpoint. Copy this URL.

Test the deployed API with:

    curl https://nsfw-checker-abc123xyz-uc.a.run.app/health

Replace the URL with your actual Service URL from the previous command.

Expected response: {"status":"healthy"}

Test image checking with:

    curl -X POST https://nsfw-checker-abc123xyz-uc.a.run.app/check-image -F "file=@test_image.jpg"

You should receive the same JSON response format as in local testing. The API is now live and accessible from anywhere on the internet.


### Step 9: (Optional) Use Secret Manager for API key security

Instead of passing the OpenAI API key as an environment variable which is visible in the Cloud Run console to anyone with access, use Google Secret Manager for better security. Secrets are encrypted at rest and access is logged.

Create a secret:

    echo -n "your-actual-openai-key" | gcloud secrets create openai-api-key --data-file=-

The echo -n prints without a newline, pipe sends it to gcloud secrets create, and --data-file=- reads from stdin. Replace your-actual-openai-key with your real key.

Grant the Cloud Run service account permission to access the secret:

    gcloud secrets add-iam-policy-binding openai-api-key \
      --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com \
      --role=roles/secretmanager.secretAccessor

Replace YOUR_PROJECT_NUMBER with your actual GCP project number (not the project ID, the numeric project number). You can find this in the GCP console or with gcloud projects describe YOUR_PROJECT_ID.

Update the Cloud Run service to use the secret:

    gcloud run services update nsfw-checker \
      --update-secrets OPENAI_API_KEY=openai-api-key:latest

This mounts the secret as an environment variable named OPENAI_API_KEY using the latest version of the secret. The secret value is not visible in the Cloud Run console.

Test that the API still works after this change by calling the health and check-image endpoints. The application code doesn't need to change because it still reads from the OPENAI_API_KEY environment variable.


### Step 10: Create project README

Create a comprehensive README.md file in the project root to document the API for users and developers. The README should include project description, features, local development setup instructions, deployment instructions, API endpoint documentation, configuration options, and cost estimates.

Working directory is the project root.

The complete content for the README.md file is provided in the "README.md Content" section of this ExecPlan (see below in Artifacts and Notes). Create the file README.md and use that content.

Expected outcome: A README.md file exists in the project root with comprehensive documentation that allows new users and developers to understand the project, set it up locally, and deploy it to GCP Cloud Run.


## Validation and Acceptance

The system follows Test-Driven Development with visual validation. Each milestone must be fully validated before proceeding to the next. The system is successfully implemented when all validation criteria below are met.

### Local Development Validation (Complete BEFORE Docker)

These tests must ALL pass before proceeding to containerization. This is the critical TDD validation checkpoint.

Local server starts: Running uvicorn app.main:app --reload --port 8080 from the project root with the virtual environment activated starts a web server at http://localhost:8080. Visiting http://localhost:8080/ shows the web UI with file upload interface displaying a modern, polished design with gradient background and white card container. Visiting /docs shows interactive API documentation with Swagger UI displaying the root GET endpoint (serves web UI), health GET endpoint, check-image POST endpoint, and check-image-base64 POST endpoint.

API classification works: Uploading a test image via POST /check-image returns valid JSON containing these fields: status with value either "Safe" or "Not Safe", reason with a text explanation, confidence with a number between 0 and 1, categories with an object containing boolean flags for each category like sexual, hate, violence, and category_scores with an object containing numeric scores for each category.

Safe image test passes: Uploading a clearly safe image such as a landscape, building, or everyday object returns JSON with "status": "Safe" and confidence above 0.9.

Unsafe image test passes: Uploading an image with nudity or sexual content returns JSON with "status": "Not Safe" and reason mentioning "Sexual content detected" or similar. Use appropriate test images that comply with OpenAI's usage policies.

Browser testing passes: All tests in Step 5 (Web UI loads, safe image classification, NSFW image classification, error handling, API documentation) must pass successfully when running locally without Docker. You must visually confirm the web interface works, upload test images through the browser, and see correct color-coded results (green for safe, red for unsafe).

OpenAI integration verified: The API returns responses with detailed category_scores that show various numeric scores. These scores could only come from OpenAI's moderation model, confirming the integration works. If you see errors like "invalid API key" the API key is wrong. If you see errors like "model not found" the OpenAI API may have changed and the code needs updating per the notes section.

Do not proceed to Docker until all local validation tests pass.

### Docker Validation (Complete AFTER Local, BEFORE Cloud Run)

Docker build succeeds: After completing all local browser testing, running docker build -t nsfw-checker . completes without errors and produces an image.

Container runs correctly: Running docker run -p 8080:8080 -e OPENAI_API_KEY=key nsfw-checker starts the service and it's accessible at localhost:8080. Calling the health endpoint returns the healthy status. The web UI should work identically inside Docker as it did locally.

Do not proceed to Cloud Run until Docker validation passes.

### Cloud Run Validation (Final Production Validation)

Deployment succeeds: After running the gcloud run deploy command, the service is live at a Cloud Run URL like https://nsfw-checker-xyz.run.app. Visiting the URL with /health appended returns {"status":"healthy"}.

Image classification works in production: Using curl or an HTTP client to POST an image to the Cloud Run URL at the /check-image endpoint returns the same JSON structure as local testing. This proves the deployed service works end-to-end including receiving requests, processing images, calling OpenAI, and returning results.

Web UI works in production: Visiting the Cloud Run service URL in a web browser displays the web UI. Uploading an image through the web interface shows the classification result formatted nicely on the page, proving the static file serving and frontend JavaScript work correctly in the deployed environment.


### Testing Commands

From the project root with the service running locally, execute these commands and verify the expected outputs.

Test health endpoint:

    curl http://localhost:8080/health

Expected: {"status":"healthy"}

Test root endpoint (serves web UI):

    curl http://localhost:8080/

Expected: HTML content of the web UI (static/index.html). Note: This endpoint is better tested by opening http://localhost:8080/ in a browser to see the visual interface.

Test image upload with safe image:

    curl -X POST http://localhost:8080/check-image -F "file=@test_safe.jpg"

Expected: {"status":"Safe",...} with high confidence.

Test image upload with NSFW image:

    curl -X POST http://localhost:8080/check-image -F "file=@test_nsfw.jpg"

Expected: {"status":"Not Safe",...} with reason about sexual content.

For the deployed Cloud Run service, replace http://localhost:8080 with your Cloud Run service URL in all the above commands.


### Test Images

Prepare at least three test images before validation.

First, a safe image: Use a landscape photo, architectural shot, or picture of an object with no people. Examples include a sunset, mountain, building facade, or coffee cup.

Second, a borderline image: Use a photo of a person in normal clothing like business attire or casual wear. This tests that the API doesn't over-flag normal photos.

Third, an unsafe image: Use an image that would typically be flagged as NSFW. Ensure compliance with OpenAI's usage policies when testing. If you don't have test NSFW images, you can test with images found in research datasets for content moderation or use stock photos marked as mature content.

Upload each image to both the local API and the deployed Cloud Run API. Verify that the API returns appropriate classifications consistently. Safe images should get "Safe" status, borderline images should typically get "Safe" unless there's concerning content, and NSFW images should get "Not Safe" status with relevant reasons.


## Idempotence and Recovery

### Idempotent Operations

The following operations can be run multiple times safely without causing problems.

Installing dependencies: Running pip install -r requirements.txt multiple times is safe. Pip checks existing packages and only installs or upgrades as needed.

Building Docker image: Running docker build can be run repeatedly. Each build is independent. Docker caches layers so unchanged layers are reused making subsequent builds faster.

Deploying to Cloud Run: Running the same gcloud run deploy command updates the existing service if it exists or creates it if it doesn't exist. There are no duplicate services created. Each deployment creates a new revision and routes traffic to it.

Creating secrets: If gcloud secrets create fails with "already exists" error, use gcloud secrets versions add openai-api-key --data-file=- to add a new version to the existing secret.


### Recovery Paths

If the local server crashes or fails to start, check the terminal logs for error messages which are usually printed to stdout/stderr. Verify the .env file exists and has the correct OPENAI_API_KEY value without extra spaces or quotes. Check that you're in the correct directory and the virtual environment is activated. Restart with uvicorn app.main:app --reload --port 8080.

If Docker build fails, check the Dockerfile syntax carefully for typos. Ensure requirements.txt exists in the project root with valid package versions. Check Docker daemon is running with docker ps. Clear Docker cache and rebuild with docker build --no-cache -t nsfw-checker . if you suspect caching issues.

If Cloud Run deployment fails, first check that the image exists in GCR with gcloud container images list --repository=gcr.io/YOUR_PROJECT_ID. Verify required APIs are enabled with gcloud services list --enabled | grep run. Check service account permissions in the GCP console under IAM. View deployment logs with gcloud run services logs read nsfw-checker to see detailed error messages.

If the API returns errors after deployment, check Cloud Run logs with gcloud run services logs tail nsfw-checker --limit=50 to see recent requests. Verify the environment variable is set with gcloud run services describe nsfw-checker and look for the OPENAI_API_KEY in the environment section. Test your OpenAI API key manually with a simple Python script to ensure it's valid. Redeploy with the correct environment variables if needed.

If OpenAI API calls fail, check that you have network connectivity to api.openai.com. Verify your API key is valid by testing it with a simple request. Check OpenAI's status page for service outages. Review OpenAI's documentation for API changes if you get "model not found" or similar errors.


### Rollback

If a new deployment has problems, Cloud Run maintains previous revisions and you can rollback easily.

To rollback to a previous revision:

    gcloud run services update-traffic nsfw-checker --to-revisions=nsfw-checker-00001-abc=100

Replace nsfw-checker-00001-abc with the revision name you want to rollback to.

List all revisions with:

    gcloud run revisions list --service=nsfw-checker

This shows all revisions with their creation times and traffic percentages. You can also do gradual rollouts by splitting traffic between revisions, for example --to-revisions=nsfw-checker-00002=80,nsfw-checker-00001=20 routes 80 percent to the new revision and 20 percent to the old one.


## Artifacts and Notes

### Example API Response for Safe Image

When testing with a safe image like a beach sunset photograph, the request and response look like this.

Request:

    curl -X POST http://localhost:8080/check-image \
      -H "Content-Type: multipart/form-data" \
      -F "file=@beach_sunset.jpg"

Response:

    {
      "status": "Safe",
      "reason": "No concerning content detected",
      "confidence": 0.992,
      "categories": {
        "sexual": false,
        "hate": false,
        "harassment": false,
        "self-harm": false,
        "sexual/minors": false,
        "hate/threatening": false,
        "violence/graphic": false,
        "self-harm/intent": false,
        "self-harm/instructions": false,
        "harassment/threatening": false,
        "violence": false
      },
      "category_scores": {
        "sexual": 0.008,
        "hate": 0.001,
        "harassment": 0.002,
        "self-harm": 0.0,
        "sexual/minors": 0.0,
        "hate/threatening": 0.0,
        "violence/graphic": 0.001,
        "self-harm/intent": 0.0,
        "self-harm/instructions": 0.0,
        "harassment/threatening": 0.0,
        "violence": 0.003
      }
    }

Note that all categories are false and all scores are very low (near zero). The confidence is high at 0.992 indicating high certainty the image is safe.


### Example API Response for Unsafe Image

When testing with an image containing nudity or sexual content, the response looks different.

Request: Same format as above but with a different image file.

Response:

    {
      "status": "Not Safe",
      "reason": "Sexual content detected",
      "confidence": 0.957,
      "categories": {
        "sexual": true,
        "hate": false,
        "harassment": false,
        "self-harm": false,
        "sexual/minors": false,
        ...
      },
      "category_scores": {
        "sexual": 0.957,
        "hate": 0.002,
        ...
      }
    }

Note that the sexual category is true and the sexual score is very high at 0.957. The status is "Not Safe" and reason explains why. The confidence matches the sexual score showing high certainty.


### Cloud Run Cost Estimate

Cloud Run pricing as of 2025 (verify current rates at cloud.google.com/run/pricing).

Free tier includes the first 2 million requests per month. After free tier, requests cost $0.40 per million requests. CPU time is charged at $0.00002400 per vCPU-second. Memory is charged at $0.00000250 per GiB-second. Minimum charge per request is approximately $0.0000004.

For moderate usage of 10,000 images per month with 1-2 seconds per request, estimated cost is $0.50 to $2.00 per month. Most of this is covered by the free tier.

For high usage of 1 million images per month, estimated cost is $10 to $30 per month depending on request duration and memory usage.

OpenAI API costs are separate. Check OpenAI's pricing page for current moderation API rates. As of late 2024, the moderation API had generous free tiers but verify current pricing.

The total cost for a production deployment serving 10,000 images per month might be $2-5 per month for infrastructure plus OpenAI API costs.


## Interfaces and Dependencies

### Python Dependencies

The requirements.txt file specifies these packages with their versions:

    fastapi==0.115.0          Web framework for building APIs
    uvicorn[standard]==0.30.6  ASGI server to run FastAPI applications
    python-multipart==0.0.12   Enables file upload support in FastAPI
    openai==1.51.0            Official OpenAI Python client library
    pillow==10.4.0            Image processing library for validation
    python-dotenv==1.0.1      Loads environment variables from .env files
    pydantic-settings==2.5.2   Configuration management with validation
    pytest==8.3.3             Testing framework for unit tests
    httpx==0.27.2             HTTP client for testing API endpoints

These versions are current as of November 2025 and include support for OpenAI's latest moderation API features. Always consult OpenAI's documentation at https://platform.openai.com/docs/guides/moderation for the current method to submit images for moderation. If the moderation API doesn't support images directly, use the two-step approach described in the notes section below.


### API Interface Specification

The API exposes these endpoints with the following specifications.

Endpoint POST /check-image accepts multipart/form-data with a field named file containing the binary image file. The response is application/json with this structure: status field contains string "Safe" or "Not Safe" or "Error", reason field contains string with human-readable explanation, confidence field contains number from 0.0 to 1.0, categories field contains object with boolean flags from OpenAI for each category like sexual, hate, violence, category_scores field contains object with numeric scores from 0.0 to 1.0 for each category.

Endpoint POST /check-image-base64 accepts application/json with body containing image_base64 field as a string with the base64-encoded image. The response format is the same as /check-image.

Endpoint GET /health accepts no parameters and returns application/json with body {"status": "healthy"}. This endpoint is used by Cloud Run for health checks and by monitoring systems.

Endpoint GET / serves the web UI by returning the static/index.html file (text/html). This provides a browser-based interface for uploading and testing images visually.


### Module Interface for nsfw_checker.py

The nsfw_checker module provides these functions.

Main function check_nsfw takes image_bytes parameter of type bytes and returns a Dict. The input is raw image file bytes. The output is a dictionary with this structure: status key has string value "Safe", "Not Safe", or "Error", reason key has string explanation of the decision, confidence key has float value from 0.0 to 1.0, categories key has dict with boolean category flags from OpenAI, category_scores key has dict with float confidence scores from OpenAI.

Helper function encode_image_to_base64 takes image_bytes of type bytes and returns a str. It converts the image to base64 encoding for transmission to APIs.

Helper function check_image_with_openai takes image_bytes of type bytes and returns a Dict. It calls the OpenAI moderation API and returns the raw moderation result.

Helper function apply_custom_rules takes moderation_result of type Dict and returns a Tuple of (str, str, float) representing status, reason, and confidence. It applies business logic on top of OpenAI's results to make the final decision.


### Configuration Interface for config.py

The config module uses Pydantic Settings to load and validate configuration from environment variables.

The Settings class inherits from BaseSettings and has these fields: openai_api_key as required string with no default (raises error if missing), port as int with default value 8080.

The nested Config class specifies env_file = ".env" so the settings are loaded from the .env file automatically.

Access the settings by importing: from app.config import settings. Then access values with settings.openai_api_key and settings.port.


### GCP Resource Requirements

To deploy this application on GCP Cloud Run, you need these resources.

Project: An active GCP project with billing enabled. You must be an owner or editor of the project.

APIs: Enable Cloud Run API for running containers and Container Registry API for storing Docker images. Enable these with gcloud services enable commands.

IAM permissions: The service account needs these roles: roles/run.admin to deploy Cloud Run services, roles/storage.admin to push images to GCR, roles/secretmanager.secretAccessor if using Secret Manager for the API key.

Compute resources: The Cloud Run service needs minimum 512 MiB memory for processing images with Pillow, 1 vCPU is sufficient for this workload, default concurrency of 80 requests per instance, timeout of 60 seconds to allow time for OpenAI API calls which can take 5-10 seconds, max instances set to 10 to prevent unexpected costs from runaway scaling.

Network: Cloud Run provides automatic HTTPS with managed certificates. No VPC or networking configuration is required for public APIs.


## README.md Content

Create a file named README.md in the project root with this content:

    # NSFW Image Detection API
    
    A REST API service that detects NSFW (Not Safe For Work) content in images using OpenAI's Moderation API with custom business rules.
    
    ## Features
    
    - Fast image classification: "Safe" or "Not Safe"
    - Detailed reasoning and confidence scores
    - Support for file upload and base64-encoded images
    - Deployed on Google Cloud Run with auto-scaling
    - Interactive API documentation at `/docs`
    
    ## Local Development
    
    ### Prerequisites
    
    - Python 3.11+
    - OpenAI API key
    - Docker (for containerization)
    
    ### Setup
    
    1. Clone repository
    2. Create virtual environment: `python -m venv venv`
    3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
    4. Install dependencies: `pip install -r requirements.txt`
    5. Copy `.env.example` to `.env` and add your OpenAI API key
    6. Run: `uvicorn app.main:app --reload --port 8080`
    7. Visit `http://localhost:8080/docs` for API documentation
    
    ### Testing
    
    ```bash
    # Health check
    curl http://localhost:8080/health
    
    # Check image
    curl -X POST http://localhost:8080/check-image -F "file=@test_image.jpg"
    ```
    
    ## Deployment to GCP Cloud Run
    
    ### Prerequisites
    
    - GCP project with billing enabled
    - `gcloud` CLI installed and authenticated
    
    ### Deploy
    
    1. Build Docker image: `docker build -t nsfw-checker .`
    2. Tag: `docker tag nsfw-checker gcr.io/YOUR_PROJECT_ID/nsfw-checker:v1`
    3. Push: `docker push gcr.io/YOUR_PROJECT_ID/nsfw-checker:v1`
    4. Deploy:
       ```bash
       gcloud run deploy nsfw-checker \
         --image gcr.io/YOUR_PROJECT_ID/nsfw-checker:v1 \
         --platform managed \
         --region us-central1 \
         --allow-unauthenticated \
         --set-env-vars OPENAI_API_KEY=your-key \
         --max-instances 10
       ```
    
    ## API Endpoints
    
    ### `POST /check-image`
    
    Upload image file for NSFW detection.
    
    **Request**: `multipart/form-data` with `file` field
    
    **Response**:
    ```json
    {
      "status": "Safe",
      "reason": "No concerning content detected",
      "confidence": 0.985,
      "categories": {...},
      "category_scores": {...}
    }
    ```
    
    ### `POST /check-image-base64`
    
    Send base64-encoded image for NSFW detection.
    
    **Request**:
    ```json
    {
      "image_base64": "iVBORw0KGgoAAAANS..."
    }
    ```
    
    **Response**: Same as `/check-image`
    
    ### `GET /health`
    
    Health check endpoint.
    
    **Response**: `{"status": "healthy"}`
    
    ## Configuration
    
    Set environment variables:
    - `OPENAI_API_KEY`: Your OpenAI API key (required)
    - `PORT`: Server port (default: 8080)
    
    ## Cost Estimation
    
    - Cloud Run: ~$0.50-$2.00/month for moderate usage (free tier covers first 2M requests)
    - OpenAI API: Check OpenAI pricing for moderation API costs
    
    ## License
    
    (Add your license here)

This README provides clear documentation for users to set up, run, and deploy the API.


## Notes on OpenAI Moderation API Evolution

Important: The OpenAI API evolves frequently. As of November 2025, verify the current method for image moderation before implementing.

First check if images are supported directly by the Moderation API endpoint. Visit https://platform.openai.com/docs/guides/moderation and look for image support.

If the moderation API doesn't accept images directly, you need a two-step process. Step one is to use the Chat API with vision capabilities. Call openai.chat.completions.create with model "gpt-4-vision-preview" or similar vision model, pass the image as a base64 data URI in the messages content, and ask it to describe the image objectively. Step two is to moderate the description by calling openai.moderations.create with the text description from step one as input.

Alternative approach is to use the Chat API with a system prompt instructing it to classify NSFW content directly. Use a vision model and provide a detailed prompt like "You are a content moderator. Classify this image as safe or unsafe. Unsafe includes: nudity, sexual content, violence, content involving minors. Respond with JSON including status, reason, and confidence." Parse the JSON response and use it directly.

Current best practice as of November 2025 should be verified with OpenAI documentation. The openai.moderations.create() endpoint may or may not accept images directly. The plan's app/nsfw_checker.py code assumes image support. If unavailable, modify the check_image_with_openai function to implement the two-step approach described above.

When implementing, test with sample images first to verify the OpenAI integration works before deploying to production. If you encounter errors like "invalid input type" or "image not supported", switch to the two-step vision plus moderation approach.


---

Plan Revision History:

- 2025-11-13: Initial plan created. Assumes OpenAI Moderation API with image support and GCP Cloud Run deployment. User specified GCP with project number and ID. Plan follows PLANS.md format with all required sections (Progress, Surprises & Discoveries, Decision Log, Outcomes & Retrospective). Plan is self-contained for novice implementation. Includes note about OpenAI API potentially not supporting images directly and alternative approaches. Formatted without nested code fences per PLANS.md requirements.

- 2025-11-13: Added simple web UI for browser-based testing per user request. User wanted an easy way to test without always using command line. Web UI includes static HTML/CSS/JS files served by FastAPI, with drag-and-drop file upload, visual feedback, and formatted results display. Updated project structure, progress checklist, decision log, Dockerfile, and all relevant sections. Command-line testing remains available alongside web UI.

- 2025-11-13: Fixed critical implementation gaps identified in plan review. Updated Step 3 to use modern OpenAI SDK client pattern (OpenAI client instance) instead of deprecated global API key pattern. Added Step 4.5 with complete web UI implementation instructions for creating static/index.html, static/style.css, and static/script.js files. Updated Step 4 to include CORS middleware configuration and static file mounting. Updated Step 1 to include creating static directory. Updated Step 6 Dockerfile to copy static files. Updated validation section to include web UI testing. These changes ensure the plan is fully implementable end-to-end without missing critical components.

- 2025-11-13: Restructured plan to follow Test-Driven Development (TDD) methodology with visual browser testing. Updated Milestone 1 to emphasize that browser testing is part of local development, not an afterthought. Added comprehensive browser testing requirements in Step 5 with six explicit tests that must pass before containerization. Made Step 5 a "CRITICAL VALIDATION CHECKPOINT" requiring successful visual testing of the web UI, safe image classification, NSFW image classification, error handling, and API documentation before proceeding to Docker. Updated Milestone 2 to explicitly state it should only begin after local browser testing succeeds. Updated Validation and Acceptance section to number browser testing as Fifth (before Docker) and Docker validation as Sixth (after browser testing). This ensures the application is proven to work correctly in the simpler local environment before adding Docker complexity, following TDD best practices and reducing debugging difficulty.

- 2025-11-13: Fixed inconsistencies and improved plan clarity based on comprehensive review. (1) Updated "Interfaces and Dependencies" section to use consistent package versions matching Step 1 (fastapi==0.115.0, openai==1.51.0, etc.). (2) Resolved conflicting root endpoint descriptions - clarified that GET "/" serves web UI HTML, not JSON, in both Testing Commands and API Interface sections. (3) Updated "Context and Orientation" to accurately reflect current repository state including CLAUDE.md, .agent/PLANS.md, and other existing files. (4) Added Step 10 to create README.md as an explicit concrete step referencing the README content in Artifacts section. (5) Enhanced Step 3 with OpenAI API verification guidance and fallback approach warning if direct image moderation is unavailable. (6) Restructured Step 3 into five clear sub-steps (3a-3e) for better readability: imports/setup, image encoding, OpenAI integration, custom rules, and main entry point. (7) Reorganized "Validation and Acceptance" section from numbered list (First through Tenth) into three logical groups: Local Development Validation, Docker Validation, and Cloud Run Validation, with clear progression gates between milestones. These improvements enhance plan usability, eliminate confusion, and maintain full PLANS.md compliance.

