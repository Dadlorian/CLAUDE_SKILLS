#!/bin/bash
# Automated Network Packet Capture Script
# Captures packets with rotation and compression

set -e

# Configuration
INTERFACE=${1:-eth0}
CAPTURE_DIR="/var/captures/network"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAX_FILESIZE=500  # MB
MAX_FILES=100
RETAIN_DAYS=30

# Create directory if needed
mkdir -p "$CAPTURE_DIR"

# Function to rotate old captures
rotate_old_captures() {
    echo "Rotating old capture files..."
    # Delete captures older than retention period
    find "$CAPTURE_DIR" -name "capture_*.pcap" -mtime +$RETAIN_DAYS -delete
    find "$CAPTURE_DIR" -name "capture_*.pcap.gz" -mtime +$RETAIN_DAYS -delete

    # Compress uncompressed files older than 7 days
    find "$CAPTURE_DIR" -name "capture_*.pcap" -mtime +7 -exec gzip -9 {} \;
}

# Function to start continuous capture
start_continuous_capture() {
    local interface=$1
    local output_dir=$2

    echo "Starting packet capture on $interface"
    echo "Output directory: $output_dir"
    echo "Max file size: ${MAX_FILESIZE}MB"
    echo "Max files: $MAX_FILES"

    # Use tcpdump with rotation
    tcpdump -i "$interface" \
        -w "$output_dir/capture_%Y%m%d_%H%M%S.pcap" \
        -G 3600 \
        -C $((MAX_FILESIZE)) \
        -W $MAX_FILES \
        'not (arp or broadcast or multicast)' \
        &

    CAPTURE_PID=$!
    echo "Capture process started with PID: $CAPTURE_PID"

    # Cleanup function
    cleanup() {
        echo "Stopping capture..."
        kill $CAPTURE_PID 2>/dev/null || true
        wait $CAPTURE_PID 2>/dev/null || true
        echo "Capture stopped"
        exit 0
    }

    # Setup signal handlers
    trap cleanup SIGTERM SIGINT

    # Run indefinitely with periodic cleanup
    while true; do
        sleep 3600  # Check every hour
        rotate_old_captures
    done
}

# Function to capture for specific duration
start_timed_capture() {
    local interface=$1
    local duration=$2  # seconds
    local output_file=$3

    echo "Capturing for $duration seconds on $interface"

    # Timeout wrapper ensures capture stops
    timeout $((duration + 10)) tcpdump \
        -i "$interface" \
        -w "$output_file" \
        'not (arp or broadcast or multicast)' || true

    if [ -f "$output_file" ]; then
        local size=$(du -h "$output_file" | cut -f1)
        echo "Capture complete: $size"

        # Optionally compress if large
        if [ $(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file") -gt 10485760 ]; then
            echo "Compressing capture file..."
            gzip -9 "$output_file"
            echo "Compressed to: ${output_file}.gz"
        fi
    else
        echo "Error: Capture file not created"
        exit 1
    fi
}

# Function to capture specific traffic
capture_specific_traffic() {
    local interface=$1
    local filter=$2  # tcpdump filter
    local output_file=$3
    local duration=${4:-300}  # default 5 minutes

    echo "Capturing $filter traffic for ${duration}s"
    echo "Filter: $filter"

    timeout $((duration + 10)) tcpdump \
        -i "$interface" \
        -w "$output_file" \
        -nn \
        -X \
        "$filter" || true

    if [ -f "$output_file" ]; then
        echo "Capture saved to: $output_file"
    fi
}

# Function to analyze captured traffic
analyze_capture() {
    local pcap_file=$1

    if [ ! -f "$pcap_file" ]; then
        echo "Error: File not found: $pcap_file"
        exit 1
    fi

    echo "=== Packet Capture Analysis ==="
    echo "File: $pcap_file"
    echo "Size: $(du -h $pcap_file | cut -f1)"
    echo ""

    echo "=== Summary ==="
    tcpdump -r "$pcap_file" -q | wc -l | xargs echo "Total packets:"
    echo ""

    echo "=== Top Source IPs ==="
    tcpdump -r "$pcap_file" -nn 'ip' | awk '{print $1}' | \
        sort | uniq -c | sort -rn | head -10
    echo ""

    echo "=== Top Destination IPs ==="
    tcpdump -r "$pcap_file" -nn 'ip' | awk '{print $(NF-2)}' | \
        sort | uniq -c | sort -rn | head -10
    echo ""

    echo "=== Protocol Distribution ==="
    tcpdump -r "$pcap_file" -q | awk '{print $5}' | sed 's/,.*//' | \
        sort | uniq -c | sort -rn | head -10
    echo ""

    echo "=== Top Ports ==="
    tcpdump -r "$pcap_file" -nn 'tcp or udp' | \
        awk -F. '{print $(NF-1)"."$NF}' | \
        sort | uniq -c | sort -rn | head -10
}

# Main script logic
case "${2:-continuous}" in
    continuous)
        # Continuous capture with rotation
        rotate_old_captures
        start_continuous_capture "$INTERFACE" "$CAPTURE_DIR"
        ;;
    timed)
        # Capture for specified duration
        duration=${3:-300}
        output_file="$CAPTURE_DIR/capture_${TIMESTAMP}.pcap"
        start_timed_capture "$INTERFACE" "$duration" "$output_file"
        ;;
    filter)
        # Capture specific traffic
        filter="$3"
        duration=${4:-300}
        output_file="$CAPTURE_DIR/capture_${TIMESTAMP}.pcap"
        capture_specific_traffic "$INTERFACE" "$filter" "$output_file" "$duration"
        ;;
    analyze)
        # Analyze existing capture
        analyze_capture "$3"
        ;;
    cleanup)
        # Clean old files
        rotate_old_captures
        ;;
    *)
        echo "Network Packet Capture Automation Script"
        echo ""
        echo "Usage: $0 [interface] [mode] [options]"
        echo ""
        echo "Modes:"
        echo "  continuous [dir]  - Continuous capture with rotation (default)"
        echo "  timed [seconds]    - Capture for specified duration"
        echo "  filter 'filter' [duration] - Capture traffic matching filter"
        echo "  analyze file.pcap  - Analyze captured traffic"
        echo "  cleanup            - Clean old capture files"
        echo ""
        echo "Examples:"
        echo "  $0 eth0 continuous          # Continuous capture on eth0"
        echo "  $0 eth0 timed 600           # Capture for 10 minutes"
        echo "  $0 eth0 filter 'tcp port 443' 300  # Capture HTTPS"
        echo "  $0 eth0 analyze capture.pcap # Analyze capture"
        exit 1
        ;;
esac

---

**Script Type**: Bash Automation
**Purpose**: Network packet capture with rotation and analysis
**Requirements**: tcpdump, gzip
**Features**: Auto-rotation, compression, analysis, filtering
