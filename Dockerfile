FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

# Install Node.js 20 (needed for building Vite frontend)
RUN apt update && apt install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt install -y nodejs && \
    apt clean && rm -rf /var/lib/apt/lists/*


# Set work directory
WORKDIR /app

# Copy only dependency files first for better Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync

# Copy rest of the application
COPY . .

# Build frontend
RUN cd frontend && npm install && npm run build

# Expose FastAPI port
EXPOSE 8000

# Start the app
CMD ["uv", "run", "python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]