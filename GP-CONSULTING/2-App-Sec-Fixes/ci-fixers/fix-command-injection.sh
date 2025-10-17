#!/bin/bash

# ============================================================================
# CI FIXER: Command Injection Prevention
# ============================================================================
# LAYER: CI (Code-level)
# WHEN: Pre-commit, CI pipeline
# FIXES:
#   - HIGH: subprocess calls with shell=True (Bandit B602)
#   - HIGH: os.system() usage (Bandit B605)
#   - HIGH: shell injection (Bandit B607)
#   - CRITICAL: Command injection vulnerabilities
#   - PCI-DSS 6.5.1: Injection flaws
#   - OWASP A03:2021 - Injection
#   - CWE-78: OS Command Injection
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

echo "🔧 CI FIXER: Command Injection Prevention"
echo "═══════════════════════════════════════════════════════"
echo "Layer: CI (Code-level)"
echo "When: Pre-commit hook, CI pipeline"
echo ""

# Auto-detect project root or use provided argument
if [ -n "$1" ]; then
    PROJECT_ROOT="$1"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
fi

BACKUP_DIR="$PROJECT_ROOT/backup/command-injection-$TIMESTAMP"
REPORT_DIR="$PROJECT_ROOT/GP-DATA/active/2-app-sec-fixes/ci-fixes"
REPORT_FILE="$REPORT_DIR/fix-command-injection-$TIMESTAMP.log"

# Create directories
mkdir -p "$REPORT_DIR"
mkdir -p "$BACKUP_DIR"

# Start logging
exec > >(tee -a "$REPORT_FILE") 2>&1

echo "Project: $PROJECT_ROOT"
echo "Report: $REPORT_FILE"
echo "Timestamp: $(date -Iseconds)"
echo ""

# Validation
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ ERROR: Project directory not found: $PROJECT_ROOT"
    exit 1
fi

echo "→ Creating backup..."
cp -r "$PROJECT_ROOT" "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Scanning for command injection vulnerabilities..."

FINDINGS=0
FIXES_APPLIED=0
MANUAL_REVIEW=0

# Python files
if find "$PROJECT_ROOT" -name "*.py" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing Python files..."

    # os.system() usage (Bandit B605)
    if grep -r "os\.system\(" "$PROJECT_ROOT" --include="*.py" | grep -q .; then
        echo "    ⚠️  Found os.system() usage (command injection risk)"
        ((FINDINGS++))

        # os.system() is always dangerous - flag for manual review
        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -q "os\.system\(" "$file"; then
                echo "      ⚠️  Manual review required: $file"
                echo "         Replace os.system() with subprocess.run() using array syntax"
                ((MANUAL_REVIEW++))
            fi
        done
    fi

    # subprocess with shell=True (Bandit B602)
    if grep -rE "subprocess\.(run|call|Popen|check_output).*shell=True" "$PROJECT_ROOT" --include="*.py" | grep -q .; then
        echo "    ⚠️  Found subprocess with shell=True (command injection risk)"
        ((FINDINGS++))

        # Auto-fix simple cases
        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -qE "subprocess\.(run|call|Popen|check_output).*shell=True" "$file"; then
                # Check if it's a simple case (no pipe, redirect, or shell features)
                if ! grep -E "subprocess.*shell=True" "$file" | grep -qE '(\||>|<|&&|\$\(|\`)'; then
                    echo "      Fixing: $file (removing shell=True)"

                    # Remove shell=True parameter
                    sed -i 's/, shell=True//g' "$file"
                    sed -i 's/shell=True, //g' "$file"
                    sed -i 's/shell=True//g' "$file"

                    # Add comment
                    if ! grep -q "# Security: Removed shell=True to prevent command injection" "$file"; then
                        sed -i '1i # Security: Removed shell=True to prevent command injection' "$file"
                    fi

                    ((FIXES_APPLIED++))
                else
                    echo "      ⚠️  Manual review required: $file (complex shell usage)"
                    ((MANUAL_REVIEW++))
                fi
            fi
        done
    fi

    # eval() usage
    if grep -r "eval\(" "$PROJECT_ROOT" --include="*.py" | grep -v "# nosec" | grep -q .; then
        echo "    ⚠️  Found eval() usage (code injection risk)"
        ((FINDINGS++))

        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -q "eval\(" "$file"; then
                echo "      ⚠️  Manual review required: $file"
                echo "         Replace eval() with ast.literal_eval() or json.loads()"
                ((MANUAL_REVIEW++))
            fi
        done
    fi

    # exec() usage
    if grep -r "exec\(" "$PROJECT_ROOT" --include="*.py" | grep -v "# nosec" | grep -q .; then
        echo "    ⚠️  Found exec() usage (code injection risk)"
        ((FINDINGS++))

        find "$PROJECT_ROOT" -name "*.py" -type f | while read -r file; do
            if grep -q "exec\(" "$file"; then
                echo "      ⚠️  Manual review required: $file"
                echo "         Avoid exec() or use safe alternatives"
                ((MANUAL_REVIEW++))
            fi
        done
    fi
