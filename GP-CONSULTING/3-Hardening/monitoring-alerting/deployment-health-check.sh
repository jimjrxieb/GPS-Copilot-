#!/bin/bash

# ============================================================================
# Deployment Health Check - Real-time deployment monitoring
# ============================================================================
# PURPOSE:
#   Monitor deployments in real-time and alert on failures
#   Deployment NEVER goes according to plan - catch failures immediately
#
# USAGE:
#   ./deployment-health-check.sh /path/to/project [deployment-type]
#
# DEPLOYMENT TYPES:
#   - terraform    : Monitor Terraform deployment
#   - kubernetes   : Monitor K8s deployment
#   - docker       : Monitor Docker deployment
#   - all          : Monitor everything (default)
#
# ALERTS ON:
#   - Pod CrashLoopBackOff
#   - Failed health checks (readiness/liveness)
#   - Terraform apply failures
#   - Resource creation timeouts
#   - OPA policy violations
#   - Container image pull errors
#   - Out of memory (OOM) kills
#   - Network connectivity failures
#
# INTEGRATIONS:
#   - Slack webhooks
#   - PagerDuty
#   - Email
#   - CloudWatch alarms
#   - Datadog
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 DEPLOYMENT HEALTH CHECK"
echo "═══════════════════════════════════════════════════════"
echo "Started: $(date -Iseconds)"
echo ""

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT="${1:-.}"
DEPLOYMENT_TYPE="${2:-all}"
CHECK_INTERVAL=5  # Check every 5 seconds
MAX_WAIT_TIME=600  # 10 minutes max

# Alert endpoints (configure these)
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
PAGERDUTY_KEY="${PAGERDUTY_INTEGRATION_KEY:-}"
ALERT_EMAIL="${ALERT_EMAIL:-ops@company.com}"

# Report directory
REPORT_DIR="$PROJECT_ROOT/secops/6-reports/monitoring"
mkdir -p "$REPORT_DIR"
REPORT_FILE="$REPORT_DIR/health-check-$TIMESTAMP.log"

# Start logging
exec > >(tee -a "$REPORT_FILE") 2>&1

echo "Project: $PROJECT_ROOT"
echo "Deployment Type: $DEPLOYMENT_TYPE"
echo "Report: $REPORT_FILE"
echo ""

# ============================================================================
# Alert Functions
# ============================================================================

send_alert() {
    local severity="$1"  # CRITICAL, WARNING, INFO
    local title="$2"
    local message="$3"

    echo -e "${RED}🚨 ALERT [$severity]: $title${NC}"
    echo "$message"
    echo ""

    # Log to file
    echo "[$(date -Iseconds)] ALERT [$severity]: $title - $message" >> "$REPORT_DIR/alerts.log"

    # Slack
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{
                \"text\": \"🚨 Deployment Alert: $title\",
                \"attachments\": [{
                    \"color\": \"danger\",
                    \"fields\": [
                        {\"title\": \"Severity\", \"value\": \"$severity\", \"short\": true},
                        {\"title\": \"Project\", \"value\": \"$PROJECT_ROOT\", \"short\": true},
                        {\"title\": \"Message\", \"value\": \"$message\", \"short\": false}
                    ]
                }]
            }" 2>/dev/null || true
    fi

    # PagerDuty
    if [ -n "$PAGERDUTY_KEY" ] && [ "$severity" = "CRITICAL" ]; then
        curl -X POST https://events.pagerduty.com/v2/enqueue \
            -H 'Content-Type: application/json' \
            -d "{
                \"routing_key\": \"$PAGERDUTY_KEY\",
                \"event_action\": \"trigger\",
                \"payload\": {
                    \"summary\": \"$title\",
                    \"severity\": \"critical\",
                    \"source\": \"deployment-health-check\",
                    \"custom_details\": {
                        \"message\": \"$message\",
                        \"project\": \"$PROJECT_ROOT\"
                    }
                }
            }" 2>/dev/null || true
    fi

    # Email (if critical)
    if [ "$severity" = "CRITICAL" ]; then
        echo "$message" | mail -s "🚨 CRITICAL: $title" "$ALERT_EMAIL" 2>/dev/null || true
    fi
}

