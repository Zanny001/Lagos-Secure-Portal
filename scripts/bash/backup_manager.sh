#!/bin/bash

# Configuration settings
BACKUP_DIR="./backups"
WORKSPACE_DATA="./data"
DATABASE_FILE="lagos_leads.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="$BACKUP_DIR/zannie_ecosystem_backup_$TIMESTAMP.tar.gz"

# Step 1: Guarantee backup storage folder availability
mkdir -p "$BACKUP_DIR"

echo "============================================================"
echo "💾 AUTOMATED STORAGE ROTATION ENGINE — RUNNING COMPRESSION"
echo "============================================================"

# Step 2: Assemble target structural assets array
TARGETS=""
[ -d "$WORKSPACE_DATA" ] && TARGETS="$TARGETS $WORKSPACE_DATA"
[ -f "$DATABASE_FILE" ] && TARGETS="$TARGETS $DATABASE_FILE"

# Track and include any relevant Python source code files in the root folder
for source_file in *.py; do
    [ -f "$source_file" ] && TARGETS="$TARGETS $source_file"
done

if [ -z "$TARGETS" ]; then
    echo -e "❌ \e[31m[ERROR]\e[0m No active development assets or databases detected to back up."
    exit 1
fi

# Step 3: Execute high-ratio gzip tar archive compression
echo "[PROCESS] Archiving workspace targets:$TARGETS"
tar -czf "$ARCHIVE_NAME" $TARGETS

if [ $? -eq 0 ]; then
    echo -e "✅ \e[32m[SUCCESS]\e[0m Secure backup file successfully compiled:"
    ls -lh "$ARCHIVE_NAME"
else
    echo -e "❌ \e[31m[ERROR]\e[0m Compression routing failure encountered."
    exit 1
fi

# Step 4: Maintenance Phase — Enforce the Rolling 7-Day Storage Ceiling
echo "------------------------------------------------------------"
echo "🧹 RUNNING PRUNING INTERSECTION FOR ASSETS OLDER THAN 7 DAYS"
echo "------------------------------------------------------------"

# Search for backup targets matching our prefix that have been unmodified for > 7 days
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "zannie_ecosystem_backup_*.tar.gz" -mtime +7)

if [ -n "$OLD_BACKUPS" ]; then
    echo "[CLEANUP] Found expired archival objects to purge:"
    echo "$OLD_BACKUPS"
    echo "$OLD_BACKUPS" | xargs rm -f
    echo -e "🧹 \e[32m[CLEANUP COMPLETED]\e[0m Storage space reclaimed cleanly."
else
    echo "ℹ️  No expired backup archives outside the 7-day sliding window discovered."
fi

echo "============================================================\n"
