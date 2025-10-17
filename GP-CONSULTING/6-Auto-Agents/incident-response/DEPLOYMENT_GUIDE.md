# GuardDuty Incident Response - Deployment Guide

**Status:** Production Ready
**Demo Ready:** Yes
**Date:** October 13, 2025

---

## 🚀 Quick Deploy (5 Minutes)

```bash
cd ~/linkops-industries/GP-copilot/GP-CONSULTING/agents/incident-response

# 1. Deploy to dev environment (dry-run mode)
./deploy.sh dev

# 2. Test the deployment
./deploy.sh dev --test

# 3. Check the results
aws logs tail /aws/lambda/guardduty-incident-response --follow
```

**That's it!** The incident response system is now deployed and ready.

---

## 📋 Prerequisites

### Required
- [x] AWS CLI installed and configured
- [x] Python 3.11+ installed
- [x] boto3 installed (`pip install boto3`)
- [x] AWS credentials with admin access
- [x] GuardDuty enabled in the region

### Optional (for production)
- [ ] SNS email verified
- [ ] Slack webhook configured
- [ ] PagerDuty integration key
- [ ] Security team trained on rollback procedures

---

## 🏗️ Architecture

```
┌─────────────┐
│  GuardDuty  │ Continuous threat detection
└──────┬──────┘
       │ Finding (severity >= 4.0)
       ▼
┌──────────────┐
│  CloudWatch  │ Event filtering
│    Events    │
└──────┬───────┘
       │ Invoke
       ▼
┌──────────────────────────────────────┐
│  Lambda: guardduty-incident-response │
│  ────────────────────────────────── │
│  1. Parse finding                     │
│  2. Determine severity               │
│  3. Execute response:                │
│     • CRITICAL → Isolate + Forensics │
│     • HIGH → Isolate + Forensics     │
│     • MEDIUM → Tag + Evidence        │
│     • LOW → Log only                 │
└──────┬───────────────────────────────┘
       │
       ├─→ EC2 (Modify security groups)
       ├─→ IAM (Deactivate keys, deny policy)
       ├─→ S3 (Store forensics evidence)
       ├─→ SNS (Notify security team)
       └─→ CloudWatch Logs (Audit trail)
```

---

## 📦 What Gets Deployed

### AWS Resources Created

1. **Lambda Function**
   - Name: `guardduty-incident-response`
   - Runtime: Python 3.11
   - Memory: 512 MB
   - Timeout: 5 minutes
   - Code: guardduty_responder.py + forensics_collector.py

2. **S3 Bucket**
   - Name: `forensics-evidence-{region}-{account-id}`
   - Encryption: AES-256
   - Versioning: Enabled
   - Public Access: Blocked
   - Lifecycle: 90-day retention

3. **SNS Topic**
   - Name: `security-incidents`
   - Subscribers: Your email address
   - Used for: Critical/High alerts

4. **CloudWatch Event Rule**
   - Name: `guardduty-incident-response`
   - Trigger: GuardDuty findings (severity >= 4.0)
   - Target: Lambda function

5. **IAM Role**
   - Name: `GuardDutyIncidentResponseRole`
   - Permissions:
     - EC2 (instance isolation)
     - IAM (credential lockdown)
     - S3 (forensics storage)
     - SSM (log collection)
     - CloudTrail (API audit)
     - SNS (notifications)

### Total Resources: 5 (Lambda, S3, SNS, EventBridge, IAM)

---

## 🎯 Deployment Environments

### Dev Environment (Recommended First)

```bash
./deploy.sh dev
```

**Configuration:**
- Dry Run: `true` (no actual changes)
- Minimum Severity: `1.0` (captures all findings for testing)
- Notifications: Dev team email
- Purpose: Testing and validation

**What it does:**
- Deploys fully functional Lambda
- Processes ALL GuardDuty findings
- Logs what WOULD happen (no actual isolation)
- Safe to test in production AWS account

### Production Environment

```bash
./deploy.sh prod
```

**Configuration:**
- Dry Run: `false` (REAL changes)
- Minimum Severity: `4.0` (HIGH and CRITICAL only)
- Notifications: Security team email
- Purpose: Live threat response

