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
