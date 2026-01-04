FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Copy installed packages
COPY --from=builder /install /usr/local

COPY . .

USER appuser

EXPOSE 8000

CMD ["python", "app.py"]
