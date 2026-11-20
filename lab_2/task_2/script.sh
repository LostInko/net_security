#!/bin/bash

PCAP="./capture-6.pcap"

# Dynamically extract JA4 fingerprint for syncbridge.example
echo "=== Target JA4 Key ==="
# Extracts raw data and put it in a pipe\
j4_KEY=$(cat "$PCAP" | tshark -r - -Y 'tls.handshake.extensions_server_name contains "syncbridge.example"' -T fields -e tls.handshake.ja4 | head -n 1)
echo "$j4_KEY"

# Extract all SNIs matching this JA4 fingerprint
echo "=== Matching Malware SNIs ==="
cat "$PCAP" | tshark -r - -Y "tls.handshake.ja4 == \"$j4_KEY\"" -T fields -e tls.handshake.extensions_server_name

echo "finish"