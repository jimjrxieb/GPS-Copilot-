#!/bin/bash
# ============================================================================
# RUNTIME MONITOR: Prometheus Metrics
# ============================================================================
# Stage: RUNTIME
# When: Continuous (24/7)
# Speed: Real-time (15s scrape interval)
# Purpose: Monitor CPU, memory, network, request rates
# ============================================================================

set -e

echo "🔍 RUNTIME MONITOR: Prometheus Metrics"
echo "═══════════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"

# Check if Prometheus is accessible
if ! curl -s "$PROMETHEUS_URL/api/v1/status/config" > /dev/null 2>&1; then
  echo "⏭️  Prometheus not accessible at $PROMETHEUS_URL"
  echo "   Set PROMETHEUS_URL environment variable or ensure Prometheus is running"
  exit 0
fi

echo "Prometheus URL: $PROMETHEUS_URL"
echo

# ============================================================================
# Query high CPU pods
# ============================================================================
echo "→ Querying high CPU usage..."
curl -s "$PROMETHEUS_URL/api/v1/query?query=rate(container_cpu_usage_seconds_total[5m])*100>80" > "$OUTPUT_DIR/prometheus-high-cpu.json"

HIGH_CPU=$(jq '.data.result | length' "$OUTPUT_DIR/prometheus-high-cpu.json" 2>/dev/null || echo "0")
echo "✅ High CPU pods: $HIGH_CPU"

# ============================================================================
# Query high memory pods
# ============================================================================
echo "→ Querying high memory usage..."
curl -s "$PROMETHEUS_URL/api/v1/query?query=container_memory_usage_bytes/(container_spec_memory_limit_bytes)*100>90" > "$OUTPUT_DIR/prometheus-high-memory.json"

HIGH_MEM=$(jq '.data.result | length' "$OUTPUT_DIR/prometheus-high-memory.json" 2>/dev/null || echo "0")
echo "✅ High memory pods: $HIGH_MEM"

# ============================================================================
# Query pod restart count
# ============================================================================
echo "→ Querying pod restarts..."
curl -s "$PROMETHEUS_URL/api/v1/query?query=kube_pod_container_status_restarts_total>5" > "$OUTPUT_DIR/prometheus-pod-restarts.json"

RESTARTS=$(jq '.data.result | length' "$OUTPUT_DIR/prometheus-pod-restarts.json" 2>/dev/null || echo "0")
echo "✅ Pods with >5 restarts: $RESTARTS"

# ============================================================================
# Query 5xx error rate
# ============================================================================
echo "→ Querying 5xx error rate..."
curl -s "$PROMETHEUS_URL/api/v1/query?query=rate(http_requests_total{status=~\"5..\"}[5m])>0.05" > "$OUTPUT_DIR/prometheus-error-rate.json"

ERRORS=$(jq '.data.result | length' "$OUTPUT_DIR/prometheus-error-rate.json" 2>/dev/null || echo "0")
echo "✅ Services with high error rate: $ERRORS"

echo
echo "✅ Prometheus Metrics Collected"
echo "   Results: $OUTPUT_DIR/prometheus-*.json"
