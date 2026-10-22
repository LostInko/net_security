#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# 1. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate virtual environment
source venv/bin/activate

# 3. Ensure required packages are installed
echo "Checking dependencies..."
pip install --quiet hypercorn aioquic

# 4. Generate certificate if missing
if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
    echo "Generating self-signed certificate for server.netsec.lab..."
    openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
      -keyout key.pem -out cert.pem \
      -subj "/CN=server.netsec.lab" \
      -addext "subjectAltName=DNS:server.netsec.lab"
fi

# 5. Start the server
echo "Starting HTTP/3 and HTTPS server on port 4433..."
python https_quic.py