FROM python:3

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libgl1-mesa-dri \
    libglx-mesa0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

COPY pyproject.toml .

# Install dependencies
RUN uv sync --system

COPY app.py .
COPY video.py .
COPY templates ./templates
COPY static ./static

ARG workers=4
ENV WORKERS=${workers}

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0", "app:app"]