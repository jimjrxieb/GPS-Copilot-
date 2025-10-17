package secrets.mutate

import future.keywords.in

# Mutating policy for secrets - Blocks hardcoded credentials, enforces Secrets Manager

# Block hardcoded database credentials
deny_hardcoded_db_credentials[msg] {
    input.request.kind.kind in ["Pod", "Deployment", "ConfigMap"]
    env := get_env_vars(input.request.object)
    contains_db_credential(env)

    msg := {
        "allowed": false,
        "reason": "Hardcoded database credentials detected. Use AWS Secrets Manager or Kubernetes Secrets.",
        "violation": "PCI-DSS 8.2.1 - Strong authentication and credential management",
        "remediation": "Create secret: kubectl create secret generic db-credentials --from-literal=password=xxx"
    }
}

contains_db_credential(env) {
    lower(env.name) in ["db_password", "database_password", "postgres_password"]
    env.value  # Direct value assignment (not valueFrom)
}

# Block hardcoded API keys
deny_hardcoded_api_keys[msg] {
    input.request.kind.kind in ["Pod", "Deployment", "ConfigMap"]
    env := get_env_vars(input.request.object)
    contains_api_key(env)

    msg := {
        "allowed": false,
        "reason": "Hardcoded API key detected. Use AWS Secrets Manager.",
        "violation": "SOC2 CC6.1 - Credential management",
        "remediation": "Store in Secrets Manager: aws secretsmanager create-secret --name api-key --secret-string xxx"
    }
}

contains_api_key(env) {
    lower(env.name) in ["api_key", "stripe_key", "sendgrid_key", "twilio_token"]
    env.value
}

# Block hardcoded JWT secrets
deny_hardcoded_jwt[msg] {
    input.request.kind.kind in ["Pod", "Deployment", "ConfigMap"]
    env := get_env_vars(input.request.object)
    lower(env.name) in ["jwt_secret", "jwt_key", "secret_key"]
    env.value

    msg := {
        "allowed": false,
        "reason": "Hardcoded JWT secret detected. Use Kubernetes Secret with rotation.",
        "violation": "PCI-DSS 8.2.1",
        "remediation": "kubectl create secret generic jwt-secret --from-literal=jwt_secret=$(openssl rand -base64 64)"
    }
}

# Mutate to use Secrets Manager instead
mutate_to_secrets_manager[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    container_path := get_container_path(input.request.kind.kind)
    container := object.get(input.request.object, container_path, [])[i]
    env := container.env[j]
    is_secret_env(env)

    patch := {
        "op": "replace",
        "path": sprintf("%s/%d/env/%d", [container_path, i, j]),
        "value": {
            "name": env.name,
            "valueFrom": {
                "secretKeyRef": {
                    "name": "securebank-secrets",
                    "key": lower(env.name)
                }
            }
        }
    }
}

is_secret_env(env) {
    lower(env.name) in [
        "db_password",
        "jwt_secret",
        "api_key",
        "stripe_key",
        "sendgrid_key"
    ]
    env.value  # Has direct value (should be valueFrom)
}

# Helper: Get environment variables
get_env_vars(obj) := env {
    obj.kind == "Pod"
    container := obj.spec.containers[_]
    env := container.env[_]
}

get_env_vars(obj) := env {
    obj.kind == "Deployment"
    container := obj.spec.template.spec.containers[_]
    env := container.env[_]
}

get_env_vars(obj) := env {
    obj.kind == "ConfigMap"
    env := {"name": key, "value": value}
    obj.data[key] = value
}

get_container_path("Pod") = "/spec/containers"
get_container_path("Deployment") = "/spec/template/spec/containers"

# Block ConfigMaps with sensitive data
deny_sensitive_configmap[msg] {
    input.request.kind.kind == "ConfigMap"
    input.request.object.data[key]
    is_sensitive_key(key)

    msg := {
        "allowed": false,
        "reason": sprintf("ConfigMap contains sensitive key: %s. Use Kubernetes Secret instead.", [key]),
        "violation": "SOC2 CC6.1",
        "remediation": "kubectl create secret generic <name> --from-literal=<key>=<value>"
    }
}

is_sensitive_key(key) {
    sensitive_keywords := ["password", "secret", "token", "key", "credential", "jwt"]
    keyword := sensitive_keywords[_]
    contains(lower(key), keyword)
}

# Enforce Secrets Manager annotation
mutate_add_secrets_annotation[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    spec := get_pod_spec(input.request.kind.kind, input.request.object)
    not spec.metadata.annotations["secrets-manager/enabled"]

    patch := {
        "op": "add",
        "path": get_annotation_path(input.request.kind.kind),
        "value": {
            "secrets-manager/enabled": "true",
            "secrets-manager/region": "us-east-1",
            "secrets-manager/secret-name": "securebank/app/credentials"
        }
    }
}

get_pod_spec("Pod", obj) = obj.spec
get_pod_spec("Deployment", obj) = obj.spec.template.spec

get_annotation_path("Pod") = "/spec/metadata/annotations"
get_annotation_path("Deployment") = "/spec/template/metadata/annotations"

# Main deny rules
deny[msg] {
    msg := deny_hardcoded_db_credentials[_]
}

deny[msg] {
    msg := deny_hardcoded_api_keys[_]
}

deny[msg] {
    msg := deny_hardcoded_jwt[_]
}

deny[msg] {
    msg := deny_sensitive_configmap[_]
}

# Main patch response
patches := array.concat([
    mutate_to_secrets_manager,
    mutate_add_secrets_annotation
], [])

response := {
    "apiVersion": "admission.k8s.io/v1",
    "kind": "AdmissionReview",
    "response": {
        "uid": input.request.uid,
        "allowed": count(deny) == 0,
        "status": {
            "message": concat(", ", [msg.reason | msg := deny[_]])
        },
        "patchType": "JSONPatch",
        "patch": base64.encode(json.marshal(patches))
    }
} {
    count(deny) == 0
    count(patches) > 0
}

response := {
    "apiVersion": "admission.k8s.io/v1",
    "kind": "AdmissionReview",
    "response": {
        "uid": input.request.uid,
        "allowed": false,
        "status": {
            "code": 403,
            "message": concat(", ", [msg.reason | msg := deny[_]])
        }
    }
} {
    count(deny) > 0
}

response := {
    "apiVersion": "admission.k8s.io/v1",
    "kind": "AdmissionReview",
    "response": {
        "uid": input.request.uid,
        "allowed": true
    }
} {
    count(deny) == 0
    count(patches) == 0
}
