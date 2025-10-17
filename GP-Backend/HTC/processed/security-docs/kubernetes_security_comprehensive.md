# Kubernetes Security Comprehensive Guide

## Cluster Security Architecture

### Control Plane Security
- **API Server**: Gateway to cluster, requires authentication/authorization
- **etcd**: Encrypted storage for cluster state and secrets
- **Scheduler**: Decides pod placement based on security policies
- **Controller Manager**: Enforces security policies and RBAC

### Node Security
- **kubelet**: Node agent, secures container runtime
- **kube-proxy**: Network proxy, enforces network policies
- **Container Runtime**: Containerd/Docker with security constraints

## Pod Security Standards (PSS)

### Privileged Profile
- **Use Case**: System-level workloads, CNI plugins
- **Security**: Minimal restrictions, highest privileges
- **Risk**: High - allows privileged containers, host access

### Baseline Profile
- **Use Case**: Standard applications with minimal security
- **Security**: Prevents most privilege escalations
- **Restrictions**:
  - No privileged containers
  - No host namespace sharing
  - Limited volume types
  - Restricted capabilities

### Restricted Profile
- **Use Case**: Security-critical applications
- **Security**: Hardened against privilege escalation
- **Restrictions**:
  - Non-root containers only
  - Read-only root filesystem
  - No privilege escalation
  - Dropped ALL capabilities
  - Seccomp profiles required

## Network Security

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  # No ingress rules = deny all ingress
```

### Micro-segmentation Patterns
```yaml
# Allow only specific app communication
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-to-api-only
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web
    ports:
    - protocol: TCP
      port: 8080
```

### Service Mesh Security
- **Istio**: mTLS between services, traffic encryption
- **Linkerd**: Automatic TLS, traffic policies
- **Consul Connect**: Service-to-service authentication

## RBAC (Role-Based Access Control)

### ClusterRole Examples
```yaml
# Read-only cluster access
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-reader
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
```

### Namespace-specific Role
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-manager
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "create", "delete"]
```

### Service Account Security
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: secure-app
automountServiceAccountToken: false  # Disable automatic token mounting
```

## Container Security Context

### Pod-level Security Context
```yaml
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
    supplementalGroups: [1000]
```

### Container-level Security Context
```yaml
spec:
  containers:
  - name: secure-app
    securityContext:
      allowPrivilegeEscalation: false
      runAsNonRoot: true
      runAsUser: 1000
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE  # Only if needed
```

## Secret Management

### Encrypted Secrets at Rest
```yaml
# Enable encryption in kube-apiserver
--encryption-provider-config=/etc/kubernetes/encryption.yaml
```

### External Secret Management
- **HashiCorp Vault**: Enterprise secret management
- **AWS Secrets Manager**: Cloud-native secrets
- **Azure Key Vault**: Azure-integrated secrets
- **External Secrets Operator**: K8s-native external secrets

### Secret Best Practices
```yaml
# Use stringData for automatic base64 encoding
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
stringData:
  username: "admin"
  password: "secure-password"
```

## Resource Security

### Resource Quotas
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: production
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "10"
```

### Limit Ranges
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-limits
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

## Admission Controllers

### Pod Security Admission
```yaml
# Namespace-level pod security
apiVersion: v1
kind: Namespace
metadata:
  name: secure-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### OPA Gatekeeper Policies
```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        properties:
          labels:
            type: array
            items:
              type: string
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredlabels
      violation[{"msg": msg}] {
        required := input.parameters.labels
        provided := input.review.object.metadata.labels
        missing := required[_]
        not provided[missing]
        msg := sprintf("Missing required label: %v", [missing])
      }
```

## Runtime Security

### Falco Rules for Kubernetes
```yaml
# Detect privileged containers
- rule: Privileged container started
  desc: Detect privileged container
  condition: >
    spawned_process and container and
    k8s_audit and
    ka.verb=create and
    ka.target.resource=pods and
    ka.req.pod.spec.containers[*].securityContext.privileged=true
  output: Privileged container started (user=%ka.user.name pod=%ka.target.name)
  priority: WARNING
```

### Pod Security Monitoring
- **Sysdig Secure**: Runtime threat detection
- **Aqua Security**: Container security platform
- **Twistlock/Prisma**: Comprehensive container security
- **Falco**: CNCF runtime security monitoring

## Image Security

### Image Scanning with Trivy
```bash
# Scan image for vulnerabilities
trivy image nginx:latest

# Scan with specific severity
trivy image --severity HIGH,CRITICAL nginx:latest

# Generate JSON report
trivy image --format json --output report.json nginx:latest
```

### Image Signing and Verification
```bash
# Sign image with Cosign
cosign sign --key cosign.key gcr.io/myproject/myimage:latest

# Verify signed image
cosign verify --key cosign.pub gcr.io/myproject/myimage:latest
```

### Admission Controller Image Policies
```yaml
# Only allow images from trusted registries
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: trusted-registry-only
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: check-registry
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Images must come from trusted registry"
      pattern:
        spec:
          containers:
          - image: "gcr.io/trusted-project/*"
```

## Compliance and Hardening

### CIS Kubernetes Benchmark Key Controls
- **1.1.1**: API server secure port configuration
- **1.1.12**: etcd data encryption at rest
- **1.2.6**: kubelet authentication and authorization
- **1.3.1**: Controller manager service account private key
- **4.1.1**: Worker node kubelet permissions
- **5.1.1**: RBAC minimization
- **5.2.5**: Minimize privileged containers

### NIST SP 800-190 Container Security
- **Image Lifecycle Management**: Vulnerability scanning, signing
- **Registry Security**: Access controls, image policies
- **Orchestrator Security**: RBAC, network policies
- **Container Runtime Security**: Isolation, monitoring
- **Host OS Security**: Kernel hardening, access controls

## Security Monitoring and Logging

### Audit Logging
```yaml
# Comprehensive audit policy
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets"]
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods"]
  verbs: ["create", "delete"]
```

### Metrics for Security Monitoring
- **Pod Security Standard violations**
- **RBAC policy violations**
- **Network policy denials**
- **Failed authentication attempts**
- **Privileged container starts**
- **Suspicious process executions**

## Integration with GP-Copilot

### When Kubernetes security issues are detected:

1. **Pod Security**: Reference PSS profiles for remediation
2. **RBAC Issues**: Apply principle of least privilege
3. **Network Policies**: Implement micro-segmentation
4. **Image Security**: Require vulnerability scanning
5. **Resource Limits**: Prevent resource exhaustion
6. **Compliance**: Map to CIS/NIST frameworks

### Escalation Criteria:
- **Privileged containers**: Immediate escalation
- **Missing RBAC**: High priority fix
- **Network policy gaps**: Medium priority
- **Resource limit missing**: Low priority automated fix

This knowledge enables Jade to provide contextual Kubernetes security guidance based on scanner findings and best practices.