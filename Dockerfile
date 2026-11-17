FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY artifacts ./artifacts
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH" MODEL_PATH=/app/artifacts/model.joblib
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')" || exit 1
CMD ["uvicorn", "nameresolve.api:app", "--host", "0.0.0.0", "--port", "8000"]