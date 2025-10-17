#!/bin/bash

# ============================================================================
# Incident Escalation System
# ============================================================================
# PURPOSE:
#   When deployment/rollback fails and manual intervention is required
#   Escalate to appropriate teams with full context
#
# USAGE:
#   ./escalate-incident.sh [severity] [incident-type]
#
# SEVERITY LEVELS:
#   - P1 (Critical)  : Production down, revenue impact
#   - P2 (High)      : Major functionality impaired
#   - P3 (Medium)    : Partial functionality affected
#   - P4 (Low)       : Minor issue, workaround available
#
# INCIDENT TYPES:
#   - deployment-failure   : Deployment failed
#   - rollback-failure     : Rollback failed (critical)
#   - security-breach      : Security incident
#   - data-loss           : Data integrity issue
#   - performance         : Severe performance degradation
#
# WHAT IT DOES:
#   1. Pages on-call engineer
#   2. Creates incident ticket (Jira/PagerDuty/ServiceNow)
#   3. Notifies stakeholders
#   4. Starts incident bridge
#   5. Collects all relevant context
#   6. Provides runbook links
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🚨 INCIDENT ESCALATION SYSTEM"
echo "═══════════════════════════════════════════════════════"
echo "Started: $(date -Iseconds)"
echo ""

# ============================================================================
# Configuration
# ============================================================================

SEVERITY="${1:-P2}"
INCIDENT_TYPE="${2:-deployment-failure}"
PROJECT_ROOT="${3:-.}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Escalation contacts
ONCALL_ENGINEER="${ONCALL_ENGINEER:-oncall@company.com}"
INCIDENT_COMMANDER="${INCIDENT_COMMANDER:-incident-commander@company.com}"
ENGINEERING_LEAD="${ENGINEERING_LEAD:-eng-lead@company.com}"
CTO="${CTO:-cto@company.com}"

# Integration endpoints
PAGERDUTY_KEY="${PAGERDUTY_INTEGRATION_KEY:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
JIRA_API="${JIRA_API_URL:-}"
ZOOM_API="${ZOOM_API_URL:-}"

# Incident tracking
INCIDENT_DIR="$PROJECT_ROOT/secops/6-reports/incidents/$TIMESTAMP"
INCIDENT_REPORT="$INCIDENT_DIR/INCIDENT-$TIMESTAMP.md"
INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$INCIDENT_DIR"

echo "Incident ID: $INCIDENT_ID"
echo "Severity: $SEVERITY"
echo "Type: $INCIDENT_TYPE"
echo "Environment: $ENVIRONMENT"
echo "Incident Directory: $INCIDENT_DIR"
echo ""

# ============================================================================
# Severity Configuration
# ============================================================================

get_escalation_chain() {
    case "$SEVERITY" in
        P1)
            # Critical - page everyone
            echo "$ONCALL_ENGINEER $INCIDENT_COMMANDER $ENGINEERING_LEAD $CTO"
            ;;
        P2)
            # High - page on-call and IC
            echo "$ONCALL_ENGINEER $INCIDENT_COMMANDER $ENGINEERING_LEAD"
            ;;
        P3)
            # Medium - notify on-call
            echo "$ONCALL_ENGINEER $INCIDENT_COMMANDER"
            ;;
        P4)
            # Low - email notification
            echo "$ONCALL_ENGINEER"
            ;;
        *)
            echo "$ONCALL_ENGINEER"
            ;;
    esac
}

get_response_time() {
    case "$SEVERITY" in
        P1) echo "15 minutes" ;;
        P2) echo "1 hour" ;;
        P3) echo "4 hours" ;;
        P4) echo "1 business day" ;;
        *) echo "Unknown" ;;
    esac
}

# ============================================================================
# Page On-Call Engineer
# ============================================================================

