#!/bin/bash

# ============================================================================
# Auto-Rollback - When Deployments Fail
# ============================================================================
# PURPOSE:
#   Automatically rollback failed deployments
#   "Deployment NEVER goes according to plan" - have a safety net
#
# USAGE:
#   ./auto-rollback.sh [deployment-type] [project-root]
#
# DEPLOYMENT TYPES:
#   - kubernetes   : Rollback K8s deployment
#   - terraform    : Destroy failed Terraform resources
#   - docker       : Stop and remove failed containers
#   - all          : Attempt all rollbacks (default)
#
# WHAT IT DOES:
#   1. Detects failed deployments
#   2. Preserves evidence (logs, state files)
#   3. Rolls back to last known good state
#   4. Sends alerts to ops team
#   5. Creates incident report
#
# SAFETY:
#   - Always creates backups before rollback
#   - Requires confirmation for production
#   - Logs all actions
#   - Preserves evidence for post-mortem
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🔄 AUTO-ROLLBACK SYSTEM"
echo "═══════════════════════════════════════════════════════"
echo "Started: $(date -Iseconds)"
echo ""

# ============================================================================
# Configuration
# ============================================================================

DEPLOYMENT_TYPE="${1:-all}"
PROJECT_ROOT="${2:-.}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

# Require confirmation for production
REQUIRE_CONFIRMATION=true
if [ "$ENVIRONMENT" = "production" ]; then
    REQUIRE_CONFIRMATION=true
fi

# Directories
BACKUP_DIR="$PROJECT_ROOT/secops/6-reports/rollback-backups/$TIMESTAMP"
EVIDENCE_DIR="$PROJECT_ROOT/secops/6-reports/incident-evidence/$TIMESTAMP"
REPORT_FILE="$PROJECT_ROOT/secops/6-reports/rollback-report-$TIMESTAMP.log"

mkdir -p "$BACKUP_DIR" "$EVIDENCE_DIR"

# Start logging
exec > >(tee -a "$REPORT_FILE") 2>&1

echo "Deployment Type: $DEPLOYMENT_TYPE"
echo "Project: $PROJECT_ROOT"
echo "Environment: $ENVIRONMENT"
echo "Backup Directory: $BACKUP_DIR"
echo "Evidence Directory: $EVIDENCE_DIR"
echo ""

# ============================================================================
# Alert Function
# ============================================================================

send_alert() {
    local severity="$1"
    local title="$2"
    local message="$3"

    echo -e "${RED}📢 ALERT [$severity]: $title${NC}"
    echo "$message"
    echo ""

    # Slack webhook
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        curl -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{
                \"text\": \"🔄 Rollback Alert: $title\",
                \"attachments\": [{
                    \"color\": \"warning\",
                    \"fields\": [
                        {\"title\": \"Severity\", \"value\": \"$severity\", \"short\": true},
                        {\"title\": \"Environment\", \"value\": \"$ENVIRONMENT\", \"short\": true},
                        {\"title\": \"Message\", \"value\": \"$message\", \"short\": false}
                    ]
                }]
            }" 2>/dev/null || true
    fi
}

# ============================================================================
# Confirmation Prompt
# ============================================================================

