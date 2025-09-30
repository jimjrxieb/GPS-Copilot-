# Developer Policy for HashiCorp Vault
# Provides read access to development secrets and limited write access to user-specific paths

# Development environment secrets (read-only)
path "secret/data/dev/*" {
  capabilities = ["read"]
}

# User-specific development secrets (read/write)
path "secret/data/users/{{identity.entity.name}}/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Shared development tools and configurations (read-only)
path "secret/data/shared/dev/*" {
  capabilities = ["read"]
}

# Database dynamic secrets for development
path "database/creds/dev-readonly" {
  capabilities = ["read"]
}

# PKI certificate requests for development
path "pki/issue/dev-role" {
  capabilities = ["create", "update"]
}

# Transit encryption for development data
path "transit/encrypt/dev-key" {
  capabilities = ["update"]
}

path "transit/decrypt/dev-key" {
  capabilities = ["update"]
}

# List capabilities for UI navigation
path "secret/metadata/dev/*" {
  capabilities = ["list"]
}

path "secret/metadata/users/{{identity.entity.name}}/*" {
  capabilities = ["list"]
}

path "secret/metadata/shared/dev/*" {
  capabilities = ["list"]
}

# Allow developers to manage their own tokens
path "auth/token/create" {
  capabilities = ["create", "update"]
}

path "auth/token/renew-self" {
  capabilities = ["update"]
}

path "auth/token/revoke-self" {
  capabilities = ["update"]
}

# Allow developers to read their own token information
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Deny access to production secrets
path "secret/data/prod/*" {
  capabilities = ["deny"]
}

path "secret/data/production/*" {
  capabilities = ["deny"]
}

# Deny access to admin functions
path "sys/*" {
  capabilities = ["deny"]
}

path "auth/*/config" {
  capabilities = ["deny"]
}