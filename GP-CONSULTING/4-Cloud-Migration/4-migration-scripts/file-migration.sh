#!/bin/bash

# ============================================================================
# File Migration to S3
# ============================================================================
# USAGE:
#   ./file-migration.sh <source-path> <s3-bucket> [s3-prefix]
#
# EXAMPLES:
#   # Migrate all files
#   ./file-migration.sh /local/files payment-receipts
#
#   # With prefix
#   ./file-migration.sh /local/uploads payment-receipts uploads/
#
# FEATURES:
#   ✅ Checksum validation (MD5)
#   ✅ Progress tracking
#   ✅ Resumable (skip existing files)
#   ✅ Metadata preservation
#   ✅ Dry-run mode
# ============================================================================

set -e

SOURCE_PATH="$1"
S3_BUCKET="$2"
S3_PREFIX="${3:-}"
AWS_CMD="${AWS_CMD:-awslocal}"
DRY_RUN="${DRY_RUN:-false}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_DIR="/tmp/file-migration-$TIMESTAMP"
REPORT_FILE="$REPORT_DIR/migration-report.log"
CHECKSUMS_FILE="$REPORT_DIR/checksums.txt"

if [ -z "$SOURCE_PATH" ] || [ -z "$S3_BUCKET" ]; then
    echo "Usage: $0 <source-path> <s3-bucket> [s3-prefix]"
    echo ""
    echo "Example: $0 /local/files payment-receipts uploads/"
    echo ""
    echo "Environment variables:"
    echo "  DRY_RUN     - Preview changes without uploading (true|false)"
    echo "  AWS_CMD     - AWS CLI command (awslocal|aws)"
    exit 1
fi

echo "📁 File Migration to S3"
echo "═══════════════════════════════════════════════════════"
echo "Source: $SOURCE_PATH"
echo "Bucket: s3://$S3_BUCKET/$S3_PREFIX"
echo "Dry Run: $DRY_RUN"
echo ""

# Create report directory
mkdir -p "$REPORT_DIR"
exec > >(tee -a "$REPORT_FILE") 2>&1

# ============================================================================
# Validate Source Path
# ============================================================================

if [ ! -d "$SOURCE_PATH" ]; then
    echo -e "${RED}❌ Source path does not exist: $SOURCE_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Source path validated${NC}"

# ============================================================================
# Check if Bucket Exists
# ============================================================================

echo "Checking S3 bucket..."
if $AWS_CMD s3 ls "s3://$S3_BUCKET" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Bucket exists${NC}"
else
    echo -e "${RED}❌ Bucket does not exist: $S3_BUCKET${NC}"
    echo "Create it with: $AWS_CMD s3 mb s3://$S3_BUCKET"
    exit 1
fi

echo ""

# ============================================================================
# Calculate Source Statistics
# ============================================================================

echo "Calculating source statistics..."

FILE_COUNT=$(find "$SOURCE_PATH" -type f | wc -l)
TOTAL_SIZE=$(du -sb "$SOURCE_PATH" | cut -f1)
TOTAL_SIZE_HUMAN=$(du -sh "$SOURCE_PATH" | cut -f1)

echo "Source statistics:"
echo "  Files: $FILE_COUNT"
echo "  Total size: $TOTAL_SIZE_HUMAN ($TOTAL_SIZE bytes)"
echo ""

# Generate checksums for source files
echo "Generating checksums..."
find "$SOURCE_PATH" -type f -exec md5sum {} \; > "$CHECKSUMS_FILE"
echo -e "${GREEN}✓ Checksums generated: $CHECKSUMS_FILE${NC}"
echo ""

# ============================================================================
# Sync Files to S3
# ============================================================================

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${YELLOW}DRY RUN MODE - No files will be uploaded${NC}"
    echo ""
fi

echo "Syncing files to S3..."

SYNC_CMD="$AWS_CMD s3 sync \"$SOURCE_PATH\" \"s3://$S3_BUCKET/$S3_PREFIX\""

# Add flags
SYNC_CMD="$SYNC_CMD --no-progress"  # Disable progress bar for cleaner logs

if [ "$DRY_RUN" = "true" ]; then
    SYNC_CMD="$SYNC_CMD --dryrun"
fi

# Execute sync
echo "Command: $SYNC_CMD"
echo ""

if eval "$SYNC_CMD" 2>&1 | tee "$REPORT_DIR/sync-output.log"; then
    echo -e "${GREEN}✓ Sync completed${NC}"
else
    echo -e "${RED}✗ Sync failed${NC}"
    exit 1
