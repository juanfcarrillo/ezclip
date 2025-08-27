# ezclip deployment Dockerfile
FROM python:3.11-slim

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

# Expose FastAPI port
EXPOSE 8081

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
