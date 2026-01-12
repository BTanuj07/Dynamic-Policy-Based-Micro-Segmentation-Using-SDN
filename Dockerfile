# Multi-stage Docker build for SDN Cloud Security
FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    net-tools \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 6653 5000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1

# Default command
CMD ["python", "controller.py"]

# Production stage
FROM base as production

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash sdn_user
RUN chown -R sdn_user:sdn_user /app
USER sdn_user

# Run the application
CMD ["python", "controller.py"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov black flake8

# Keep root user for development
CMD ["python", "controller.py"]