#!/bin/bash

PCAP="./capture-6.pcap"

# Extract JA4 fingerprint
echo "=== Target JA4 Key ==="
# Extracts raw data and put it in a pipe\
JA4_KEY=$(cat "$PCAP" | tshark -r - \
  -Y 'tls.handshake.type == 1 && tls.handshake.extensions_server_name contains "syncbridge.example"' \
  -T fields -e tls.handshake.ja4 | head -n 1)

echo "Target JA4: $JA4_KEY"

# Extract all SNIs matching this JA4 fingerprint
SNIS=$(cat "$PCAP" | tshark -r - \
  -Y "tls.handshake.type == 1 && tls.handshake.ja4 == \"$JA4_KEY\"" \
  -T fields -e tls.handshake.extensions_server_name)

echo "=== Matching SNIs ($(echo "$SNIS" | wc -l)) ==="
echo "$SNIS"

# Take the first label (6 hex digits) of each SNI and join them
TOKEN=$(echo "$SNIS" | cut -d'.' -f1 | tr -d '\n')
echo "=== Flag ==="
echo "netsec{$TOKEN}"

echo "finish"