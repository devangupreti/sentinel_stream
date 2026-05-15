# Use a slim Python image for performance
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for ONNX)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set the PYTHONPATH so 'src' is always found
ENV PYTHONPATH=/app

# Expose the API port
EXPOSE 8000

# Command to run the API
CMD ["python", "run_api.py"]