page_oncall() {
    echo "📟 Paging on-call engineer..."

    ESCALATION_CHAIN=$(get_escalation_chain)
    RESPONSE_TIME=$(get_response_time)

    # PagerDuty
    if [ -n "$PAGERDUTY_KEY" ]; then
        echo "Creating PagerDuty incident..."

        PD_RESPONSE=$(curl -s -X POST https://events.pagerduty.com/v2/enqueue \
            -H 'Content-Type: application/json' \
            -d "{
                \"routing_key\": \"$PAGERDUTY_KEY\",
                \"event_action\": \"trigger\",
                \"payload\": {
                    \"summary\": \"[$SEVERITY] $INCIDENT_TYPE - $ENVIRONMENT\",
                    \"severity\": \"critical\",
                    \"source\": \"deployment-automation\",
                    \"custom_details\": {
                        \"incident_id\": \"$INCIDENT_ID\",
                        \"incident_type\": \"$INCIDENT_TYPE\",
                        \"environment\": \"$ENVIRONMENT\",
                        \"project\": \"$PROJECT_ROOT\",
                        \"response_time\": \"$RESPONSE_TIME\",
                        \"incident_report\": \"$INCIDENT_REPORT\"
                    }
                },
                \"links\": [
                    {
                        \"href\": \"file://$INCIDENT_REPORT\",
                        \"text\": \"Incident Report\"
                    }
                ]
            }")

        DEDUP_KEY=$(echo "$PD_RESPONSE" | jq -r '.dedup_key // empty')

        if [ -n "$DEDUP_KEY" ]; then
            echo -e "${GREEN}✓ PagerDuty incident created: $DEDUP_KEY${NC}"
            echo "$DEDUP_KEY" > "$INCIDENT_DIR/pagerduty-incident.txt"
        else
            echo -e "${RED}✗ Failed to create PagerDuty incident${NC}"
        fi
    fi

    # Slack
    if [ -n "$SLACK_WEBHOOK" ]; then
        echo "Posting to Slack #incidents channel..."

        SLACK_COLOR="danger"
        [ "$SEVERITY" = "P3" ] && SLACK_COLOR="warning"
        [ "$SEVERITY" = "P4" ] && SLACK_COLOR="#808080"

        curl -s -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{
                \"text\": \"🚨 [$SEVERITY] Incident Escalation\",
                \"attachments\": [{
                    \"color\": \"$SLACK_COLOR\",
                    \"title\": \"$INCIDENT_TYPE - $ENVIRONMENT\",
                    \"fields\": [
                        {\"title\": \"Incident ID\", \"value\": \"$INCIDENT_ID\", \"short\": true},
                        {\"title\": \"Severity\", \"value\": \"$SEVERITY\", \"short\": true},
                        {\"title\": \"Environment\", \"value\": \"$ENVIRONMENT\", \"short\": true},
                        {\"title\": \"Response Time\", \"value\": \"$RESPONSE_TIME\", \"short\": true},
                        {\"title\": \"Escalation Chain\", \"value\": \"$ESCALATION_CHAIN\", \"short\": false},
                        {\"title\": \"Incident Report\", \"value\": \"$INCIDENT_REPORT\", \"short\": false}
                    ],
                    \"footer\": \"Incident Escalation System\",
                    \"ts\": $(date +%s)
                }]
            }" 2>/dev/null && echo -e "${GREEN}✓ Slack notification sent${NC}" || echo -e "${RED}✗ Slack notification failed${NC}"
    fi

    # Email
    echo "Sending email notifications..."
    for contact in $ESCALATION_CHAIN; do
        mail -s "🚨 [$SEVERITY] $INCIDENT_TYPE - $ENVIRONMENT" "$contact" <<EOF
Incident ID: $INCIDENT_ID
Severity: $SEVERITY
Type: $INCIDENT_TYPE
Environment: $ENVIRONMENT
Response Time: $RESPONSE_TIME

Incident Report: $INCIDENT_REPORT

Please join the incident bridge immediately.

---
Automated Incident Escalation System
EOF
        echo "  ✓ Emailed $contact"
    done

    echo ""
}

# ============================================================================
# Create Incident Report
# ============================================================================

create_incident_report() {
    echo "📄 Creating incident report..."

    cat > "$INCIDENT_REPORT" <<EOF
# Incident Report: $INCIDENT_ID

**Created:** $(date -Iseconds)
**Severity:** $SEVERITY
**Type:** $INCIDENT_TYPE
**Environment:** $ENVIRONMENT
**Status:** ACTIVE

---

## Incident Summary

**What happened:**
- Deployment/rollback failed and requires manual intervention
- Type: $INCIDENT_TYPE
- Severity: $SEVERITY
- Environment: $ENVIRONMENT

**Impact:**
- $(get_impact_description)

**Response Time:** $(get_response_time)

---

## Escalation Chain

| Role | Contact | Paged |
|------|---------|-------|
| On-Call Engineer | $ONCALL_ENGINEER | ✅ |
| Incident Commander | $INCIDENT_COMMANDER | $([ "$SEVERITY" = "P1" ] || [ "$SEVERITY" = "P2" ] && echo "✅" || echo "❌") |
| Engineering Lead | $ENGINEERING_LEAD | $([ "$SEVERITY" = "P1" ] && echo "✅" || echo "❌") |
| CTO | $CTO | $([ "$SEVERITY" = "P1" ] && echo "✅" || echo "❌") |

---

## Incident Bridge

**Zoom Link:** ${ZOOM_INCIDENT_BRIDGE:-TBD}
**Slack Channel:** ${SLACK_INCIDENT_CHANNEL:-#incident-$INCIDENT_ID}

---

## Timeline

| Time | Event |
|------|-------|
| $(date -Iseconds) | Incident detected and escalation triggered |

---

## Technical Details

**Project:** $PROJECT_ROOT
**Incident Type:** $INCIDENT_TYPE

### System Status

**Last Health Check:**
\`\`\`
# Run health check
cd /path/to/GP-CONSULTING/3-Hardening/monitoring-alerting/
./deployment-health-check.sh "$PROJECT_ROOT"
\`\`\`

### Recent Deployments

\`\`\`bash
# Check Kubernetes deployments
kubectl get deployments -A

# Check Terraform state
terraform state list

# Check Docker containers
docker ps -a
\`\`\`

---

## Runbooks

### For $INCIDENT_TYPE

$(get_runbook_link)

### General Incident Response

1. **Join incident bridge** - ${ZOOM_INCIDENT_BRIDGE:-TBD}
2. **Check monitoring dashboards**
   - CloudWatch: ${CLOUDWATCH_DASHBOARD:-TBD}
   - Datadog: ${DATADOG_DASHBOARD:-TBD}
   - Grafana: ${GRAFANA_DASHBOARD:-TBD}

3. **Review recent changes**
   \`\`\`bash
   cd "$PROJECT_ROOT"
   git log --oneline -10
   \`\`\`

4. **Check logs**
   \`\`\`bash
   # Kubernetes
   kubectl logs -n <namespace> <pod> --tail=100

   # CloudWatch
   aws logs tail /aws/ecs/<cluster> --follow

   # Docker
   docker logs <container> --tail=100
   \`\`\`

5. **Rollback if needed**
   \`\`\`bash
   cd /path/to/GP-CONSULTING/3-Hardening/rollback-mitigation/
   ./auto-rollback.sh
   \`\`\`

---

## Evidence Directory

All evidence and logs are collected in:
\`$INCIDENT_DIR\`

\`\`\`
$(ls -lh "$INCIDENT_DIR" 2>/dev/null || echo "No evidence collected yet")
\`\`\`

---

## Next Steps

### Immediate (< 15 min)
- [ ] Join incident bridge
- [ ] Assign incident commander
- [ ] Run health checks
- [ ] Review recent deployments
- [ ] Check monitoring dashboards

### Short-term (< 1 hour)
- [ ] Identify root cause
- [ ] Implement fix or rollback
- [ ] Verify fix in staging
- [ ] Deploy fix to production

### Long-term (< 1 week)
- [ ] Post-mortem meeting
- [ ] Document root cause
- [ ] Create preventive measures
- [ ] Update runbooks
- [ ] Share lessons learned

---

## Communication

**Internal:**
- Slack: ${SLACK_INCIDENT_CHANNEL:-#incident-$INCIDENT_ID}
- Email: incident-$INCIDENT_ID@company.com

**External:**
- Status Page: ${STATUS_PAGE:-TBD}
- Customer Support: ${SUPPORT_EMAIL:-support@company.com}

---

## Resolution

**Status:** ACTIVE

**Resolution Steps:**
_To be filled by incident commander_

**Root Cause:**
_To be filled after post-mortem_

**Preventive Measures:**
_To be filled after post-mortem_

---

*Auto-generated by escalate-incident.sh*
*Last Updated: $(date -Iseconds)*
EOF

    echo -e "${GREEN}✓ Incident report created: $INCIDENT_REPORT${NC}"
    echo ""
}

get_impact_description() {
    case "$INCIDENT_TYPE" in
        deployment-failure)
            echo "- Deployment failed, new features/fixes not deployed"
            echo "- Users may experience degraded functionality"
            ;;
        rollback-failure)
            echo "- CRITICAL: Both deployment AND rollback failed"
            echo "- System may be in inconsistent state"
            echo "- Manual intervention required immediately"
            ;;
        security-breach)
            echo "- CRITICAL: Potential security breach detected"
            echo "- Immediate investigation required"
            echo "- May need to notify customers/regulators"
            ;;
        data-loss)
            echo "- CRITICAL: Data integrity issue detected"
            echo "- Potential data loss or corruption"
            echo "- Backup restoration may be required"
            ;;
        performance)
            echo "- Severe performance degradation"
            echo "- Users experiencing slow response times"
            echo "- May lead to timeouts and failures"
            ;;
        *)
            echo "- Unknown incident type: $INCIDENT_TYPE"
            ;;
    esac
}

get_runbook_link() {
    case "$INCIDENT_TYPE" in
        deployment-failure)
            echo "See: /path/to/runbooks/deployment-failure.md"
            ;;
        rollback-failure)
            echo "See: /path/to/runbooks/rollback-failure.md"
            echo ""
            echo "**CRITICAL: Both deployment and rollback failed**"
            echo "1. DO NOT attempt automatic fixes"
            echo "2. Preserve all evidence"
            echo "3. Manual recovery required"
            ;;
        security-breach)
            echo "See: /path/to/runbooks/security-incident.md"
            echo ""
            echo "**Follow security incident response plan:**"
            echo "1. Isolate affected systems"
            echo "2. Preserve evidence"
            echo "3. Notify security team"
            echo "4. Begin forensic analysis"
            ;;
        *)
            echo "See: /path/to/runbooks/general-incident.md"
            ;;
    esac
}

# ============================================================================
# Collect Evidence
# ============================================================================

collect_evidence() {
    echo "🔍 Collecting evidence..."

    # System info
    uname -a > "$INCIDENT_DIR/system-info.txt" 2>&1 || true

    # Recent deployments
    git log --oneline -20 > "$INCIDENT_DIR/recent-commits.txt" 2>&1 || true

    # Run health check
    if [ -f "../monitoring-alerting/deployment-health-check.sh" ]; then
        ../monitoring-alerting/deployment-health-check.sh "$PROJECT_ROOT" all > "$INCIDENT_DIR/health-check.log" 2>&1 || true
    fi

    # K8s state
    if command -v kubectl &> /dev/null; then
        kubectl get all -A > "$INCIDENT_DIR/k8s-resources.txt" 2>&1 || true
        kubectl get events -A --sort-by='.lastTimestamp' | tail -50 > "$INCIDENT_DIR/k8s-events.txt" 2>&1 || true
    fi

    # Docker state
    if command -v docker &> /dev/null; then
        docker ps -a > "$INCIDENT_DIR/docker-containers.txt" 2>&1 || true
    fi

    # Terraform state
    if command -v terraform &> /dev/null && [ -d "$PROJECT_ROOT/terraform" ]; then
        cd "$PROJECT_ROOT/terraform" && terraform state list > "$INCIDENT_DIR/terraform-state.txt" 2>&1 || true
    fi

    echo -e "${GREEN}✓ Evidence collected in $INCIDENT_DIR${NC}"
    echo ""
}

# ============================================================================
# Main Execution
# ============================================================================

echo "🚨 Escalating incident..."
echo ""

# Validate severity
case "$SEVERITY" in
    P1|P2|P3|P4) ;;
    *)
        echo -e "${RED}Invalid severity: $SEVERITY${NC}"
        echo "Valid options: P1, P2, P3, P4"
        exit 1
        ;;
esac

# Create incident report
create_incident_report

# Collect evidence
collect_evidence

# Page on-call
page_oncall

# ============================================================================
# Summary
# ============================================================================

echo "═══════════════════════════════════════════════════════"
echo "✅ Incident Escalation Complete"
echo ""
echo "Incident ID: $INCIDENT_ID"
echo "Severity: $SEVERITY"
echo "Type: $INCIDENT_TYPE"
echo "Environment: $ENVIRONMENT"
echo ""
echo "📄 Incident Report: $INCIDENT_REPORT"
echo "📁 Evidence Directory: $INCIDENT_DIR"
echo ""
echo "Escalation chain notified:"
for contact in $(get_escalation_chain); do
    echo "  ✓ $contact"
done
echo ""
echo "Expected response time: $(get_response_time)"
echo ""
echo "Next steps:"
echo "  1. Join incident bridge: ${ZOOM_INCIDENT_BRIDGE:-TBD}"
echo "  2. Review incident report: $INCIDENT_REPORT"
echo "  3. Check evidence in: $INCIDENT_DIR"
echo "  4. Follow runbook for: $INCIDENT_TYPE"
echo ""
