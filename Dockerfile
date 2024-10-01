FROM python:3

RUN apt-get update && apt-get install -y ffmpeg libglib2.0-0 libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY app.py .
COPY video.py .
COPY templates ./templates
COPY static ./static

ARG workers=4
ENV WORKERS=${workers}

CMD gunicorn -w $WORKERS -b 0.0.0.0 app:app