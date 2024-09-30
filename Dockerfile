FROM python:3

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY app.py .
COPY templates ./templates

ARG workers=4

CMD ["gunicorn", "-w", workers, "app:app"]