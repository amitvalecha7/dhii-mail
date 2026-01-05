# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY a2ui_integration/client/package*.json ./
RUN npm install
COPY a2ui_integration/client/ .
RUN npm run build

# Stage 2: Python Backend
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from Stage 1 to /app/static
# This location is checked by main.py to serve the frontend
COPY --from=frontend-builder /app/dist /app/static

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8005/health || exit 1

EXPOSE 8005

CMD ["python", "main.py", "--port", "8005"]
