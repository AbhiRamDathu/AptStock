#!/bin/bash

# ============================================================
# FORECASTAI PRO - MongoDB Backup Script
# Safe, zero-cost backup for MVP
# Run weekly or daily from cron
# ============================================================

# Configuration
BACKUP_DIR="./backups/mongodb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="apdf_io_mongo_${TIMESTAMP}"
RETENTION_DAYS=14  # Keep 14 days of backups locally

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "========================================="
echo "🔄 MongoDB Backup Started"
echo "Time: $(date)"
echo "========================================="

# Check if mongodump is installed
if ! command -v mongodump &> /dev/null; then
    echo "❌ ERROR: mongodump not found!"
    echo "Install MongoDB Database Tools:"
    echo "  macOS: brew install mongodb-database-tools"
    echo "  Ubuntu: sudo apt-get install mongodb-database-tools"
    exit 1
fi

# Run backup
echo "📦 Dumping database to $BACKUP_DIR/$BACKUP_NAME..."

# Get MONGO_URI from .env file
export $(grep ^MONGO_URI= .env | xargs)

mongodump \
  --uri="$MONGO_URI" \
  --out="$BACKUP_DIR/$BACKUP_NAME" \
  --gzip

# Check if backup succeeded
if [ $? -eq 0 ]; then
    # Compress backup for storage
    echo "📦 Compressing backup..."
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
    rm -rf "$BACKUP_DIR/$BACKUP_NAME"
    
    # Count backups
    BACKUP_COUNT=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    
    echo ""
    echo "✅ BACKUP SUCCESSFUL"
    echo "   File: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    echo "   Total backups: $BACKUP_COUNT"
    echo "   Backup directory size: $BACKUP_SIZE"
    echo ""
    
    # Delete old backups (> 14 days)
    echo "🧹 Cleaning old backups (> $RETENTION_DAYS days)..."
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    echo ""
    echo "✅ Backup Complete"
    echo "Timestamp: $(date)"
    echo "========================================="
    
else
    echo ""
    echo "❌ BACKUP FAILED!"
    echo "Check your MongoDB connection or permissions"
    echo "========================================="
    exit 1
fi
