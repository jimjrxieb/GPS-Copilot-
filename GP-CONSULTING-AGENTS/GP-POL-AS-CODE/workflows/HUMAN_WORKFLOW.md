# 👤 Human Policy-as-Code Workflow

## 🎯 **Complete Human-Driven Policy Management**

### **Scenario**: Security consultant manually managing policies, evaluating systems, and deploying controls.

---

## 🔄 **Phase 1: Policy Development & Testing**

### **Step 1: Create/Modify Policies**
```bash
# Edit policy files directly
nano policies/pod-security.rego

# Test policy logic locally
opa fmt policies/pod-security.rego           # Format policy
opa test policies/pod-security.rego --verbose # Run built-in tests
```

### **Step 2: Validate Policy Syntax**
```bash
# Check all policies for syntax errors
for policy in policies/*.rego; do
    echo "Validating $policy"
    opa fmt "$policy" --diff || echo "❌ Format issues in $policy"
done

# Run comprehensive test suite
opa test policies/ --verbose --explain=full
```

### **Step 3: Local Testing Against Sample Data**
```bash
# Create test input
cat > test-input.json << EOF
{
  "file_type": "config",
  "file_path": "bad-pod.yaml",
  "file_content": "privileged: true\nrunAsUser: 0\nhostNetwork: true"
}
EOF

# Test policy evaluation
opa eval --data policies/security.rego \
  --input test-input.json \
  "data.security.violations"

# Expected output: 3 violations detected
```

---

## 🔄 **Phase 2: Project/Environment Scanning**

### **Step 4: Scan Client Projects**
```bash
# Scan specific project
python scanners/opa_scanner.py \
  ../../../GP-PROJECTS/Portfolio/ \
  kubernetes.admission.security.pods

# Review results
cat /home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/scans/opa_latest.json

# Generate human-readable report
python scanners/opa_scanner.py \
  --target ../../../GP-PROJECTS/Portfolio/ \
  --output-format markdown \
  --save-report portfolio_security_assessment.md
```

### **Step 5: Analyze Violation Patterns**
```bash
# Review violations by severity
jq '.findings[] | select(.severity == "CRITICAL")' \
  /home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/scans/opa_latest.json

# Count violations by policy
jq '.findings | group_by(.policy) | map({policy: .[0].policy, count: length})' \
  /home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/scans/opa_latest.json
```

---

## 🔄 **Phase 3: Policy Generation & Enhancement**

### **Step 6: Generate New Policies from Violations**
```bash
# Auto-generate policies based on common violations
python generators/opa_policy_generator.py \
  --violations-file /home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/scans/opa_latest.json \
  --output-dir policies/ \
  --policy-type kubernetes

# Review generated policy
cat policies/generated_kubernetes_policy.rego

# Test generated policy
opa test policies/generated_kubernetes_policy.rego
```

### **Step 7: Policy Refinement**
```bash
# Merge with existing policies or create new ones
# Human decision: integrate vs separate policy file

# Example: Add to existing pod-security.rego
echo "
# Generated from violation patterns on $(date)
violation[{\"msg\": msg, \"severity\": \"high\", \"control\": \"CUSTOM-1\"}] {
    container := input.request.object.spec.containers[_]
    container.image
    not startswith(container.image, \"registry.company.com/\")
    msg := \"Container uses untrusted registry\"
}" >> policies/pod-security.rego

# Validate merged policy
opa test policies/pod-security.rego
```

---

## 🔄 **Phase 4: Deployment Decision**

### **Step 8: Choose Deployment Mode**

