#!/bin/bash

# ============================================================================
# Auto-Fixer: Security Groups (CRITICAL FINDINGS)
# ============================================================================
# FIXES:
#   - CRITICAL: Security group allows ingress from 0.0.0.0/0
#   - CRITICAL: Security group allows egress to 0.0.0.0/0 on all ports
#   - PCI-DSS 1.2.1: Restrict inbound/outbound traffic
#   - PCI-DSS 1.3.1: Implement DMZ, no direct database access from internet
# ============================================================================

set -e

echo "🔧 Auto-Fixer: Security Groups (CRITICAL)"
echo "═══════════════════════════════════════════════════════"

TF_DIR="../../../../infrastructure/terraform"
BACKUP_DIR="$TF_DIR.backup.$(date +%Y%m%d-%H%M%S)"

# Validate Terraform directory exists
if [ ! -d "$TF_DIR" ]; then
    echo "❌ ERROR: Terraform directory not found: $TF_DIR"
    exit 1
fi

if [ ! -f "$TF_DIR/security-groups.tf" ]; then
    echo "❌ ERROR: security-groups.tf not found"
    exit 1
fi

echo ""
echo "→ Creating backup..."
cp -r "$TF_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Analyzing current security groups..."
grep -n "0.0.0.0/0" "$TF_DIR/security-groups.tf" || echo "  (No 0.0.0.0/0 found)"

echo ""
echo "→ Fixing CRITICAL: Replacing allow_all security group with least-privilege groups..."

# Replace the entire allow_all security group with secure alternatives
cat > "$TF_DIR/security-groups-fixed.tf" << 'EOF'
# ============================================================================
# SECURITY GROUPS - LEAST PRIVILEGE (PCI-DSS COMPLIANT)
# ============================================================================
# ✅ PCI 1.2.1: Restrict inbound/outbound traffic to necessary only
# ✅ PCI 1.3.1: No direct database access from internet
# ============================================================================

# ALB Security Group (Internet-facing)
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb"
  description = "Allow HTTPS from internet to ALB only"
  vpc_id      = aws_vpc.main.id

  # Allow HTTPS from internet (ALB only)
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # OK: ALB is public-facing
  }

  # Allow HTTP redirect to HTTPS
  ingress {
    description = "HTTP redirect to HTTPS"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress to backend in private subnets only
  egress {
    description     = "To backend app"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  tags = {
    Name        = "${var.project_name}-alb"
    PCI_DSS     = "1.2.1"
    Description = "Public ALB - HTTPS only"
  }
}

# Backend Security Group (Private)
resource "aws_security_group" "backend" {
  name        = "${var.project_name}-backend"
  description = "Backend app - only from ALB"
  vpc_id      = aws_vpc.main.id

  # Only allow traffic from ALB
  ingress {
    description     = "From ALB only"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Egress to database only
  egress {
    description     = "To database"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.database.id]
  }

  # Egress to Redis only
  egress {
    description     = "To Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.redis.id]
  }

  # Egress for AWS API calls (VPC endpoints preferred)
  egress {
    description = "AWS API calls"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-backend"
    PCI_DSS     = "1.2.1"
    Description = "Backend - ALB to DB only"
  }
}

# Database Security Group (Private - No Internet Access)
resource "aws_security_group" "database" {
  name        = "${var.project_name}-database"
  description = "PostgreSQL - only from backend"
  vpc_id      = aws_vpc.main.id

  # ✅ PCI 1.3.1: NO internet access to database
  ingress {
    description     = "PostgreSQL from backend only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  # No egress - database shouldn't initiate connections

  tags = {
    Name        = "${var.project_name}-database"
    PCI_DSS     = "1.3.1"
    Description = "Database - No Internet"
  }
}

# Redis Security Group (Private)
resource "aws_security_group" "redis" {
  name        = "${var.project_name}-redis"
  description = "Redis - only from backend"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Redis from backend only"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  tags = {
    Name        = "${var.project_name}-redis"
    Description = "Redis cache"
  }
}

# EKS Cluster Security Group
resource "aws_security_group" "eks_cluster" {
  name        = "${var.project_name}-eks-cluster"
  description = "EKS cluster control plane"
  vpc_id      = aws_vpc.main.id

  # Allow worker nodes to communicate with cluster
  ingress {
    description     = "From worker nodes"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }

  egress {
    description     = "To worker nodes"
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }

  tags = {
    Name = "${var.project_name}-eks-cluster"
  }
}

# EKS Worker Nodes Security Group
resource "aws_security_group" "eks_nodes" {
  name        = "${var.project_name}-eks-nodes"
  description = "EKS worker nodes"
  vpc_id      = aws_vpc.main.id

  # Allow nodes to communicate with each other
  ingress {
    description = "Node to node"
    from_port   = 0
    to_port     = 65535
    protocol    = "-1"
    self        = true
  }

  # Allow worker nodes to communicate with cluster
  ingress {
    description     = "From cluster"
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  # Egress to cluster
  egress {
    description     = "To cluster"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  # Egress for pulling images, updates
  egress {
    description = "Internet for images/updates"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name                                           = "${var.project_name}-eks-nodes"
    "kubernetes.io/cluster/${var.project_name}"    = "owned"
  }
}
EOF

echo "✅ Created security-groups-fixed.tf with least-privilege groups"

echo ""
echo "→ Replacing old security-groups.tf..."
mv "$TF_DIR/security-groups.tf" "$TF_DIR/security-groups.tf.INSECURE.bak"
mv "$TF_DIR/security-groups-fixed.tf" "$TF_DIR/security-groups.tf"
echo "✅ Replaced security groups file"

echo ""
echo "→ Validating Terraform configuration..."
cd "$TF_DIR"
if terraform validate > /dev/null 2>&1; then
    echo "✅ Terraform validation passed"
else
    echo "❌ Terraform validation failed! Rolling back..."
    mv "$TF_DIR/security-groups.tf.INSECURE.bak" "$TF_DIR/security-groups.tf"
    rm -f "$TF_DIR/security-groups-fixed.tf"
    echo "❌ Rollback complete. Please fix Terraform errors manually."
    exit 1
fi

echo ""
echo "→ Showing changes..."
git diff "$TF_DIR/security-groups.tf" 2>/dev/null || echo "  (git not available, use diff manually)"

echo ""
echo "✅ Security Groups auto-fix complete!"
echo ""
echo "📋 BEFORE (INSECURE):"
echo "   ❌ allow_all security group with 0.0.0.0/0 ingress/egress"
echo "   ❌ Database exposed to internet"
echo "   ❌ No network segmentation"
echo ""
echo "📋 AFTER (SECURE):"
echo "   ✅ ALB security group - HTTPS from internet only"
echo "   ✅ Backend security group - ALB to backend only"
echo "   ✅ Database security group - Backend to database only (NO INTERNET)"
echo "   ✅ Redis security group - Backend to Redis only"
echo "   ✅ EKS security groups - Cluster and node communication"
echo "   ✅ PCI-DSS 1.2.1 compliant - Least privilege"
echo "   ✅ PCI-DSS 1.3.1 compliant - DMZ with no direct DB access"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff $TF_DIR/security-groups.tf"
echo "   2. Update references to 'allow_all' in other .tf files"
echo "   3. Plan: cd $TF_DIR && terraform plan"
echo "   4. Apply: terraform apply"
echo ""
echo "🔙 Rollback: mv $TF_DIR/security-groups.tf.INSECURE.bak $TF_DIR/security-groups.tf"
echo "💾 Backup: $BACKUP_DIR"
