#!/bin/bash
# ============================================================
# ZANNIE SYSTEM UTILITY — AUTOMATED DATABASE BACKUP & LOG ROTATION
# ============================================================

# Load paths relative to project root
BASE_DIR="/home/userland/Lagos-Secure-Portal"
BACKUP_DIR="$BASE_DIR/data/backups"
LOG_DIR="$BASE_DIR/logs"

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "============== [STARTING SYSTEM MAINTENANCE] =============="
echo "[*] Initializing live hot-backup for SQLite storage blocks..."

# 1. Back up Academic Database
if [ -f "$BASE_DIR/data/student_reports/academic.db" ]; then
    sqlite3 "$BASE_DIR/data/student_reports/academic.db" ".backup '$BACKUP_DIR/academic_backup_$TIMESTAMP.db'"
    echo "✅ Academic Stats Database backed up successfully."
else
    echo "⚠️ Academic Database file not found. Skipping backup."
fi

# 2. Back up Zannie Orders Database
if [ -f "$BASE_DIR/data/zannie_shop/zannie.db" ]; then
    sqlite3 "$BASE_DIR/data/zannie_shop/zannie.db" ".backup '$BACKUP_DIR/zannie_backup_$TIMESTAMP.db'"
    echo "✅ Zannie E-Commerce Storage Database backed up successfully."
else
    echo "⚠️ Zannie Database file not found. Skipping backup."
fi

# 3. Log Rotation Routine
echo "[*] Initiating active telemetry log rotation..."
if [ -d "$LOG_DIR" ]; then
    for logfile in "$LOG_DIR"/*.log; do
        if [ -f "$logfile" ]; then
            # Archive old log contents to keep live logs small and snappy
            cp "$logfile" "${logfile}_$TIMESTAMP.bak"
            cat /dev/null > "$logfile"
            echo "⚡ Rotated log asset: $(basename "$logfile")"
        fi
    done
else
    echo "⚠️ Telemetry log folder not found."
fi

echo "=================== [MAINTENANCE COMPLETE] ==================="
