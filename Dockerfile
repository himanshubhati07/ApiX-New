# Multi-stage Dockerfile for FastAPI app.
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd -m appuser
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 47375
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:47375/health').read()"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "47375"]
