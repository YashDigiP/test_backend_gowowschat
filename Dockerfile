# Use Python 3.11 slim image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Set the port for Cloud Run
EXPOSE 8080

# Run using gunicorn on port 8080 if Flask or FastAPI is used
CMD exec gunicorn --bind :8080 server:app --workers=3 --timeout=1000
