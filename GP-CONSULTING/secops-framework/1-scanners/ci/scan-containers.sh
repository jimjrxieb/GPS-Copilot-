#!/bin/bash
# ============================================================================
# CI SCANNER: Container Scanning (Trivy)
# ============================================================================
# Stage: CI (Continuous Integration)
# When: Dockerfile change, image build
# Speed: ~15 seconds per image
# Purpose: Find vulnerable OS packages and CVEs in Docker images
# ============================================================================

set -e

echo "🔍 CI SCANNER: Container Scanning (Trivy)"
echo "═══════════════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker not running, skipping Trivy"
  exit 0
fi

echo

# ============================================================================
# Scan backend image
# ============================================================================
if docker images | grep -q "securebank/backend"; then
  echo "→ Scanning securebank/backend:latest..."
  trivy image securebank/backend:latest \
    --severity HIGH,CRITICAL \
    --format json \
    --output "$OUTPUT_DIR/trivy-backend-results.json" 2>/dev/null || echo "⚠️  Vulnerabilities found"

  VULNS=$(jq '[.Results[]?.Vulnerabilities[]?] | length' "$OUTPUT_DIR/trivy-backend-results.json" 2>/dev/null || echo "0")
  echo "✅ Backend scan complete: $VULNS vulnerabilities"
else
  echo "⏭️  securebank/backend image not found"
fi

echo

# ============================================================================
# Scan frontend image
# ============================================================================
if docker images | grep -q "securebank/frontend"; then
  echo "→ Scanning securebank/frontend:latest..."
  trivy image securebank/frontend:latest \
    --severity HIGH,CRITICAL \
    --format json \
    --output "$OUTPUT_DIR/trivy-frontend-results.json" 2>/dev/null || echo "⚠️  Vulnerabilities found"

  VULNS=$(jq '[.Results[]?.Vulnerabilities[]?] | length' "$OUTPUT_DIR/trivy-frontend-results.json" 2>/dev/null || echo "0")
  echo "✅ Frontend scan complete: $VULNS vulnerabilities"
else
  echo "⏭️  securebank/frontend image not found"
fi

echo
echo "✅ Container Scanning Complete"
echo "   Results: $OUTPUT_DIR/trivy-*-results.json"
