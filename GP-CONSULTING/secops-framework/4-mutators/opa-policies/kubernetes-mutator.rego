package kubernetes.mutate

import future.keywords.in

# Mutating policy for Kubernetes - Auto-injects security contexts

# Pod: Auto-inject security context
mutate_pod_security_context[patch] {
    input.request.kind.kind == "Pod"
    not input.request.object.spec.securityContext

    patch := {
        "op": "add",
        "path": "/spec/securityContext",
        "value": {
            "runAsNonRoot": true,
            "runAsUser": 1000,
            "fsGroup": 2000,
            "seccompProfile": {
                "type": "RuntimeDefault"
            }
        }
    }
}

# Container: Auto-inject security context
mutate_container_security_context[patch] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[i]
    not container.securityContext

    patch := {
        "op": "add",
        "path": sprintf("/spec/containers/%d/securityContext", [i]),
        "value": {
            "allowPrivilegeEscalation": false,
            "capabilities": {
                "drop": ["ALL"]
            },
            "readOnlyRootFilesystem": true,
            "runAsNonRoot": true,
            "runAsUser": 1000
        }
    }
}

# Deployment: Inject security context
mutate_deployment_security[patch] {
    input.request.kind.kind == "Deployment"
    not input.request.object.spec.template.spec.securityContext

    patch := {
        "op": "add",
        "path": "/spec/template/spec/securityContext",
        "value": {
            "runAsNonRoot": true,
            "runAsUser": 1000,
            "fsGroup": 2000,
            "seccompProfile": {
                "type": "RuntimeDefault"
            }
        }
    }
}

# Container: Drop all capabilities
mutate_drop_capabilities[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    container_path := get_container_path(input.request.kind.kind)
    container := object.get(input.request.object, container_path, [])[i]
    not has_dropped_capabilities(container)

    patch := {
        "op": "add",
        "path": sprintf("%s/%d/securityContext/capabilities", [container_path, i]),
        "value": {
            "drop": ["ALL"]
        }
    }
}

has_dropped_capabilities(container) {
    caps := container.securityContext.capabilities.drop
    "ALL" in caps
}

get_container_path("Pod") = "/spec/containers"
get_container_path("Deployment") = "/spec/template/spec/containers"

# Disable privileged containers
mutate_disable_privileged[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    container_path := get_container_path(input.request.kind.kind)
    container := object.get(input.request.object, container_path, [])[i]
    container.securityContext.privileged == true

    patch := {
        "op": "replace",
        "path": sprintf("%s/%d/securityContext/privileged", [container_path, i]),
        "value": false
    }
}

# Disable hostNetwork
mutate_disable_host_network[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    spec := get_spec(input.request.kind.kind, input.request.object)
    spec.hostNetwork == true

    patch := {
        "op": "replace",
        "path": get_host_network_path(input.request.kind.kind),
        "value": false
    }
}

get_spec("Pod", obj) = obj.spec
get_spec("Deployment", obj) = obj.spec.template.spec

get_host_network_path("Pod") = "/spec/hostNetwork"
get_host_network_path("Deployment") = "/spec/template/spec/hostNetwork"

# Disable hostPID
mutate_disable_host_pid[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    spec := get_spec(input.request.kind.kind, input.request.object)
    spec.hostPID == true

    patch := {
        "op": "replace",
        "path": get_host_pid_path(input.request.kind.kind),
        "value": false
    }
}

get_host_pid_path("Pod") = "/spec/hostPID"
get_host_pid_path("Deployment") = "/spec/template/spec/hostPID"

# Add resource limits
mutate_add_resource_limits[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    container_path := get_container_path(input.request.kind.kind)
    container := object.get(input.request.object, container_path, [])[i]
    not container.resources.limits

    patch := {
        "op": "add",
        "path": sprintf("%s/%d/resources/limits", [container_path, i]),
        "value": {
            "cpu": "500m",
            "memory": "512Mi"
        }
    }
}

# Add resource requests
mutate_add_resource_requests[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    container_path := get_container_path(input.request.kind.kind)
    container := object.get(input.request.object, container_path, [])[i]
    not container.resources.requests

    patch := {
        "op": "add",
        "path": sprintf("%s/%d/resources/requests", [container_path, i]),
        "value": {
            "cpu": "250m",
            "memory": "256Mi"
        }
    }
}

# Block latest tag
mutate_block_latest_tag[patch] {
    input.request.kind.kind in ["Pod", "Deployment"]
    container_path := get_container_path(input.request.kind.kind)
    container := object.get(input.request.object, container_path, [])[i]
    endswith(container.image, ":latest")

    patch := {
        "op": "replace",
        "path": sprintf("%s/%d/image", [container_path, i]),
        "value": sprintf("%s:v1.0.0", [trim_suffix(container.image, ":latest")])
    }
}

# Main mutation response (Kubernetes Admission Controller format)
patch_response := {
    "apiVersion": "admission.k8s.io/v1",
    "kind": "AdmissionReview",
    "response": {
        "uid": input.request.uid,
        "allowed": true,
        "patchType": "JSONPatch",
        "patch": base64.encode(json.marshal(patches))
    }
} {
    count(patches) > 0
}

# Aggregate all patches
patches := array.concat([
    mutate_pod_security_context,
    mutate_container_security_context,
    mutate_deployment_security,
    mutate_drop_capabilities,
    mutate_disable_privileged,
    mutate_disable_host_network,
    mutate_disable_host_pid,
    mutate_add_resource_limits,
    mutate_add_resource_requests,
    mutate_block_latest_tag
], [])

# If no mutations needed, allow without patch
patch_response := {
    "apiVersion": "admission.k8s.io/v1",
    "kind": "AdmissionReview",
    "response": {
        "uid": input.request.uid,
        "allowed": true
    }
} {
    count(patches) == 0
}