**What it does:**
- Automatically isolates compromised resources
- Collects forensics evidence
- Pages on-call team for CRITICAL
- Real isolation = real impact

⚠️ **Warning:** Production mode will actually isolate resources. Ensure rollback procedures are documented first.

---

## 🧪 Testing

### Test 1: Dry Run Test (Safe)

```bash
cd ~/linkops-industries/GP-copilot/GP-CONSULTING/agents/incident-response

# Test with sample finding
python3 guardduty_responder.py --finding-file test-finding.json --dry-run
```

**Expected Output:**
```json
{
  "response_level": "CRITICAL",
  "actions": [
    {"action": "isolate_ec2", "success": true, "dry_run": true},
    {"action": "trigger_forensics", "success": true, "dry_run": true},
    {"action": "send_critical_alert", "success": true, "dry_run": true}
  ],
  "success": true,
  "finding_id": "test-finding-20251013-001",
  "severity_level": "CRITICAL"
}
```

### Test 2: Lambda Local Test

```bash
# Test Lambda handler locally
python3 lambda_handler.py
```

**Expected:** Lambda processes test finding successfully in dry-run mode

### Test 3: AWS Lambda Test (After Deployment)

```bash
# Deploy and test
./deploy.sh dev --test
```

**Expected:** Lambda invoked successfully, logs visible in CloudWatch

### Test 4: GuardDuty Sample Findings (Safe)

```bash
# Enable GuardDuty sample findings
aws guardduty create-sample-findings \
  --detector-id YOUR_DETECTOR_ID \
  --finding-types UnauthorizedAccess:EC2/SSHBruteForce

# Check CloudWatch Logs
aws logs tail /aws/lambda/guardduty-incident-response --follow
```

**Expected:** Lambda processes sample finding, logs show dry-run actions

---

## 📊 Monitoring

### CloudWatch Logs

```bash
# View Lambda execution logs
aws logs tail /aws/lambda/guardduty-incident-response --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/guardduty-incident-response \
  --filter-pattern "ERROR"

# Count executions
aws logs filter-log-events \
  --log-group-name /aws/lambda/guardduty-incident-response \
  --filter-pattern "Processing finding"
```

### Forensics Evidence

```bash
# List evidence collected
aws s3 ls s3://forensics-evidence-us-east-1/ --recursive

# Download chain of custody report
aws s3 cp s3://forensics-evidence-us-east-1/incident-123/chain-of-custody.json -
```

### Metrics to Track

1. **Response Time:** Time from finding to isolation
2. **Success Rate:** % of successful isolations
3. **False Positives:** Count of rollbacks needed
4. **Evidence Integrity:** Verify SHA-256 hashes

---

## 🔄 Rollback Procedures

### Rollback EC2 Isolation

```bash
# Option 1: Using the responder tool
python3 guardduty_responder.py \
  --finding-id i-abc123 \
  --action rollback

# Option 2: Manual rollback
aws ec2 describe-instances --instance-ids i-abc123 \
  --query 'Reservations[0].Instances[0].Tags[?Key==`OriginalSGs`].Value' \
  --output text

# Restore original security groups
aws ec2 modify-instance-attribute \
  --instance-id i-abc123 \
  --groups sg-original1 sg-original2
```

### Rollback IAM Lockdown

```bash
# Remove deny-all policy
aws iam delete-user-policy \
  --user-name compromised-user \
  --policy-name GuardDutyIncidentDenyAll

# Reactivate access key
aws iam update-access-key \
  --user-name compromised-user \
  --access-key-id AKIAEXAMPLE \
  --status Active
```

---

## 🔧 Configuration

### Environment Variables (Lambda)

```bash
# Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name guardduty-incident-response \
  --environment Variables={
      DRY_RUN=false,
      SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:security-incidents,
      FORENSICS_BUCKET=forensics-evidence-us-east-1
  }
```

### Change Severity Threshold