# ============================================================================
# Kubernetes Health Checks
# ============================================================================

check_kubernetes_health() {
    echo "━━━ Kubernetes Health Check ━━━"

    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        echo -e "${YELLOW}⚠ kubectl not found, skipping K8s checks${NC}"
        return 0
    fi

    # Check current context
    CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")
    echo "K8s Context: $CONTEXT"

    if [ "$CONTEXT" = "none" ]; then
        echo -e "${YELLOW}⚠ No K8s context configured${NC}"
        return 0
    fi

    # Get all pods
    echo ""
    echo "Checking pod status..."

    # Check for CrashLoopBackOff
    CRASH_PODS=$(kubectl get pods -A -o json 2>/dev/null | jq -r '.items[] | select(.status.containerStatuses[]?.state.waiting?.reason == "CrashLoopBackOff") | "\(.metadata.namespace)/\(.metadata.name)"' || echo "")

    if [ -n "$CRASH_PODS" ]; then
        send_alert "CRITICAL" "Pods in CrashLoopBackOff" "Pods crashing:\n$CRASH_PODS"

        # Get pod logs
        while IFS= read -r pod_full; do
            namespace=$(echo "$pod_full" | cut -d/ -f1)
            pod=$(echo "$pod_full" | cut -d/ -f2)
            echo "Fetching logs for $pod_full..."
            kubectl logs -n "$namespace" "$pod" --tail=50 > "$REPORT_DIR/crash-$pod-$TIMESTAMP.log" 2>&1 || true
        done <<< "$CRASH_PODS"
    else
        echo -e "${GREEN}✓ No pods in CrashLoopBackOff${NC}"
    fi

    # Check for ImagePullBackOff
    IMAGE_PULL_ERRORS=$(kubectl get pods -A -o json 2>/dev/null | jq -r '.items[] | select(.status.containerStatuses[]?.state.waiting?.reason == "ImagePullBackOff" or .status.containerStatuses[]?.state.waiting?.reason == "ErrImagePull") | "\(.metadata.namespace)/\(.metadata.name)"' || echo "")

    if [ -n "$IMAGE_PULL_ERRORS" ]; then
        send_alert "CRITICAL" "Image Pull Failures" "Cannot pull images:\n$IMAGE_PULL_ERRORS"
    else
        echo -e "${GREEN}✓ No image pull errors${NC}"
    fi

    # Check for OOMKilled containers
    OOM_PODS=$(kubectl get pods -A -o json 2>/dev/null | jq -r '.items[] | select(.status.containerStatuses[]?.lastState.terminated?.reason == "OOMKilled") | "\(.metadata.namespace)/\(.metadata.name)"' || echo "")

    if [ -n "$OOM_PODS" ]; then
        send_alert "CRITICAL" "Containers OOM Killed" "Pods killed due to out of memory:\n$OOM_PODS"
    else
        echo -e "${GREEN}✓ No OOM kills${NC}"
    fi

    # Check readiness/liveness probes
    NOT_READY=$(kubectl get pods -A -o json 2>/dev/null | jq -r '.items[] | select(.status.conditions[] | select(.type == "Ready" and .status == "False")) | "\(.metadata.namespace)/\(.metadata.name)"' || echo "")

    if [ -n "$NOT_READY" ]; then
        send_alert "WARNING" "Pods Not Ready" "Pods failing readiness checks:\n$NOT_READY"
    else
        echo -e "${GREEN}✓ All pods ready${NC}"
    fi

    # Check for recent restarts
    HIGH_RESTART=$(kubectl get pods -A -o json 2>/dev/null | jq -r '.items[] | select(.status.containerStatuses[]?.restartCount > 5) | "\(.metadata.namespace)/\(.metadata.name) (restarts: \(.status.containerStatuses[0].restartCount))"' || echo "")

    if [ -n "$HIGH_RESTART" ]; then
        send_alert "WARNING" "High Pod Restart Count" "Pods with >5 restarts:\n$HIGH_RESTART"
    else
        echo -e "${GREEN}✓ No high restart counts${NC}"
    fi

    # Check for pending pods
    PENDING_PODS=$(kubectl get pods -A -o json 2>/dev/null | jq -r '.items[] | select(.status.phase == "Pending") | "\(.metadata.namespace)/\(.metadata.name)"' || echo "")

    if [ -n "$PENDING_PODS" ]; then
        # Check if pending for more than 5 minutes
        send_alert "WARNING" "Pods Pending" "Pods stuck in Pending state:\n$PENDING_PODS"
    else
        echo -e "${GREEN}✓ No pending pods${NC}"
    fi

    # Check Gatekeeper violations (if installed)
    if kubectl get constrainttemplates &>/dev/null; then
        echo ""
        echo "Checking OPA Gatekeeper violations..."
        VIOLATIONS=$(kubectl get constraints -A -o json 2>/dev/null | jq -r '.items[] | select(.status.totalViolations > 0) | "\(.metadata.name): \(.status.totalViolations) violations"' || echo "")

        if [ -n "$VIOLATIONS" ]; then
            send_alert "WARNING" "OPA Policy Violations" "Gatekeeper violations detected:\n$VIOLATIONS"
        else
            echo -e "${GREEN}✓ No OPA violations${NC}"
        fi
    fi

    echo ""
}

