#!/bin/bash

LOG_DIR="."
MAX_SIZE_MB=5
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "============================================================"
echo "📝 ZANNIE ECOSYSTEM LOG MONITOR & HEALTH DIAGNOSTIC MATRIX"
echo "  Timestamp Check: $TIMESTAMP"
echo "============================================================"

# Define targets to actively monitor
declare -A LOG_FILES
LOG_FILES=(
    ["Path A: Lead Harvester"]="scraper.log"
    ["Path B: Crypto Signal Feed"]="crypto.log"
    ["Path C: Paystack Checkout Gateway"]="gateway.log"
    ["Path D: Physics Analytical Portal"]="physics.log"
)

for service in "${!LOG_FILES[@]}"; do
    log_file="${LOG_FILES[$service]}"
    
    echo -e "\n🔍 Analyzing File State: \e[36m$log_file\e[0m ($service)"
    
    if [ ! -f "$log_file" ]; then
        echo "   ○ Status: Log file has not materialized yet (service may not have output records)."
        continue
    fi

    # Calculate size boundary parameters cleanly
    file_size_kb=$(du -k "$log_file" | cut -f1)
    file_size_mb=$(echo "scale=2; $file_size_kb / 1024" | bc)
    
    echo "   ▪️ Disk Footprint: ${file_size_mb}MB (${file_size_kb} KB)"
    
    # Check for core runtime crash patterns inside the text traces
    echo "   ▪️ Error Scan Summary:"
    error_count=$(egrep -i -c "error|exception|fail|traceback" "$log_file")
    if [ "$error_count" -gt 0 ]; then
        echo -e "     \e[31m[WARN]\e[0m Found $error_count abnormal status descriptors in logging traces."
        echo "     Recent Critical Trailing Vectors:"
        egrep -i "error|exception|fail|traceback" "$log_file" | tail -n 2 | sed 's/^/      → /'
    else
        echo -e "     \e[32m[PASS]\e[0m Zero critical runtime exception blocks discovered."
    fi

    # Enforce rolling truncation to prevent mobile flash storage bloat
    if (( $(echo "$file_size_mb > $MAX_SIZE_MB" | bc -l) )); then
        echo -e "   ⚠️  \e[33m[THRESHOLD EXCEEDED]\e[0m Size exceeds $MAX_SIZE_MB MB limit. Executing safe truncation backup..."
        tail -n 1000 "$log_file" > "${log_file}.tmp" && mv "${log_file}.tmp" "$log_file"
        echo "   ✨ Truncated cleanly. Preserved the final 1,000 active execution lines."
    fi
done
echo -e "\n============================================================"