```bash
# Update CloudFormation stack to capture MEDIUM+ (3.0+)
aws cloudformation update-stack \
  --stack-name guardduty-incident-response-prod \
  --use-previous-template \
  --parameters ParameterKey=MinimumSeverity,ParameterValue=3.0 \
  --capabilities CAPABILITY_NAMED_IAM
```

---

## 🚨 Troubleshooting

### Issue: Lambda Timeout

**Symptom:** Lambda times out after 5 minutes

**Solution:**
```bash
aws lambda update-function-configuration \
  --function-name guardduty-incident-response \
  --timeout 600  # Increase to 10 minutes
```

### Issue: Permission Denied

**Symptom:** Lambda fails with "AccessDenied" error

**Solution:** Check IAM role has required permissions
```bash
aws iam get-role-policy \
  --role-name GuardDutyIncidentResponseRole \
  --policy-name IncidentResponsePolicy
```

### Issue: No Findings Processed

**Symptom:** Lambda never triggered

**Possible Causes:**
1. GuardDuty not enabled
2. No findings generated yet
3. Severity threshold too high
4. Event rule disabled

**Solution:**
```bash
# Check GuardDuty status
aws guardduty list-detectors

# Check event rule
aws events describe-rule --name guardduty-incident-response

# Generate test findings
aws guardduty create-sample-findings \
  --detector-id YOUR_DETECTOR_ID \
  --finding-types UnauthorizedAccess:EC2/SSHBruteForce
```

---

## 📈 Production Checklist

Before enabling production mode (`DRY_RUN=false`):

- [ ] Tested in dev environment with dry-run
- [ ] Reviewed and tested rollback procedures
- [ ] SNS email confirmed and verified
- [ ] Security team trained on incident response
- [ ] Documented escalation procedures
- [ ] Set up monitoring dashboards
- [ ] Created runbook for common scenarios
- [ ] Tested with GuardDuty sample findings
- [ ] Verified forensics bucket permissions
- [ ] Established evidence retention policy
- [ ] Integrated with ticketing system (Jira/ServiceNow)
- [ ] Configured PagerDuty/Slack notifications
- [ ] Performed tabletop exercise with team

---

## 🎬 Demo Script for Interviews

```bash
# 1. Show the problem (2 min)
cat ../SCANNER_FIXER_MATRIX.txt
# Point out: Runtime incident response was 0%

# 2. Show the solution architecture (3 min)
cat README.md  # Architecture diagram

# 3. Deploy to dev environment (2 min)
./deploy.sh dev
# Explain: Creates Lambda, S3, SNS, EventBridge rule

# 4. Test with sample finding (3 min)
python3 guardduty_responder.py --finding-file test-finding.json --dry-run
# Show: CRITICAL finding → Isolation + Forensics + Alert

# 5. Show CloudWatch Logs (2 min)
aws logs tail /aws/lambda/guardduty-incident-response --since 5m
# Point out: Sub-2-minute response time

# 6. Explain production deployment (3 min)
# ./deploy.sh prod  # (Don't actually run in demo)
# Explain: Same stack, but dry_run=false for real isolation

# Total: 15 minutes
```

---

## 📚 Additional Resources

- [guardduty_responder.py](guardduty_responder.py) - Main responder code (650 lines)
- [forensics_collector.py](forensics_collector.py) - Evidence collector (600 lines)
- [lambda_handler.py](lambda_handler.py) - Lambda handler
- [cloudformation-template.yaml](cloudformation-template.yaml) - Infrastructure as Code
- [README.md](README.md) - Component documentation
- [../INCIDENT_RESPONSE_COMPLETE.md](../INCIDENT_RESPONSE_COMPLETE.md) - Implementation summary

---

## 🎯 Success Metrics

After deployment, measure:

1. **Mean Time to Isolate (MTTI):** < 2 minutes
2. **Mean Time to Evidence (MTTE):** < 5 minutes
3. **Detection to Response:** < 3 minutes total
4. **False Positive Rate:** < 5%
5. **Evidence Integrity:** 100% (SHA-256 verified)

---

**Version:** 1.0
**Status:** Production Ready
**Last Updated:** October 13, 2025

**Questions?** Review README.md or check CloudWatch Logs
