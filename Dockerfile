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