fi

# JavaScript/Node.js files
if find "$PROJECT_ROOT" -name "*.js" -type f | grep -q .; then
    echo ""
    echo "  📝 Analyzing JavaScript files..."

    # child_process.exec() usage
    if grep -rE "require\(['\"]child_process['\"]\)|child_process\.exec\(" "$PROJECT_ROOT" --include="*.js" | grep -q .; then
        echo "    ⚠️  Found child_process.exec() usage (command injection risk)"
        ((FINDINGS++))

        find "$PROJECT_ROOT" -name "*.js" -type f | while read -r file; do
            if grep -q "child_process\.exec\(" "$file"; then
                echo "      ⚠️  Manual review required: $file"
                echo "         Replace exec() with execFile() or spawn()"
                ((MANUAL_REVIEW++))
            fi
        done
    fi

    # eval() usage
    if grep -r "eval\(" "$PROJECT_ROOT" --include="*.js" | grep -q .; then
        echo "    ⚠️  Found eval() usage (code injection risk)"
        ((FINDINGS++))

        find "$PROJECT_ROOT" -name "*.js" -type f | while read -r file; do
            if grep -q "eval\(" "$file"; then
                echo "      ⚠️  Manual review required: $file"
                echo "         Avoid eval() or use JSON.parse() for JSON data"
                ((MANUAL_REVIEW++))
            fi
        done
    fi
fi

if [ $FINDINGS -eq 0 ]; then
    echo "  ✅ No command injection vulnerabilities found"
    exit 0
fi

# Create secure command execution helper for Python projects
if find "$PROJECT_ROOT" -name "*.py" -type f | grep -q .; then
    UTILS_DIR="$PROJECT_ROOT/utils"
    mkdir -p "$UTILS_DIR"

    cat > "$UTILS_DIR/secure_subprocess.py" << 'EOF'
#!/usr/bin/env python3
"""
Secure Subprocess Execution Helper
Prevents command injection vulnerabilities
"""

import subprocess
import shlex
from typing import List, Optional, Union


def run_command(
    command: Union[str, List[str]],
    cwd: Optional[str] = None,
    timeout: Optional[int] = 30,
    capture_output: bool = True
) -> subprocess.CompletedProcess:
    """
    Execute a command safely without shell injection risks

    Args:
        command: Command as list (recommended) or string (will be split safely)
        cwd: Working directory (optional)
        timeout: Command timeout in seconds (default: 30)
        capture_output: Capture stdout/stderr (default: True)

    Returns:
        CompletedProcess: Command result

    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout
        subprocess.CalledProcessError: If command fails

    Example:
        # List format (safest)
        result = run_command(['ls', '-la', '/tmp'])

        # String format (will be split safely)
        result = run_command('ls -la /tmp')

        # With user input (SAFE - no shell injection)
        filename = user_input  # Even if malicious like "; rm -rf /"
        result = run_command(['cat', filename])  # Safe!
    """
    # Convert string to list if needed
    if isinstance(command, str):
        command = shlex.split(command)

    # Execute without shell=True (prevents injection)
    return subprocess.run(
        command,
        cwd=cwd,
        timeout=timeout,
        capture_output=capture_output,
        check=True,
        shell=False  # NEVER use shell=True!
    )