#### **Option A: CI/CD Scanner Integration**
```bash
# Copy to project repository
cp -r . /path/to/client/project/.policies/

# Add to GitHub Actions workflow
cat >> /path/to/client/project/.github/workflows/security.yml << EOF
      - name: Run OPA Policy Scan
        run: |
          opa eval --data .policies/policies/ --input k8s-manifests/ \\
            "data.kubernetes.admission.deny[x]" \\
            --format json > opa-violations.json

          # Fail if critical violations found
          critical_count=\$(jq '.result[0].expressions[0].value | length' opa-violations.json)
          if [ "\$critical_count" -gt 0 ]; then
            echo "❌ Critical policy violations detected"
            exit 1
          fi
EOF
```

#### **Option B: OPA Server Deployment**
```bash
# Start OPA server locally for testing
python managers/opa_manager.py --start-server --port 8181

# Test server endpoint
curl -X POST localhost:8181/v1/data/security/violations \
  -H 'Content-Type: application/json' \
  -d @test-input.json

# Deploy to production server (human decision required)
python managers/opa_manager.py --deploy-server --environment production
```

#### **Option C: Gatekeeper Kubernetes Integration**
```bash
# Check cluster access
kubectl cluster-info

# Install Gatekeeper (REQUIRES HUMAN CONFIRMATION)
echo "⚠️  This will install Gatekeeper admission controller"
echo "Do you want to proceed? (y/N)"
read confirmation

if [ "$confirmation" = "y" ]; then
    kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

    # Wait for Gatekeeper pods
    kubectl wait --for=condition=Ready pods -l gatekeeper.sh/system=yes -n gatekeeper-system --timeout=60s

    # Deploy constraint templates
    python managers/opa_cluster_manager.py --deploy-constraints --dry-run

    echo "Review the above constraints. Deploy them? (y/N)"
    read deploy_confirmation

    if [ "$deploy_confirmation" = "y" ]; then
        python managers/opa_cluster_manager.py --deploy-constraints
    fi
fi
```

---

## 🔄 **Phase 5: Monitoring & Maintenance**

### **Step 9: Monitor Policy Violations**
```bash
# Check Gatekeeper violations (if deployed)
kubectl get K8sRequiredLabels -A

# Review violation events
kubectl get events --field-selector reason=FailedCreate -A

# Generate compliance report
python ../workflows/full_workflow.py --compliance-report --client Portfolio
```

### **Step 10: Policy Updates & Versioning**
```bash
# Backup current policies
cp -r policies/ policies-backup-$(date +%Y%m%d)

# Update policies based on new requirements
git add policies/
git commit -m "Update pod security policies - add registry restrictions"
git tag v1.1.0

# Test updated policies against existing deployments
python scanners/opa_scanner.py --target ../../../GP-PROJECTS/Portfolio/ --policies policies/
```

---

## 📋 **Human Decision Points**

### **🚨 Critical Decisions Requiring Human Judgment:**

1. **Policy Severity Levels**: Determining if violation should be CRITICAL vs HIGH
2. **Deployment Mode**: Scanner vs Server vs Gatekeeper based on environment
3. **Rollback Decisions**: When policy changes break existing deployments
4. **Exception Handling**: When to allow policy violations for business reasons
5. **Cluster Impact**: Understanding downstream effects of admission control

### **✅ Safe Automation Points:**

1. **Policy Formatting**: `opa fmt` can run automatically
2. **Syntax Validation**: `opa test` can run in CI/CD
3. **Report Generation**: Violation reports can be auto-generated
4. **Backup Creation**: Policy versioning can be automated

---

## 🎯 **Human Workflow Summary**

```
Policy Development → Testing → Project Scanning → Analysis →
Policy Generation → Deployment Decision → Implementation →
Monitoring → Maintenance

Each phase requires human expertise for:
- Business context understanding
- Risk assessment
- Impact analysis
- Strategic decisions
```

**Time Investment**: 2-4 hours for complete workflow cycle
**Expertise Required**: Kubernetes security, OPA/Rego, compliance frameworks
**Risk Level**: Medium (with proper testing and staged deployment)

---
*Human-Driven Policy-as-Code Management*
*GP-Copilot Policy Management System*
*Date: 2025-09-29*