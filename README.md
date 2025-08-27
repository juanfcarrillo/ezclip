# EZClip

A FastAPI-based video clipping service that uses AI to understand and extract highlights from videos.

## Features

- Video analysis using Google Gemini AI
- Automatic highlight extraction
- Video clipping with FFmpeg
- YouTube video downloading
- Background processing with Celery
- Firebase integration for data storage
- Cloudflare R2 storage for video files

## Environment Setup

### Required Environment Variables

The application requires two main environment variables that will be automatically converted to files during container startup:

#### CREDENTIALS
Firebase service account credentials in JSON format. Can be provided as:
- Raw JSON string
- Base64 encoded JSON

Example:
```bash
export CREDENTIALS='{"type":"service_account","project_id":"your-project-id",...}'
```

Or base64 encoded:
```bash
export CREDENTIALS=$(echo '{"type":"service_account",...}' | base64)
```

#### COOKIES
YouTube cookies in Netscape format for video downloading. Can be provided as:
- Raw cookie file content
- Base64 encoded content

Example:
```bash
export COOKIES='# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1234567890	cookie_name	cookie_value'
```

Or base64 encoded:
```bash
export COOKIES=$(cat cookies.txt | base64)
```

### Setting Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   CREDENTIALS='your-firebase-credentials-json'
   COOKIES='your-youtube-cookies'
   ```

3. Load the environment variables:
   ```bash
   source .env
   ```

## Docker Deployment

### Quick Start

1. Set your environment variables (see above)
2. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

The application will:
1. Run the initialization script to create `credentials.json` and `cookies.txt`
2. Start the FastAPI application on port 8081
3. Start the Celery worker for background processing
4. Start Redis for task queuing

### Services

- **API**: FastAPI application (http://localhost:8081)
- **Worker**: Celery worker for video processing
- **Redis**: Task queue and cache

## Development

### Prerequisites

- Python 3.11+
- Poetry
- FFmpeg
- Redis (for local development)

### Local Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. Run the initialization script:
   ```bash
   python init_env_files.py
   ```

4. Start Redis:
   ```bash
   redis-server
   ```

5. Start the API:
   ```bash
   poetry run uvicorn app.main.app:app --reload --port 8081
   ```

6. Start the Celery worker:
   ```bash
   poetry run celery -A celery_worker.celery_app worker --loglevel=info -Q clipping
   ```

## API Endpoints

### Health Check
- `GET /` - Basic health check

### Video Processing
- `POST /clip` - Submit a video for clipping
- `GET /clip/{task_id}` - Get clipping task status

## Architecture

The application follows clean architecture principles:

- **Domain**: Core business logic (`app/clipping/domain/`)
- **Use Cases**: Application services (`app/clipping/use_cases/`)
- **Infrastructure**: External integrations (`app/clipping/infrastructure/`)
- **Services**: Application services (`app/clipping/services/`)

## Testing

Run tests with:
```bash
poetry run pytest
```

## Project Structure

```
ezclip/
├── app/
│   ├── clipping/           # Main clipping module
│   │   ├── domain/         # Domain models and interfaces
│   │   ├── infrastructure/ # External service implementations
│   │   ├── services/       # Application services
│   │   └── use_cases/      # Business use cases
│   ├── main/               # Application entry point
│   └── shared/             # Shared utilities
├── tests/                  # Test files
├── init_env_files.py       # Environment initialization script
├── init_env_files.sh       # Shell version of init script
├── entrypoint.sh           # Docker entrypoint
├── docker-compose.yml      # Docker services configuration
├── Dockerfile              # Container image definition
└── pyproject.toml          # Python dependencies
```
