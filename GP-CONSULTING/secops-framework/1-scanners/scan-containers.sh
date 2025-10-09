#!/bin/bash
set -e

OUTPUT_DIR="../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

echo "🔍 Container Security Scan (Trivy)"
echo "═══════════════════════════════════════"

# Trivy scan
if command -v trivy >/dev/null 2>&1; then
  echo "→ Running Trivy on Docker images..."

  # Scan backend image
  if docker image inspect securebank/backend:latest >/dev/null 2>&1; then
    trivy image securebank/backend:latest \
      --severity HIGH,CRITICAL \
      --format json \
      --output "$OUTPUT_DIR/trivy-backend-results.json" || true
    echo "✅ Backend image scanned"
  else
    echo "⚠️  Backend image not found. Build it first: docker-compose build backend"
  fi

  # Scan frontend image
  if docker image inspect securebank/frontend:latest >/dev/null 2>&1; then
    trivy image securebank/frontend:latest \
      --severity HIGH,CRITICAL \
      --format json \
      --output "$OUTPUT_DIR/trivy-frontend-results.json" || true
    echo "✅ Frontend image scanned"
  else
    echo "⚠️  Frontend image not found. Build it first: docker-compose build frontend"
  fi
else
  echo "⚠️  Trivy not installed. Install: brew install trivy"
fi

echo ""
echo "📁 Results saved to: $OUTPUT_DIR/"
