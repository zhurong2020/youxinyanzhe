#!/bin/bash
#
# WordPress Backup Script
# Run this on VPS before migration
#
# Usage:
#   ssh arong-vps 'bash -s' < wp_backup.sh
#   or copy to VPS and run locally
#

set -e

# Configuration
WP_DIR="/var/www/html"          # WordPress installation directory
BACKUP_DIR="/home/backup"       # Backup destination
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="wp_backup_${DATE}"

echo "=========================================="
echo "WordPress Backup Script"
echo "Date: $(date)"
echo "=========================================="

# Create backup directory
mkdir -p "${BACKUP_DIR}"
cd "${BACKUP_DIR}"

echo ""
echo "[1/4] Backing up WordPress files..."
tar -czf "${BACKUP_NAME}_files.tar.gz" -C "${WP_DIR}" . 2>/dev/null || {
    echo "Warning: Some files may have been skipped"
}
echo "  Files backup: ${BACKUP_DIR}/${BACKUP_NAME}_files.tar.gz"

echo ""
echo "[2/4] Backing up MySQL database..."
# Get database credentials from wp-config.php
if [ -f "${WP_DIR}/wp-config.php" ]; then
    DB_NAME=$(grep "DB_NAME" "${WP_DIR}/wp-config.php" | cut -d "'" -f 4)
    DB_USER=$(grep "DB_USER" "${WP_DIR}/wp-config.php" | cut -d "'" -f 4)
    DB_PASS=$(grep "DB_PASSWORD" "${WP_DIR}/wp-config.php" | cut -d "'" -f 4)
    DB_HOST=$(grep "DB_HOST" "${WP_DIR}/wp-config.php" | cut -d "'" -f 4)

    if [ -n "$DB_NAME" ]; then
        mysqldump -h "${DB_HOST}" -u "${DB_USER}" -p"${DB_PASS}" "${DB_NAME}" > "${BACKUP_NAME}_db.sql" 2>/dev/null
        gzip "${BACKUP_NAME}_db.sql"
        echo "  Database backup: ${BACKUP_DIR}/${BACKUP_NAME}_db.sql.gz"
    else
        echo "  Warning: Could not extract database credentials"
    fi
else
    echo "  Warning: wp-config.php not found at ${WP_DIR}"
fi

echo ""
echo "[3/4] Creating backup manifest..."
cat > "${BACKUP_NAME}_manifest.txt" << EOF
WordPress Backup Manifest
=========================
Date: $(date)
Hostname: $(hostname)
WordPress Directory: ${WP_DIR}

Files:
- ${BACKUP_NAME}_files.tar.gz
- ${BACKUP_NAME}_db.sql.gz
- ${BACKUP_NAME}_manifest.txt

WordPress Version: $(grep "wp_version = " "${WP_DIR}/wp-includes/version.php" 2>/dev/null | cut -d "'" -f 2 || echo "Unknown")

Disk Usage Before Backup:
$(du -sh ${WP_DIR} 2>/dev/null || echo "Unknown")

Backup Sizes:
$(ls -lh ${BACKUP_NAME}* 2>/dev/null)

Restore Instructions:
1. Stop web server: sudo systemctl stop nginx (or apache2)
2. Restore files: tar -xzf ${BACKUP_NAME}_files.tar.gz -C ${WP_DIR}
3. Restore database: gunzip < ${BACKUP_NAME}_db.sql.gz | mysql -u [user] -p [database]
4. Start web server: sudo systemctl start nginx
EOF

echo "  Manifest: ${BACKUP_DIR}/${BACKUP_NAME}_manifest.txt"

echo ""
echo "[4/4] Verifying backup..."
if [ -f "${BACKUP_NAME}_files.tar.gz" ] && [ -f "${BACKUP_NAME}_db.sql.gz" ]; then
    FILES_SIZE=$(ls -lh "${BACKUP_NAME}_files.tar.gz" | awk '{print $5}')
    DB_SIZE=$(ls -lh "${BACKUP_NAME}_db.sql.gz" | awk '{print $5}')
    echo "  Files backup size: ${FILES_SIZE}"
    echo "  Database backup size: ${DB_SIZE}"
    echo ""
    echo "=========================================="
    echo "BACKUP COMPLETED SUCCESSFULLY!"
    echo "=========================================="
    echo ""
    echo "Backup location: ${BACKUP_DIR}"
    echo "Files:"
    ls -lh "${BACKUP_DIR}/${BACKUP_NAME}"*
else
    echo ""
    echo "=========================================="
    echo "WARNING: Backup may be incomplete!"
    echo "=========================================="
fi

echo ""
echo "To download backup to local machine:"
echo "  scp arong-vps:${BACKUP_DIR}/${BACKUP_NAME}* /path/to/local/backup/"
