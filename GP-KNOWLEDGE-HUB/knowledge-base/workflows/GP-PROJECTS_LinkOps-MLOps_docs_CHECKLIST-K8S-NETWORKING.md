# Kubernetes Networking & Infrastructure Checklist

This document provides a comprehensive checklist for implementing Kubernetes networking, security, and infrastructure components.

---

## 🌐 Service Types & Networking

✅ **Goal:** Properly expose applications with appropriate service types and networking.

### Service Types Checklist
- [ ] **ClusterIP** - Internal service communication
- [ ] **NodePort** - External access via node ports
- [ ] **LoadBalancer** - Cloud provider load balancer
- [ ] **ExternalName** - DNS-based service discovery

### Implementation
```yaml
# ClusterIP (internal)
apiVersion: v1
kind: Service
metadata:
  name: mlops-platform
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: mlops-platform

# LoadBalancer (external)
apiVersion: v1
kind: Service
metadata:
  name: mlops-platform-lb
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: mlops-platform
```

---

## 🚪 Ingress Configuration

✅ **Goal:** Configure ingress for external access with SSL termination and routing.

### Ingress Checklist
- [ ] Ingress controller installed (nginx, traefik, etc.)
- [ ] SSL certificates configured
- [ ] Host-based routing rules
- [ ] Path-based routing rules
- [ ] Rate limiting configured
- [ ] CORS headers set

### Implementation
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mlops-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - mlops.example.com
    secretName: mlops-tls
  rules:
  - host: mlops.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mlops-platform
            port:
              number: 8000
```

---

## 🔐 RBAC & Security

✅ **Goal:** Implement proper role-based access control and security policies.

### RBAC Checklist
- [ ] Service accounts created for each application
- [ ] Roles defined with minimal required permissions
- [ ] Role bindings configured
- [ ] Network policies implemented
- [ ] Pod security policies configured
- [ ] Security contexts set

### Implementation
```yaml
# Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mlops-platform-sa
  namespace: mlops

---
# Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: mlops-platform-role
  namespace: mlops
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]

---
# Role Binding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: mlops-platform-rolebinding
  namespace: mlops
subjects:
- kind: ServiceAccount
  name: mlops-platform-sa
  namespace: mlops
roleRef:
  kind: Role
  name: mlops-platform-role
  apiGroup: rbac.authorization.k8s.io
```

---

## 💾 Persistent Storage (PVC)

✅ **Goal:** Configure persistent storage for applications that need data persistence.

### PVC Checklist
- [ ] Storage class defined
- [ ] PVC created with appropriate size
- [ ] PVC mounted in deployment
- [ ] Backup strategy implemented
- [ ] Storage monitoring configured

### Implementation
```yaml
# Storage Class
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"

---
# PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mlops-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi

---
# Deployment with PVC
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlops-platform
spec:
  template:
    spec:
      serviceAccountName: mlops-platform-sa
      containers:
      - name: mlops-platform
        image: mlops-platform:latest
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: mlops-data
```

---

## 🌍 Network Policies

✅ **Goal:** Implement network policies for microservice communication control.

### Network Policy Checklist
- [ ] Default deny all traffic
- [ ] Allow specific pod-to-pod communication
- [ ] Allow ingress traffic to services
- [ ] Allow egress traffic to external services
- [ ] Monitor policy violations

### Implementation
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mlops-network-policy
  namespace: mlops
spec:
  podSelector:
    matchLabels:
      app: mlops-platform
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to: []
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
```

---

## 🔍 Service Discovery & DNS

✅ **Goal:** Configure proper service discovery and DNS resolution.

### Service Discovery Checklist
- [ ] CoreDNS configured properly
- [ ] Service names resolve correctly
- [ ] External DNS integration (if needed)
- [ ] Service mesh considerations (Istio, Linkerd)

### Implementation
```yaml
# Headless Service for StatefulSets
apiVersion: v1
kind: Service
metadata:
  name: mlops-database
spec:
  clusterIP: None
  ports:
  - port: 5432
  selector:
    app: database
```

---

## 📊 Monitoring & Observability

✅ **Goal:** Implement comprehensive monitoring and observability.

### Monitoring Checklist
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards configured
- [ ] Alerting rules defined
- [ ] Log aggregation (ELK, Fluentd)
- [ ] Distributed tracing (Jaeger, Zipkin)
- [ ] Health checks implemented

### Implementation
```yaml
# Service with metrics port
apiVersion: v1
kind: Service
metadata:
  name: mlops-platform
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
spec:
  ports:
  - name: http
    port: 8000
    targetPort: 8000
  - name: metrics
    port: 8000
    targetPort: 8000
  selector:
    app: mlops-platform
```

---

## 🔧 LinkOps MLOps Platform Implementation

### Current Networking Status
✅ **Services Configured**
- MLOps Platform (ClusterIP + LoadBalancer)
- Audit Assess (ClusterIP)
- Whis Data Input (ClusterIP)
- Whis Enhance (ClusterIP)
- Frontend (LoadBalancer)

✅ **Ingress Configured**
- SSL termination with Let's Encrypt
- Host-based routing for services
- Rate limiting and CORS headers

✅ **RBAC Implemented**
- Service accounts for each component
- Minimal required permissions
- Network policies for security

### Implementation Commands

```bash
# Apply networking components
kubectl apply -f k8s/networking/
kubectl apply -f k8s/rbac/
kubectl apply -f k8s/storage/

# Verify networking
kubectl get services
kubectl get ingress
kubectl get networkpolicies

# Test connectivity
kubectl exec -it <pod> -- nslookup mlops-platform
```

### Next Steps
- [ ] Implement service mesh (Istio/Linkerd)
- [ ] Add distributed tracing
- [ ] Configure advanced monitoring
- [ ] Implement backup strategies 