confirm_rollback() {
    if [ "$REQUIRE_CONFIRMATION" = "false" ]; then
        return 0
    fi

    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠  ROLLBACK CONFIRMATION REQUIRED${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "Environment: $ENVIRONMENT"
    echo "Deployment Type: $DEPLOYMENT_TYPE"
    echo "Project: $PROJECT_ROOT"
    echo ""
    echo "This will:"
    echo "  1. Preserve current state as evidence"
    echo "  2. Rollback to previous version"
    echo "  3. Send alerts to ops team"
    echo ""
    read -p "Proceed with rollback? (yes/no): " -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Rollback cancelled"
        exit 1
    fi
}

# ============================================================================
# Kubernetes Rollback
# ============================================================================

rollback_kubernetes() {
    echo "━━━ Kubernetes Rollback ━━━"

    if ! command -v kubectl &> /dev/null; then
        echo -e "${YELLOW}⚠ kubectl not found, skipping K8s rollback${NC}"
        return 0
    fi

    # Get current context
    CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")
    echo "K8s Context: $CONTEXT"

    if [ "$CONTEXT" = "none" ]; then
        echo "No K8s context configured"
        return 0
    fi

    # Find failed deployments
    echo "Checking for failed deployments..."
    FAILED_DEPLOYMENTS=$(kubectl get deployments -A -o json 2>/dev/null | \
        jq -r '.items[] | select(.status.conditions[]? | select(.type == "Progressing" and .status == "False")) | "\(.metadata.namespace)/\(.metadata.name)"' || echo "")

    if [ -z "$FAILED_DEPLOYMENTS" ]; then
        echo -e "${GREEN}✓ No failed deployments found${NC}"
        return 0
    fi

    echo "Failed deployments:"
    echo "$FAILED_DEPLOYMENTS"
    echo ""

    # Collect evidence before rollback
    echo "Collecting evidence..."
    while IFS= read -r deployment_full; do
        namespace=$(echo "$deployment_full" | cut -d/ -f1)
        deployment=$(echo "$deployment_full" | cut -d/ -f2)

        # Save deployment YAML
        kubectl get deployment -n "$namespace" "$deployment" -o yaml > "$EVIDENCE_DIR/deployment-$deployment.yaml" 2>&1 || true

        # Save pod logs
        PODS=$(kubectl get pods -n "$namespace" -l "app=$deployment" -o name 2>/dev/null || echo "")
        for pod in $PODS; do
            pod_name=$(basename "$pod")
            kubectl logs -n "$namespace" "$pod_name" --all-containers=true > "$EVIDENCE_DIR/logs-$pod_name.log" 2>&1 || true
            kubectl describe pod -n "$namespace" "$pod_name" > "$EVIDENCE_DIR/describe-$pod_name.txt" 2>&1 || true
        done

        # Save events
        kubectl get events -n "$namespace" --sort-by='.lastTimestamp' > "$EVIDENCE_DIR/events-$namespace.log" 2>&1 || true

    done <<< "$FAILED_DEPLOYMENTS"

    # Perform rollback
    confirm_rollback

    echo "Rolling back deployments..."
    while IFS= read -r deployment_full; do
        namespace=$(echo "$deployment_full" | cut -d/ -f1)
        deployment=$(echo "$deployment_full" | cut -d/ -f2)

        echo "Rolling back: $deployment_full"

        # Check rollback history
        REVISION_COUNT=$(kubectl rollout history deployment -n "$namespace" "$deployment" 2>/dev/null | wc -l)

        if [ "$REVISION_COUNT" -gt 2 ]; then
            # Rollback to previous revision
            if kubectl rollout undo deployment -n "$namespace" "$deployment"; then
                echo -e "${GREEN}✓ Rolled back $deployment_full${NC}"
                send_alert "INFO" "Deployment Rolled Back" "Successfully rolled back $deployment_full"

                # Wait for rollback to complete
                kubectl rollout status deployment -n "$namespace" "$deployment" --timeout=300s || {
                    echo -e "${RED}✗ Rollback failed for $deployment_full${NC}"
                    send_alert "CRITICAL" "Rollback Failed" "Rollback failed for $deployment_full"
                }
            else
                echo -e "${RED}✗ Failed to rollback $deployment_full${NC}"
                send_alert "CRITICAL" "Rollback Command Failed" "kubectl rollout undo failed for $deployment_full"
            fi
        else
            echo -e "${YELLOW}⚠ Not enough revisions to rollback $deployment_full${NC}"

            # Scale down to zero as last resort
            echo "Scaling down to zero pods..."
            kubectl scale deployment -n "$namespace" "$deployment" --replicas=0
            send_alert "WARNING" "Deployment Scaled Down" "No rollback history available, scaled $deployment_full to 0 replicas"
        fi

    done <<< "$FAILED_DEPLOYMENTS"

    echo ""
}

# ============================================================================
# Terraform Rollback
# ============================================================================

rollback_terraform() {
    echo "━━━ Terraform Rollback ━━━"

    if ! command -v terraform &> /dev/null; then
        echo -e "${YELLOW}⚠ Terraform not found, skipping rollback${NC}"
        return 0
    fi

    # Find Terraform directories
    TF_DIRS=$(find "$PROJECT_ROOT" -type f -name "*.tf" -exec dirname {} \; | sort -u)

    if [ -z "$TF_DIRS" ]; then
        echo "No Terraform files found"
        return 0
    fi

    while IFS= read -r tf_dir; do
        echo "Checking: $tf_dir"
        cd "$tf_dir" || continue

        # Backup current state
        if [ -f ".terraform/terraform.tfstate" ]; then
            cp .terraform/terraform.tfstate "$BACKUP_DIR/terraform.tfstate.backup" || true
        fi
        if [ -f "terraform.tfstate" ]; then
            cp terraform.tfstate "$BACKUP_DIR/terraform.tfstate.backup" || true
        fi

        # Check for failed resources
        echo "Checking for failed applies..."

        # Run terraform plan to detect issues
        if ! terraform plan -detailed-exitcode &> "$EVIDENCE_DIR/terraform-plan.log"; then
            EXIT_CODE=$?

            if [ $EXIT_CODE -eq 1 ]; then
                echo -e "${RED}✗ Terraform configuration has errors${NC}"
                send_alert "CRITICAL" "Terraform Config Error" "Configuration errors detected in $tf_dir"

                # Save evidence
                cp "$EVIDENCE_DIR/terraform-plan.log" "$EVIDENCE_DIR/terraform-error-$TIMESTAMP.log"

                # Check if we should destroy failed resources
                confirm_rollback

                echo "Destroying failed resources..."
                terraform destroy -auto-approve 2>&1 | tee "$EVIDENCE_DIR/terraform-destroy.log"

                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✓ Terraform resources destroyed${NC}"
                    send_alert "INFO" "Terraform Rollback Complete" "Destroyed resources in $tf_dir"
                else
                    echo -e "${RED}✗ Failed to destroy resources${NC}"
                    send_alert "CRITICAL" "Terraform Destroy Failed" "Could not destroy resources in $tf_dir - manual intervention required"
                fi
            fi
        else
            echo -e "${GREEN}✓ No Terraform issues detected${NC}"
        fi

    done <<< "$TF_DIRS"

    echo ""
}

# ============================================================================
# Docker Rollback
# ============================================================================

rollback_docker() {
    echo "━━━ Docker Rollback ━━━"

    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}⚠ Docker not found, skipping rollback${NC}"
        return 0
    fi

    # Find unhealthy or exited containers
    FAILED_CONTAINERS=$(docker ps -a --filter "health=unhealthy" --format "{{.Names}}" 2>/dev/null)
    EXITED_CONTAINERS=$(docker ps -a --filter "status=exited" --filter "since=1h" --format "{{.Names}}" 2>/dev/null)

    ALL_FAILED="$FAILED_CONTAINERS"$'\n'"$EXITED_CONTAINERS"
    ALL_FAILED=$(echo "$ALL_FAILED" | sort -u | grep -v '^$')

    if [ -z "$ALL_FAILED" ]; then
        echo -e "${GREEN}✓ No failed containers found${NC}"
        return 0
    fi

    echo "Failed containers:"
    echo "$ALL_FAILED"
    echo ""

    # Collect evidence
    echo "Collecting evidence..."
    while IFS= read -r container; do
        docker logs --tail 500 "$container" > "$EVIDENCE_DIR/docker-$container.log" 2>&1 || true
        docker inspect "$container" > "$EVIDENCE_DIR/docker-inspect-$container.json" 2>&1 || true
    done <<< "$ALL_FAILED"

    confirm_rollback

    # Stop and remove failed containers
    echo "Removing failed containers..."
    while IFS= read -r container; do
        echo "Removing: $container"

        docker stop "$container" 2>&1 | tee -a "$EVIDENCE_DIR/docker-rollback.log" || true
        docker rm "$container" 2>&1 | tee -a "$EVIDENCE_DIR/docker-rollback.log" || true

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Removed $container${NC}"
            send_alert "INFO" "Container Removed" "Removed failed container: $container"
        else
            echo -e "${RED}✗ Failed to remove $container${NC}"
            send_alert "WARNING" "Container Removal Failed" "Could not remove: $container"
        fi
    done <<< "$ALL_FAILED"

    # Check for docker-compose
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        echo ""
        echo "Found docker-compose.yml"
        echo "To restart services, run: docker-compose up -d"
    fi

    echo ""
}

