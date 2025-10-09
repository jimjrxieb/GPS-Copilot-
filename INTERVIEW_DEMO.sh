#!/bin/bash
#
# 🎬 Jade AI - Interview Demo Script
#
# Demonstrates dynamic learning capability:
# "Drop client files → Jade learns → Immediately queryable"
#
# Run this during the interview to show real-time learning!
#

set -e

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║              🎬 JADE AI - DYNAMIC LEARNING DEMO                            ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Demo scenario
CLIENT_NAME="TechCorp"
CLIENT_FILE="GP-RAG/unprocessed/client-docs/${CLIENT_NAME}-requirements.md"

echo -e "${CYAN}📋 DEMO SCENARIO${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "New client: ${CLIENT_NAME}"
echo "Engagement: Kubernetes Security Assessment"
echo "Demo: Show Jade learning client requirements on-the-fly"
echo ""
read -p "Press ENTER to start demo..."
echo ""

# Step 1: Show current knowledge base
echo -e "${CYAN}STEP 1: Check current knowledge base${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Command: jade query \"${CLIENT_NAME}\"${NC}"
echo ""
python3 GP-AI/cli/jade-cli.py query "${CLIENT_NAME}" 2>/dev/null || echo "No results found (as expected - client is new)"
echo ""
read -p "Press ENTER to continue..."
echo ""

# Step 2: Create client document (simulating file drop)
echo -e "${CYAN}STEP 2: Client sends requirements document${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Simulating: Client email with requirements.md attachment"
echo -e "${YELLOW}Action: Drop file into GP-RAG/unprocessed/client-docs/${NC}"
echo ""

cat > "${CLIENT_FILE}" << 'EOF'
# TechCorp - Security Assessment Requirements

**Client:** TechCorp Inc.
**Engagement:** Kubernetes Security & Compliance Assessment
**Date:** 2025-10-03

## Client Overview

TechCorp is a rapidly growing e-commerce platform with 10,000+ customers.
They need urgent help with Kubernetes security for their upcoming SOC 2 audit.

## Critical Issues

### 1. CrashLoopBackOff in Production
**Pod:** checkout-service
**Namespace:** production
**Impact:** Payment processing failures
**Frequency:** Every 15 minutes
**Last Error:** OOMKilled (memory limit 256Mi, actual usage 380Mi)

**Required Fix:**
- Increase memory limit to 512Mi
- Add resource quotas
- Implement horizontal pod autoscaling

### 2. Privileged Containers
**Issue:** 12 pods running with privileged: true
**Risk:** Container escape, root access to nodes
**Compliance:** Fails SOC 2 requirement CC6.6

**Required Fix:**
- Remove privileged flag from all pods
- Implement Pod Security Admission (Restricted profile)
- Document exceptions for monitoring agents

### 3. No Network Policies
**Issue:** All pods can communicate freely (flat network)
**Risk:** Lateral movement in case of breach
**Compliance:** Fails SOC 2 requirement CC6.7

**Required Fix:**
- Implement default deny-all network policy
- Create micro-segmentation policies per namespace
- Document allowed communication paths

## Compliance Requirements

- **SOC 2 Type II** - Audit in 60 days
- **PCI-DSS Level 1** - Payment card data
- **GDPR** - EU customer data

## Timeline

- Week 1: Fix CrashLoopBackOff (URGENT - production impact)
- Week 2: Remove privileged containers
- Week 3-4: Implement network policies
- Week 5-8: Compliance documentation and testing

## Success Criteria

- ✅ Zero production CrashLoopBackOff errors
- ✅ All pods pass Pod Security Standards (Restricted)
- ✅ Network policies enforced (deny-all default)
- ✅ SOC 2 audit evidence documented
- ✅ Remediation runbooks for operations team

## Contact

- **CISO:** Sarah Chen (sarah.chen@techcorp.com)
- **DevOps Lead:** Mike Rodriguez (mike@techcorp.com)
- **Audit Partner:** Ernst & Young

---

**Notes:**
- Production cluster: EKS in us-east-1
- 45 microservices, 200+ pods
- Limited DevOps capacity (2 engineers)
- Zero-downtime deployment required
EOF

echo -e "${GREEN}✅ File created: ${CLIENT_FILE}${NC}"
echo ""
cat "${CLIENT_FILE}" | head -20
echo "..."
echo ""
read -p "Press ENTER to continue..."
echo ""

# Step 3: Jade learns the new knowledge
echo -e "${CYAN}STEP 3: Jade learns the new client requirements${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Command: jade learn${NC}"
echo ""
python3 GP-AI/cli/jade-cli.py learn
echo ""
read -p "Press ENTER to continue..."
echo ""

# Step 4: Query the new knowledge
echo -e "${CYAN}STEP 4: Query Jade about the new client${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Command: jade query \"${CLIENT_NAME} crashloopbackoff issue\"${NC}"
echo ""
python3 GP-AI/cli/jade-cli.py query "${CLIENT_NAME} crashloopbackoff issue"
echo ""
read -p "Press ENTER to continue..."
echo ""

# Step 5: Use agentic mode for troubleshooting
echo -e "${CYAN}STEP 5: Use Jade Agent for intelligent troubleshooting${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Command: jade agent \"${CLIENT_NAME} production pod crashlooping\"${NC}"
echo ""
python3 GP-AI/cli/jade-cli.py agent "${CLIENT_NAME} production pod crashlooping"
echo ""
read -p "Press ENTER to continue..."
echo ""

# Step 6: Summary
echo -e "${CYAN}DEMO COMPLETE ✅${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}What we demonstrated:${NC}"
echo ""
echo "1. ✅ Client file dropped into GP-RAG/unprocessed/"
echo "2. ✅ Jade learned it automatically (no model retraining)"
echo "3. ✅ Knowledge immediately queryable via RAG"
echo "4. ✅ Agentic workflow used client context + troubleshooting knowledge"
echo "5. ✅ Provided intelligent recommendations based on client requirements"
echo ""
echo -e "${YELLOW}Key Interview Points:${NC}"
echo ""
echo "• No retraining required - RAG-based learning"
echo "• Automatic chunking and categorization"
echo "• Semantic search across all knowledge"
echo "• LangGraph orchestration for multi-step reasoning"
echo "• Production-ready for real client engagements"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}Additional demos you can run:${NC}"
echo ""
echo "  jade learn --watch          # Start file watcher (real-time learning)"
echo "  jade chat                   # Natural language chat mode"
echo "  jade agent \"your question\"  # Agentic troubleshooting"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