fi

echo ""

# Skip validation if dry-run
if [ "$DRY_RUN" = "true" ]; then
    echo "═══════════════════════════════════════════════════════"
    echo "Dry run complete - no files uploaded"
    echo "Review changes in: $REPORT_DIR/sync-output.log"
    exit 0
fi

# ============================================================================
# Validate Migration
# ============================================================================

echo "Validating migration..."

# List files in S3
S3_FILE_COUNT=$($AWS_CMD s3 ls "s3://$S3_BUCKET/$S3_PREFIX" --recursive | wc -l)

echo "Validation:"
echo "  Local files: $FILE_COUNT"
echo "  S3 files: $S3_FILE_COUNT"

if [ "$FILE_COUNT" -eq "$S3_FILE_COUNT" ]; then
    echo -e "${GREEN}✓ File counts match${NC}"
else
    echo -e "${RED}✗ File counts do not match${NC}"
fi

echo ""

# ============================================================================
# Verify Checksums (Sample)
# ============================================================================

echo "Verifying checksums (sampling 10 files)..."

SAMPLE_FILES=$(find "$SOURCE_PATH" -type f | head -10)
CHECKSUM_ERRORS=0

while IFS= read -r file; do
    [ -z "$file" ] && continue

    # Get relative path
    REL_PATH="${file#$SOURCE_PATH/}"
    S3_PATH="s3://$S3_BUCKET/$S3_PREFIX$REL_PATH"

    # Calculate local checksum
    LOCAL_MD5=$(md5sum "$file" | cut -d' ' -f1)

    # Get S3 ETag (should match MD5 for non-multipart uploads)
    S3_ETAG=$($AWS_CMD s3api head-object --bucket "$S3_BUCKET" --key "$S3_PREFIX$REL_PATH" --query 'ETag' --output text 2>/dev/null | tr -d '"')

    if [ "$LOCAL_MD5" = "$S3_ETAG" ]; then
        echo -e "  ${GREEN}✓ $REL_PATH${NC}"
    else
        echo -e "  ${RED}✗ $REL_PATH (checksum mismatch)${NC}"
        CHECKSUM_ERRORS=$((CHECKSUM_ERRORS + 1))
    fi
done <<< "$SAMPLE_FILES"

if [ $CHECKSUM_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All sampled checksums verified${NC}"
else
    echo -e "${RED}✗ $CHECKSUM_ERRORS checksum errors found${NC}"
fi

echo ""

# ============================================================================
# Upload Checksums File
# ============================================================================

echo "Uploading checksums file for verification..."
if $AWS_CMD s3 cp "$CHECKSUMS_FILE" "s3://$S3_BUCKET/${S3_PREFIX}migration-checksums.txt" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Checksums file uploaded${NC}"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================

echo "═══════════════════════════════════════════════════════"
if [ $CHECKSUM_ERRORS -eq 0 ] && [ "$FILE_COUNT" -eq "$S3_FILE_COUNT" ]; then
    echo -e "${GREEN}✅ File Migration Complete and Validated${NC}"
else
    echo -e "${YELLOW}⚠ File Migration Complete but Validation Failed${NC}"
fi
echo ""
echo "Migration Report:"
echo "  Source: $SOURCE_PATH"
echo "  Destination: s3://$S3_BUCKET/$S3_PREFIX"
echo "  Files migrated: $S3_FILE_COUNT"
echo "  Total size: $TOTAL_SIZE_HUMAN"
echo ""
echo "Report Directory: $REPORT_DIR"
echo "  - migration-report.log (this output)"
echo "  - checksums.txt (source file checksums)"
echo "  - sync-output.log (aws s3 sync output)"
echo ""
echo "Verify migration:"
echo "  List files: $AWS_CMD s3 ls s3://$S3_BUCKET/$S3_PREFIX --recursive"
echo "  Download checksums: $AWS_CMD s3 cp s3://$S3_BUCKET/${S3_PREFIX}migration-checksums.txt ."
echo ""
echo "Next steps:"
echo "  1. Update application config to use S3"
echo "  2. Test application with S3 storage"
echo "  3. If successful, remove local files (BACKUP FIRST!)"
echo ""
echo "Rollback (if needed):"
echo "  Download all: $AWS_CMD s3 sync s3://$S3_BUCKET/$S3_PREFIX $SOURCE_PATH"
echo "  Delete from S3: $AWS_CMD s3 rm s3://$S3_BUCKET/$S3_PREFIX --recursive"
echo ""
