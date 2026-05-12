FROM python:3.12-slim

WORKDIR /app

COPY app2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app2/app/ ./app/
COPY app2/run.py .

VOLUME ["/app/instance"]

EXPOSE 5000

CMD ["python", "run.py"]
