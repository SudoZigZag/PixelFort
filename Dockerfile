# Start from official Python image for ARM64
FROM arm64v8/python:3.11-slim AS development

# Set working directory inside container
WORKDIR /app

# Copy requirements first (Docker caching optimization)
COPY api/requirements.txt .
COPY api/requirements-test.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    iproute2 \
    net-tools \
    iputils-ping \
    dnsutils \
    tcpdump \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt
 # Test requirements
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy application code
COPY api/ /app/api/

# Tell Docker which port to expose
EXPOSE 8000 8080

# Command to run when container starts
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

