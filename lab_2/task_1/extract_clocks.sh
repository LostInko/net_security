#!/bin/bash

PCAP="/tmp/capture-6.pcap"

# Capture the clocks: stream, time, tsval
tshark  -r "$PCAP" -Y "ip.src == 198.51.100.7 && tcp.options.timestamp.tsval"  \
        -T "fields" -E header=y \
        -e tcp.stream -e frame.time_relative -e tcp.options.timestamp.tsval > clock.tsv

tshark  -r "$PCAP" -Y 'http.request' \
        -T fields -E header=y -e tcp.stream -e http.request.line > http.tsv

wc -l http.tsv
head -3 http.tsv

echo "capture finished"