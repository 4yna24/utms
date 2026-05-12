FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY run.py .

VOLUME ["/app/instance"]

EXPOSE 5000

CMD ["python", "run.py"]
