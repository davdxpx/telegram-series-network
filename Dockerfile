FROM python:3.12-slim

WORKDIR /app

# Set environment variables
# PYTHONUNBUFFERED=1 ensures logs are sent to stdout immediately without buffering
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start command: Use Uvicorn to run the FastAPI application
# This triggers the 'lifespan' event which starts the bot polling loop
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
