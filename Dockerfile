# ezclip deployment Dockerfile
FROM python:3.11-slim

# Build arguments for credentials
ARG CREDENTIALS
ARG COOKIES

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files and install dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

# Make init scripts executable
RUN chmod +x init_env_files.sh entrypoint.sh

# Create credentials and cookies files from build args
RUN if [ -n "$CREDENTIALS" ]; then \
        echo "$CREDENTIALS" | base64 -d > credentials.json 2>/dev/null || echo "$CREDENTIALS" > credentials.json; \
    fi
RUN if [ -n "$COOKIES" ]; then \
        echo "$COOKIES" | base64 -d > cookies.txt 2>/dev/null || echo "$COOKIES" > cookies.txt; \
    fi

# Expose FastAPI port
EXPOSE 8081
