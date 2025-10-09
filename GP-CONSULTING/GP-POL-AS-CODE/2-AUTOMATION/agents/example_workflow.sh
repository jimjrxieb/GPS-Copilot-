#!/bin/bash
# Example Workflow: How to Use the Automation Agents
# This demonstrates the complete three-step groove

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

AGENTS_DIR="/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents"

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  GP-Copilot Three-Step Security Groove - Example Workflow${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if repo path provided
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage: $0 <path_to_terraform_or_k8s_repo>${NC}"
    echo ""
    echo "Example:"
    echo "  $0 ~/projects/my-terraform-infra"
    echo "  $0 ~/projects/my-k8s-manifests"
    echo ""
    exit 1
fi

REPO_PATH="$1"

if [ ! -d "$REPO_PATH" ]; then
    echo -e "${RED}Error: Directory not found: $REPO_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}📁 Target Repository: $REPO_PATH${NC}"
echo ""

# Detect repo type
if ls "$REPO_PATH"/*.tf &> /dev/null; then
    REPO_TYPE="terraform"
    echo -e "${BLUE}Detected: Terraform repository${NC}"
elif ls "$REPO_PATH"/*.yaml &> /dev/null || ls "$REPO_PATH"/*.yml &> /dev/null; then
    REPO_TYPE="kubernetes"
    echo -e "${BLUE}Detected: Kubernetes manifests${NC}"
else
    echo -e "${YELLOW}Warning: Could not detect repository type, assuming Terraform${NC}"
    REPO_TYPE="terraform"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  STEP 1: CI Shift-Left Validation (Conftest Gate)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$REPO_TYPE" = "terraform" ]; then
    echo -e "${GREEN}Running Terraform plan validation...${NC}"
    echo "Command: python $AGENTS_DIR/conftest_gate_agent.py $REPO_PATH"
    echo ""

    # Run conftest gate (will fail if violations found)
    if python "$AGENTS_DIR/conftest_gate_agent.py" "$REPO_PATH" 2>&1; then
        echo ""
        echo -e "${GREEN}✅ PASSED: No Terraform violations found!${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠️  VIOLATIONS FOUND: Terraform plan has policy violations${NC}"
        echo -e "${YELLOW}Jade AI will analyze these and create approval proposals${NC}"
    fi
else
    echo -e "${YELLOW}Skipping Conftest gate (not a Terraform repo)${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  STEP 2: Daily Kubernetes Audit (Gatekeeper)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$REPO_TYPE" = "kubernetes" ]; then
    echo -e "${GREEN}Running Gatekeeper daily audit...${NC}"
    echo "Command: python $AGENTS_DIR/gatekeeper_audit_agent.py"
    echo ""

    AUDIT_FILE="/tmp/gatekeeper_audit_$(date +%Y%m%d_%H%M%S).json"

    if python "$AGENTS_DIR/gatekeeper_audit_agent.py" > "$AUDIT_FILE" 2>&1; then
        echo ""
        echo -e "${GREEN}✅ PASSED: No Kubernetes violations found!${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠️  VIOLATIONS FOUND: Kubernetes cluster has policy violations${NC}"
        echo -e "Audit report saved: $AUDIT_FILE"

        echo ""
        echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
        echo -e "${BLUE}  STEP 2b: Create PR with Fixes (PR Bot)${NC}"
        echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
        echo ""

        echo -e "${GREEN}Creating PR with automated fixes...${NC}"
        echo "Command: python $AGENTS_DIR/pr_bot_agent.py $REPO_PATH $AUDIT_FILE"
        echo ""

        if python "$AGENTS_DIR/pr_bot_agent.py" "$REPO_PATH" "$AUDIT_FILE" 2>&1; then
            echo ""
            echo -e "${GREEN}✅ PR created successfully!${NC}"
            echo -e "Review the PR in your git hosting platform"
        else
            echo ""
            echo -e "${YELLOW}⚠️  PR creation skipped (no gh CLI or no fixes generated)${NC}"
        fi
    fi
else
    echo -e "${YELLOW}Note: Gatekeeper audit requires a running Kubernetes cluster${NC}"
    echo -e "To test: Deploy Gatekeeper to your cluster first"
    echo -e "  kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.15/deploy/gatekeeper.yaml"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  STEP 3: Staged Rollout (dryrun → warn → deny)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}Example: Deploy policy with progressive enforcement${NC}"
echo ""

# Find a constraint file
CONSTRAINT_FILE=$(find /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/GP-POL-AS-CODE/1-POLICIES/gatekeeper/constraints -name "*.yaml" | head -1)

if [ -n "$CONSTRAINT_FILE" ]; then
    echo -e "Using constraint: $(basename $CONSTRAINT_FILE)"
    echo ""

    echo -e "${YELLOW}Stage 1: dryrun (audit only, no blocking)${NC}"
    echo "Command: python $AGENTS_DIR/patch_rollout_agent.py deploy $CONSTRAINT_FILE staging dryrun"
    echo -e "${BLUE}In production, this would run for 7 days to collect violation data${NC}"
    echo ""

    echo -e "${YELLOW}Stage 2: warn (log violations, alert teams)${NC}"
    echo "Command: python $AGENTS_DIR/patch_rollout_agent.py deploy $CONSTRAINT_FILE staging warn"
    echo -e "${BLUE}In production, this would run for 7 days to prepare teams${NC}"
    echo ""

    echo -e "${YELLOW}Stage 3: deny (full enforcement)${NC}"
    echo "Command: python $AGENTS_DIR/patch_rollout_agent.py deploy $CONSTRAINT_FILE production deny"
    echo -e "${BLUE}This blocks violations in production${NC}"
    echo ""

    echo -e "${GREEN}To run progressive rollout automatically:${NC}"
    echo "python $AGENTS_DIR/patch_rollout_agent.py progressive $CONSTRAINT_FILE staging"
else
    echo -e "${YELLOW}No constraint files found. Create one first:${NC}"
    echo "  1. Use opa_policy_generator.py to generate from violations"
    echo "  2. Or manually create in 1-POLICIES/gatekeeper/constraints/"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  WHERE TO SEE RESULTS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}1. Local Git Changes:${NC}"
echo "   cd $REPO_PATH"
echo "   git status                # See modified files"
echo "   git diff                  # See what changed"
echo "   git log -1                # See Jade's commit"
echo ""

echo -e "${GREEN}2. Approval Queue (Electron GUI):${NC}"
echo "   cd /home/jimmie/linkops-industries/GP-copilot/GP-GUI"
echo "   npm start                 # Open Jade GUI"
echo "   # Navigate to Approval Queue tab"
echo ""

echo -e "${GREEN}3. Activity Tracker (RAG):${NC}"
echo "   jade query 'What did we do today?'"
echo "   jade query 'Show me all CRITICAL proposals'"
echo "   jade query 'What violations did you find in $REPO_PATH?'"
echo ""

echo -e "${GREEN}4. API (Programmatic):${NC}"
echo "   # Start FastAPI server"
echo "   cd /home/jimmie/linkops-industries/GP-copilot/GP-AI"
echo "   uvicorn api.main:app --reload"
echo ""
echo "   # Query approvals"
echo "   curl http://localhost:8000/api/v1/approvals/pending"
echo "   curl http://localhost:8000/api/v1/approvals/1001"
echo ""

echo -e "${GREEN}5. Audit Reports:${NC}"
echo "   ls -lh /home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/audit/"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  JADE AI DECISION FLOW${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Jade analyzes violations and decides:${NC}"
echo ""
echo "  CRITICAL violations → Create approval proposal (24h expiry)"
echo "  HIGH + production   → Create approval proposal (7d expiry)"
echo "  HIGH + non-prod     → Auto-fix + create PR"
echo "  MEDIUM/LOW          → Auto-fix via Gatekeeper mutation"
echo ""
echo "Jade tracks everything in RAG for 'What did we do today?' queries"
echo ""

echo -e "${GREEN}✅ Example workflow complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review the generated audit reports"
echo "2. Open Jade GUI to see approval proposals"
echo "3. Approve/reject proposals in the Approval Queue"
echo "4. Query Jade: 'What did we do today?'"
echo ""
echo -e "${YELLOW}For detailed integration guide:${NC}"
echo "cat $AGENTS_DIR/JADE_INTEGRATION_GUIDE.md"
echo ""