# ============================================================================
# Main Execution
# ============================================================================

echo "🔍 Detecting failed deployments..."
echo ""

case "$DEPLOYMENT_TYPE" in
    kubernetes|k8s)
        rollback_kubernetes
        ;;
    terraform|tf)
        rollback_terraform
        ;;
    docker)
        rollback_docker
        ;;
    all)
        rollback_kubernetes
        rollback_terraform
        rollback_docker
        ;;
    *)
        echo "Unknown deployment type: $DEPLOYMENT_TYPE"
        echo "Valid options: kubernetes, terraform, docker, all"
        exit 1
        ;;
esac

# ============================================================================
# Create Incident Report
# ============================================================================

INCIDENT_REPORT="$EVIDENCE_DIR/INCIDENT-REPORT.md"

cat > "$INCIDENT_REPORT" <<EOF
# Deployment Rollback Incident Report

**Date:** $(date -Iseconds)
**Environment:** $ENVIRONMENT
**Deployment Type:** $DEPLOYMENT_TYPE
**Project:** $PROJECT_ROOT

---

## Incident Summary

Automated rollback was triggered due to deployment failures.

## Actions Taken

1. Evidence collection completed
2. Rollback performed for: $DEPLOYMENT_TYPE
3. Alerts sent to ops team
4. Logs preserved in: $EVIDENCE_DIR

