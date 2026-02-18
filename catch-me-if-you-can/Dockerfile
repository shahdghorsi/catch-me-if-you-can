FROM europe-docker.pkg.dev/prj-vm-p-tool-gar-01/shared-docker-external-shared-images/chainguard/wolfi-base:57428116d2d7c27d1d4de4103e19b40bb8d2942ff6dff31b900e55efedeb7e30
WORKDIR /app

COPY zscaler.crt /etc/ssl/certs/
RUN cat /etc/ssl/certs/zscaler.crt >> /etc/ssl/certs/ca-certificates.crt
RUN apk update && apk add --no-cache \
    bash \
    git \
    unzip \
    curl \
    libstdc++ \
    libgcc

ENV UV_NATIVE_TLS=true
ENV UV_HTTP_TIMEOUT=900
ENV PYTHONUNBUFFERED=true
ENV UV_PYTHON="3.10"
ENV UV_LINK_MODE=copy
ENV PATH="/root/.local/bin:$PATH"
ENV UV_DEFAULT_INDEX=https://europe-west2-python.pkg.dev/prj-vo-aa-p-mlops-gar/pypi-virtual/simple
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# default and preview flags make sure `python3` is available
RUN --mount=type=cache,target=/root/.cache/uv \
    uv python install 3.10 --default --preview

# Create venv and install dependencies
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r requirements.txt

# Copy application
COPY . .
RUN mkdir -p instance

ENV PORT=8080
EXPOSE 8080

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:8080", "app:app"]
