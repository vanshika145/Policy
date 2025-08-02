# Use slim Python base image with build tools
FROM python:3.10-slim

# Install system dependencies for ML libraries
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
    libgomp1 \
    libblas-dev \
    liblapack-dev \
    gfortran \
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

# Create uploads directory
RUN mkdir -p uploads

# Expose the port Uvicorn will run on
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Start command using our Docker startup script
CMD ["python", "start_docker.py"] 