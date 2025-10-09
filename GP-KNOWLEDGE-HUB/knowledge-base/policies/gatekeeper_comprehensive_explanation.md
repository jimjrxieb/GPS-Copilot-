# Gatekeeper vs Scanners - Comprehensive Understanding

## The Key Distinction

**Scanners (Bandit, Trivy, Checkov, SonarQube, Snyk):**
- Run AFTER code/configs are written
- Find problems in existing code
- Generate reports saying "you have issues"
- Don't block anything - just inform

**OPA/Gatekeeper:**
- Runs BEFORE resources are deployed
- **Actively prevents** bad configs from being created
- Real-time enforcement, not post-analysis
- Acts as a gatekeeper (hence the name)

## Better Analogy

**Scanners are like TSA checking your luggage** - they scan what you brought and tell you if there's a problem, but you already packed it.

**OPA is like a bouncer at a club** - checks you at the door and won't let you in if you don't meet requirements. You never get inside with the wrong config.

## The Workflow Difference

**Traditional Scanning (Checkov/Trivy):**
```
Write manifest → Scan with tool → See violations → Fix manually → Re-scan
```

**OPA/Gatekeeper:**
```
Write manifest → kubectl apply → API Server asks Gatekeeper → Policy violation → REJECTED (never created)
```

## Why This Matters

Checkov can tell you "this pod runs as root" AFTER you write it. Gatekeeper **prevents you from creating that pod at all**.

Your comparison to SonarQube with blocking is actually pretty accurate - if SonarQube could block commits/deploys, that's similar. Some CI/CD pipelines do this with quality gates, but that's still in the pipeline, not at the Kubernetes API level.

## The Real Difference

**Scanners:** Find vulnerabilities in images, code, configs (passive detection)

**OPA:** Enforces organizational policies on what can be deployed (active prevention)

**You need both.** Trivy finds the vulnerable base image. OPA prevents you from deploying images from untrusted registries. They solve different problems.

For your interview: "OPA is a policy enforcement engine, not a vulnerability scanner. It prevents policy violations at deployment time, whereas tools like Trivy and Checkov detect security issues in existing code and configs."

---

# Kubernetes Admission Control and Gatekeeper Architecture

## The Kubernetes Request Flow

When you try to create/update/delete anything in Kubernetes:

```
kubectl apply → API Server → Admission Controllers → etcd (storage)
```

The API server doesn't just blindly accept your request. It runs it through a series of checks called **admission controllers**.

## What Are Admission Controllers?

Admission controllers are plugins that intercept requests to the Kubernetes API server. They can:
- **Validate** (reject bad configs)
- **Mutate** (modify requests automatically)

**Built-in examples:**
- `PodSecurityAdmission` - enforces pod security standards
- `ResourceQuota` - enforces namespace resource limits
- `NamespaceLifecycle` - prevents operations on terminating namespaces

## Where Does Gatekeeper Fit?

Gatekeeper is a **custom admission controller** that uses OPA (Open Policy Agent) as its policy engine.

```
Your Request
    ↓
API Server
    ↓
[Built-in Admission Controllers] → PodSecurity, ResourceQuota, etc.
    ↓
[Gatekeeper Admission Webhook] → Calls OPA to evaluate policies
    ↓
Accept or Reject
```

## The Technical Details

**Gatekeeper runs as:**
- A pod in your cluster (typically in `gatekeeper-system` namespace)
- A ValidatingWebhookConfiguration that tells Kubernetes to send it requests
- A MutatingWebhookConfiguration for policy-based mutations

**When you create a pod:**
1. Kubernetes API server receives the request
2. It checks its ValidatingWebhookConfiguration
3. Sees Gatekeeper is registered for Pod resources
4. Sends the pod spec to Gatekeeper's webhook endpoint
5. Gatekeeper evaluates your Rego policies against the pod
6. Returns allow/deny to the API server
7. API server accepts or rejects based on response

## Why OPA + Gatekeeper Instead of Just Gatekeeper?

**OPA is the engine**, Gatekeeper is the Kubernetes integration:
- **OPA**: General-purpose policy engine, can evaluate any structured data
- **Gatekeeper**: Kubernetes-native wrapper that provides CRDs, audit, and admission control

## The CRDs Gatekeeper Adds

**ConstraintTemplate**: Defines reusable policy templates
```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8spspprivileged
spec:
  crd:
    spec:
      names:
        kind: K8sPSPPrivileged
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8spspprivileged
        violation[{"msg": msg}] {
          # Your Rego policy here
        }
```

**Constraint**: Instances of templates that enforce specific policies
```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPSPPrivileged
metadata:
  name: deny-privileged-containers
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
```

## Interview Questions They'll Ask

**Q: Can you bypass Gatekeeper policies?**
A: Yes, if you have cluster-admin privileges you can modify/delete the ValidatingWebhookConfiguration. Also, existing resources aren't affected unless you enable audit mode.

**Q: What happens if Gatekeeper is down?**
A: Depends on `failurePolicy` in the webhook config. `Fail` means reject all requests (safe but disruptive). `Ignore` means allow everything (dangerous but available).

**Q: How do you debug rejected requests?**
A: Check Gatekeeper pod logs, look at the constraint status, use `kubectl describe` on the resource to see rejection message.

**Q: Difference between validation and mutation?**
A: Validation says yes/no. Mutation changes the resource (like adding default labels or security contexts) before it's stored.

## Real-World Gotcha

Gatekeeper policies only apply to NEW resources or UPDATES. If you deploy a policy that denies privileged pods, existing privileged pods keep running. You need to run audit mode to find existing violations.

The key interview answer: "Gatekeeper is a Kubernetes admission controller that uses OPA's Rego language to enforce custom policies on resource creation and updates. It runs as a webhook that the API server calls before persisting resources to etcd."