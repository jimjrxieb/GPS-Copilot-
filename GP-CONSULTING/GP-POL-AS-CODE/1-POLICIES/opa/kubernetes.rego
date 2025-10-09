package kubernetes_security

violations[{"msg": msg, "file": input.file_path, "severity": "high"}] {
    input.file_type == "config"
    contains(input.file_content, "allowPrivilegeEscalation: true")
    msg := "Privilege escalation is allowed"
}

violations[{"msg": msg, "file": input.file_path, "severity": "medium"}] {
    input.file_type == "config"
    contains(input.file_content, "readOnlyRootFilesystem: false")
    msg := "Root filesystem is not read-only"
}