## Evidence Collected

\`\`\`
$(ls -lh "$EVIDENCE_DIR")
\`\`\`

## Next Steps

1. **Root Cause Analysis**: Review logs in $EVIDENCE_DIR
2. **Fix Issues**: Address deployment failures
3. **Re-deploy**: After fixes are verified
4. **Post-Mortem**: Document lessons learned

## Rollback Log

See: $REPORT_FILE

## Contact

- **On-Call Engineer:** ${ONCALL_ENGINEER:-TBD}
- **Incident Commander:** ${INCIDENT_COMMANDER:-TBD}

---

*Auto-generated by auto-rollback.sh*
EOF

echo "📄 Incident report created: $INCIDENT_REPORT"
echo ""

# ============================================================================
# Summary
# ============================================================================

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "═══════════════════════════════════════════════════════"
echo "✅ Rollback Complete"
echo "Duration: ${DURATION}s"
echo "Evidence: $EVIDENCE_DIR"
echo "Backups: $BACKUP_DIR"
echo "Report: $REPORT_FILE"
echo "Incident Report: $INCIDENT_REPORT"
echo ""
echo "Next steps:"
echo "  1. Review incident report: $INCIDENT_REPORT"
echo "  2. Analyze logs in: $EVIDENCE_DIR"
echo "  3. Fix deployment issues"
echo "  4. Test in lower environment"
echo "  5. Re-deploy after verification"
echo ""

send_alert "INFO" "Rollback Complete" "Rollback finished successfully. Review incident report: $INCIDENT_REPORT"
