#!/bin/bash

SANDBOX_RUNTIME="/mnt/sandbox"

# Create sandbox and tmp directory
mkdir -p "${SANDBOX_RUNTIME}/tmp"
cp -r /app/sandbox/* "${SANDBOX_RUNTIME}/"
chmod -R u+rwX,go-rwx "${SANDBOX_RUNTIME}"
chmod 777 "${SANDBOX_RUNTIME}/tmp"  # Allow script writing/execution

# Start the Flask app
exec python3 /app/main.py