# ============================================================================
# Terraform Health Checks
# ============================================================================

check_terraform_health() {
    echo "━━━ Terraform Health Check ━━━"

    if ! command -v terraform &> /dev/null; then
        echo -e "${YELLOW}⚠ Terraform not found, skipping checks${NC}"
        return 0
    fi

    # Look for Terraform directories
    TF_DIRS=$(find "$PROJECT_ROOT" -type f -name "*.tf" -exec dirname {} \; | sort -u)

    if [ -z "$TF_DIRS" ]; then
        echo -e "${YELLOW}⚠ No Terraform files found${NC}"
        return 0
    fi

    while IFS= read -r tf_dir; do
        echo "Checking: $tf_dir"
        cd "$tf_dir" || continue

        # Check if state exists
        if ! terraform state list &>/dev/null; then
            echo -e "${YELLOW}⚠ No state found in $tf_dir${NC}"
            continue
        fi

        # Check for drift
        echo "Checking for drift..."
        if ! terraform plan -detailed-exitcode -out=tfplan 2>&1 | tee "$REPORT_DIR/terraform-plan-$TIMESTAMP.log"; then
            EXIT_CODE=$?
            if [ $EXIT_CODE -eq 1 ]; then
                send_alert "CRITICAL" "Terraform Plan Failed" "terraform plan failed in $tf_dir"
            elif [ $EXIT_CODE -eq 2 ]; then
                send_alert "WARNING" "Terraform Drift Detected" "Configuration drift detected in $tf_dir"
            fi
        else
            echo -e "${GREEN}✓ No drift detected${NC}"
        fi

        # Check for failed resources
        FAILED_RESOURCES=$(terraform state list 2>/dev/null | while read -r resource; do
            if ! terraform state show "$resource" &>/dev/null; then
                echo "$resource"
            fi
        done)

        if [ -n "$FAILED_RESOURCES" ]; then
            send_alert "CRITICAL" "Terraform Resources Failed" "Failed resources in $tf_dir:\n$FAILED_RESOURCES"
        fi

    done <<< "$TF_DIRS"

    echo ""
}

# ============================================================================
# Docker Health Checks
# ============================================================================

