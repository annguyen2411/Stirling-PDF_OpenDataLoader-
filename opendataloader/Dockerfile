FROM python:3.11-slim

# Install Default JRE headless (Java 17/21, required by opendataloader-pdf)
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    opendataloader-pdf \
    fastapi \
    uvicorn \
    python-multipart \
    watchdog

COPY app.py /app/app.py

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
