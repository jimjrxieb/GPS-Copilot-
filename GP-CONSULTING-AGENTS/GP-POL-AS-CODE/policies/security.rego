package security

violations[{"msg": msg, "file": input.file_path, "severity": "medium"}] {
    input.file_type == "config"
    contains(input.file_content, "privileged: true")
    msg := "Container runs in privileged mode"
}

violations[{"msg": msg, "file": input.file_path, "severity": "high"}] {
    input.file_type == "config"
    contains(input.file_content, "runAsUser: 0")
    msg := "Container runs as root user"
}

violations[{"msg": msg, "file": input.file_path, "severity": "medium"}] {
    input.file_type == "config"
    contains(input.file_content, "hostNetwork: true")
    msg := "Pod uses host network"
}

violations[{"msg": msg, "file": input.file_path, "severity": "low"}] {
    input.file_type == "config"
    not contains(input.file_content, "resources:")
    msg := "No resource limits defined"
}
