FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 python3-pip python3-venv \
    clang make git \
    libprotobuf-dev protobuf-compiler \
    libnl-3-dev libnl-route-3-dev libcap-dev libseccomp-dev \
    pkg-config flex bison \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy application files
COPY app/main.py ./main.py         
COPY scripts/ ./scripts
COPY sandbox/ ./sandbox
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Build and install nsjail
RUN git clone https://github.com/google/nsjail.git && \
    cd nsjail && \
    make && \
    cp nsjail /usr/local/bin/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8080

# Start Flask app via entrypoint
ENTRYPOINT ["/entrypoint.sh"]