def run_command_with_input(
    command: Union[str, List[str]],
    stdin_data: str,
    timeout: Optional[int] = 30
) -> subprocess.CompletedProcess:
    """
    Execute command with stdin input (safe)

    Args:
        command: Command as list or string
        stdin_data: Data to send to command's stdin
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess: Command result

    Example:
        # Echo data to command
        result = run_command_with_input(['grep', 'error'], stdin_data=log_contents)
    """
    if isinstance(command, str):
        command = shlex.split(command)

    return subprocess.run(
        command,
        input=stdin_data,
        text=True,
        timeout=timeout,
        capture_output=True,
        check=True,
        shell=False
    )


def validate_filename(filename: str) -> bool:
    """
    Validate filename for safe filesystem operations

    Args:
        filename: Filename to validate

    Returns:
        bool: True if filename is safe

    Example:
        if validate_filename(user_filename):
            run_command(['cat', user_filename])
        else:
            raise ValueError("Invalid filename")
    """
    # Reject path traversal attempts
    if '..' in filename or filename.startswith('/'):
        return False

    # Reject shell metacharacters
    dangerous_chars = ['|', '&', ';', '$', '`', '\n', '*', '?', '<', '>', '(', ')']
    if any(char in filename for char in dangerous_chars):
        return False

    return True


# Example: Safe alternative to os.system()
def safe_system(command: List[str]) -> int:
    """
    Safe alternative to os.system()

    Args:
        command: Command as list (NOT string!)

    Returns:
        int: Exit code (0 = success)

    Example:
        # Instead of: os.system(f"cat {filename}")  # DANGEROUS!
        # Use: safe_system(['cat', filename])  # SAFE!
        exit_code = safe_system(['cat', '/tmp/file.txt'])
    """
    try:
        result = subprocess.run(command, shell=False, check=False)
        return result.returncode
    except Exception as e:
        print(f"Command failed: {e}")
        return 1
EOF

    echo "  ✅ Created: $UTILS_DIR/secure_subprocess.py (safe command execution)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CI FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Changes made:"
echo "  ✅ Removed shell=True from simple subprocess calls"
echo "  ✅ Created utils/secure_subprocess.py (safe execution helper)"
echo "  ⚠️  Flagged $MANUAL_REVIEW files for manual review"
echo ""
echo "Command injection prevention:"
echo "  • NEVER use shell=True"
echo "  • NEVER use os.system()"
echo "  • ALWAYS use command arrays: ['ls', '-la', filename]"
echo "  • User input CANNOT inject commands when using arrays"
echo ""
echo "Usage of secure helper:"
echo "  from utils.secure_subprocess import run_command"
echo "  "
echo "  # Safe - even with malicious input"
echo "  user_file = request.GET['file']  # Could be \"; rm -rf /\""
echo "  result = run_command(['cat', user_file])  # SAFE!"
echo "  "
echo "  # The command executes exactly: cat \"; rm -rf /\""
echo "  # No shell interpretation - just tries to read that filename"
echo ""
echo "Manual review needed for:"
if [ $MANUAL_REVIEW -gt 0 ]; then
    echo "  1. os.system() usage → replace with run_command()"
    echo "  2. shell=True with pipes/redirects → use subprocess.PIPE"
    echo "  3. eval()/exec() usage → use ast.literal_eval() or remove"
    echo "  4. child_process.exec() → replace with execFile() or spawn()"
fi
echo ""
echo "Next steps:"
echo "  1. Review all flagged files"
echo "  2. Replace command strings with arrays:"
echo "     BAD:  subprocess.run(f\"cat {file}\", shell=True)"
echo "     GOOD: subprocess.run(['cat', file], shell=False)"
echo "  3. For JavaScript, use execFile():"
echo "     const { execFile } = require('child_process');"
echo "     execFile('ls', ['-la'], callback);"
echo "  4. Re-run Bandit scanner:"
echo "     python3 ../../1-Security-Assessment/ci-scanners/bandit_scanner.py --target $PROJECT_ROOT"
echo ""
echo "Backup saved: $BACKUP_DIR"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-command-injection.sh"
echo "Layer: CI (Code-level)"
echo "Findings: $FINDINGS"
echo "Fixes Applied: $FIXES_APPLIED"
echo "Manual Review Needed: $MANUAL_REVIEW"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Report: $REPORT_FILE"
echo ""
