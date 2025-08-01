# Use slim Python base image with build tools
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Now copy your source code
COPY . .

# Expose the port Uvicorn will run on
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app:/app/server
ENV PORT=8000

# Start command
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"] 