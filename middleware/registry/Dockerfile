FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install --prefix=/install flask==3.0.0

FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Copy installed packages
COPY --from=builder /install /usr/local

COPY app.py .

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
