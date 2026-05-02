FROM python:3

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg libglib2.0-0 libgl1-mesa-dri libglx-mesa0 curl \
    && rm -rf /var/lib/apt/lists/*

# install uv
ADD https://astral.sh/uv/install.sh /install.sh
RUN sh /install.sh && rm /install.sh
ENV PATH="/root/.local/bin:$PATH"

# copy only dependency files first (better caching)
COPY pyproject.toml uv.lock* ./

# install dependencies into uv-managed environment
RUN uv sync --frozen

# copy app
COPY . .

ARG workers=4
ENV WORKERS=${workers}

CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0", "app:app"]