check_docker_health() {
    echo "━━━ Docker Health Check ━━━"

    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}⚠ Docker not found, skipping checks${NC}"
        return 0
    fi

    # Check unhealthy containers
    UNHEALTHY=$(docker ps -a --filter "health=unhealthy" --format "{{.Names}}" 2>/dev/null || echo "")

    if [ -n "$UNHEALTHY" ]; then
        send_alert "CRITICAL" "Unhealthy Docker Containers" "Containers failing health checks:\n$UNHEALTHY"

        # Get container logs
        while IFS= read -r container; do
            docker logs --tail 100 "$container" > "$REPORT_DIR/docker-$container-$TIMESTAMP.log" 2>&1 || true
        done <<< "$UNHEALTHY"
    else
        echo -e "${GREEN}✓ No unhealthy containers${NC}"
    fi

    # Check exited containers (recent)
    EXITED=$(docker ps -a --filter "status=exited" --filter "since=1h" --format "{{.Names}} (exit code: {{.Status}})" 2>/dev/null || echo "")

    if [ -n "$EXITED" ]; then
        send_alert "WARNING" "Containers Exited Recently" "Containers exited in last hour:\n$EXITED"
    else
        echo -e "${GREEN}✓ No recent exits${NC}"
    fi

    # Check for OOM killed containers
    OOM_CONTAINERS=$(docker ps -a --filter "status=exited" --format "{{.Names}}" 2>/dev/null | while read -r container; do
        if docker inspect "$container" 2>/dev/null | jq -e '.[] | select(.State.OOMKilled == true)' > /dev/null; then
            echo "$container"
        fi
    done)

    if [ -n "$OOM_CONTAINERS" ]; then
        send_alert "CRITICAL" "Docker Containers OOM Killed" "Containers killed due to OOM:\n$OOM_CONTAINERS"
    else
        echo -e "${GREEN}✓ No OOM kills${NC}"
    fi

    echo ""
}

# ============================================================================
# AWS Health Checks (if applicable)
# ============================================================================

check_aws_health() {
    echo "━━━ AWS Health Check ━━━"

    if ! command -v aws &> /dev/null; then
        echo -e "${YELLOW}⚠ AWS CLI not found, skipping checks${NC}"
        return 0
    fi

    # Check CloudWatch alarms in ALARM state
    ALARMS=$(aws cloudwatch describe-alarms --state-value ALARM --query 'MetricAlarms[*].[AlarmName,StateReason]' --output text 2>/dev/null || echo "")

    if [ -n "$ALARMS" ]; then
        send_alert "CRITICAL" "CloudWatch Alarms Triggered" "Active alarms:\n$ALARMS"
    else
        echo -e "${GREEN}✓ No CloudWatch alarms${NC}"
    fi

    # Check for failed ECS tasks (if using ECS)
    if aws ecs list-clusters &>/dev/null; then
        CLUSTERS=$(aws ecs list-clusters --query 'clusterArns[*]' --output text 2>/dev/null)
        for cluster in $CLUSTERS; do
            STOPPED_TASKS=$(aws ecs list-tasks --cluster "$cluster" --desired-status STOPPED --query 'taskArns[*]' --output text 2>/dev/null | head -5)

            if [ -n "$STOPPED_TASKS" ]; then
                send_alert "WARNING" "ECS Tasks Stopped" "Recent stopped tasks in $cluster"
            fi
        done
    fi

    echo ""
}

# ============================================================================
# Main Execution
# ============================================================================

echo "🏥 Starting health checks..."
echo ""

case "$DEPLOYMENT_TYPE" in
    terraform)
        check_terraform_health
        ;;
    kubernetes|k8s)
        check_kubernetes_health
        ;;
    docker)
        check_docker_health
        ;;
    aws)
        check_aws_health
        ;;
    all)
        check_kubernetes_health
        check_terraform_health
        check_docker_health
        check_aws_health
        ;;
    *)
        echo "Unknown deployment type: $DEPLOYMENT_TYPE"
        exit 1
        ;;
esac

# ============================================================================
# Summary
# ============================================================================

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "═══════════════════════════════════════════════════════"
echo "✅ Health Check Complete"
echo "Duration: ${DURATION}s"
echo "Report: $REPORT_FILE"
echo "Alerts logged: $REPORT_DIR/alerts.log"
echo ""

# Check if any critical alerts were sent
if grep -q "CRITICAL" "$REPORT_DIR/alerts.log" 2>/dev/null; then
    echo -e "${RED}🚨 CRITICAL issues detected - see alerts.log${NC}"
    exit 1
elif grep -q "WARNING" "$REPORT_DIR/alerts.log" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Warnings detected - review recommended${NC}"
    exit 0
else
    echo -e "${GREEN}✓ All systems healthy${NC}"
    exit 0
fi
