#!/usr/bin/env python3
"""
Remediation Database - Direct, Practical Security Fixes
Maps scanner findings to actionable remediation steps
"""

class RemediationDB:
    """Simple, working remediation database for security findings"""

    def __init__(self):
        # Bandit Python Security Fixes
        self.bandit_fixes = {
            "B101": {
                "issue": "Use of assert detected",
                "risk": "Assert statements are removed in optimized code, breaking validation",
                "severity": "low",
                "fix": """
Replace assert with proper exception handling:

# Bad:
assert user_input, "Invalid input"

# Good:
if not user_input:
    raise ValueError("Invalid input")
""",
                "references": ["https://bandit.readthedocs.io/en/latest/plugins/b101_assert_used.html"]
            },

            "B113": {
                "issue": "Request without timeout",
                "risk": "Can cause denial of service through hanging requests",
                "severity": "medium",
                "fix": """
Add timeout parameter to all requests:

# Bad:
response = requests.get(url)

# Good:
response = requests.get(url, timeout=30)

# Better (with retry logic):
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
response = session.get(url, timeout=30)
""",
                "references": ["https://bandit.readthedocs.io/en/latest/plugins/b113_request_without_timeout.html"]
            },

            "B105": {
                "issue": "Hardcoded password",
                "risk": "Credentials exposed in source code",
                "severity": "high",
                "fix": """
Use environment variables or secrets management:

# Bad:
password = "admin123"

# Good:
import os
password = os.environ.get('DB_PASSWORD')

# Better (with fallback):
from dotenv import load_dotenv
load_dotenv()
password = os.environ.get('DB_PASSWORD')
if not password:
    raise ValueError("DB_PASSWORD not set")
""",
                "references": ["https://12factor.net/config"]
            },

            "B108": {
                "issue": "Insecure temporary file",
                "risk": "Race conditions and unauthorized access",
                "severity": "medium",
                "fix": """
Use secure temporary file creation:

# Bad:
tmp = '/tmp/myfile.txt'
with open(tmp, 'w') as f:
    f.write(data)

# Good:
import tempfile
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write(data)
    tmp = f.name
""",
                "references": ["https://docs.python.org/3/library/tempfile.html"]
            }
        }

        # Semgrep Common Fixes
        self.semgrep_fixes = {
            "python.sqlalchemy.security.sqlalchemy-execute-raw-query": {
                "issue": "Raw SQL query execution",
                "risk": "SQL injection vulnerability",
                "severity": "high",
                "fix": """
Use parameterized queries:

# Bad:
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)

# Good:
query = "SELECT * FROM users WHERE id = :user_id"
db.execute(query, {"user_id": user_id})

# Better (using ORM):
User.query.filter_by(id=user_id).first()
""",
                "references": ["https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"]
            },

            "python.django.security.audit.xss.direct-use-of-httpresponse": {
                "issue": "Direct HttpResponse with user input",
                "risk": "Cross-site scripting (XSS)",
                "severity": "high",
                "fix": """
Use Django templates with auto-escaping:

# Bad:
return HttpResponse(f"<h1>Welcome {username}</h1>")

# Good:
from django.shortcuts import render
return render(request, 'welcome.html', {'username': username})

# Or escape manually:
from django.utils.html import escape
return HttpResponse(f"<h1>Welcome {escape(username)}</h1>")
""",
                "references": ["https://docs.djangoproject.com/en/stable/topics/security/#cross-site-scripting-xss-protection"]
            }
        }

        # Trivy/Container Security Fixes
        self.trivy_fixes = {
            "CVE-2021-44228": {  # Log4Shell
                "issue": "Log4j Remote Code Execution",
                "risk": "Complete system compromise",
                "severity": "critical",
                "fix": """
Update Log4j immediately:

# Check version:
mvn dependency:tree | grep log4j

# Update pom.xml:
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.17.1</version> <!-- Fixed version -->
</dependency>

# Or disable JNDI:
-Dlog4j2.formatMsgNoLookups=true
""",
                "references": ["https://www.cisa.gov/uscert/apache-log4j-vulnerability-guidance"]
            },

            "DKL-DI-0005": {
                "issue": "Container running as root",
                "risk": "Container escape and privilege escalation",
                "severity": "high",
                "fix": """
Run containers as non-root user:

# Dockerfile:
FROM alpine:latest

# Create non-root user
RUN addgroup -g 1000 appuser && \\
    adduser -D -u 1000 -G appuser appuser

# Switch to non-root user
USER appuser

# Or in docker-compose.yml:
services:
  app:
    image: myapp
    user: "1000:1000"
""",
                "references": ["https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user"]
            }
        }

        # GitLeaks Secret Fixes
        self.gitleaks_fixes = {
            "aws-access-token": {
                "issue": "AWS credentials in code",
                "risk": "Unauthorized AWS access",
                "severity": "critical",
                "fix": """
Remove from code and rotate immediately:

1. Remove from repository:
   git filter-branch --force --index-filter \\
     'git rm --cached --ignore-unmatch path/to/file' \\
     --prune-empty --tag-name-filter cat -- --all

2. Rotate credentials in AWS:
   - Go to AWS IAM Console
   - Deactivate compromised key
   - Generate new access key

3. Use AWS Secrets Manager or environment variables:
   # Use boto3 with IAM role (best):
   import boto3
   client = boto3.client('s3')  # Uses IAM role

   # Or environment variables:
   export AWS_ACCESS_KEY_ID=xxx
   export AWS_SECRET_ACCESS_KEY=xxx
""",
                "references": ["https://aws.amazon.com/premiumsupport/knowledge-center/rotate-access-keys/"]
            },

            "generic-api-key": {
                "issue": "API key in source code",
                "risk": "API abuse and data breach",
                "severity": "high",
                "fix": """
Use environment variables and .env files:

1. Create .env file (and add to .gitignore):
   API_KEY=your_actual_key_here

2. Load in Python:
   from dotenv import load_dotenv
   import os

   load_dotenv()
   api_key = os.getenv('API_KEY')

3. Add .env to .gitignore:
   echo ".env" >> .gitignore

4. Document in README:
   ## Setup
   1. Copy .env.example to .env
   2. Add your API keys
""",
                "references": ["https://12factor.net/config"]
            }
        }

        # Checkov Terraform Fixes
        self.checkov_fixes = {
            "CKV_AWS_20": {
                "issue": "S3 bucket not encrypted",
                "risk": "Data exposure if bucket is compromised",
                "severity": "high",
                "fix": """
Enable S3 bucket encryption:

resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
""",
                "references": ["https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration"]
            },

            "CKV_AWS_79": {
                "issue": "Instance Metadata Service v1 enabled",
                "risk": "SSRF attacks can steal IAM credentials",
                "severity": "high",
                "fix": """
Require IMDSv2:

resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # This enforces IMDSv2
    http_put_response_hop_limit = 1
  }
}
""",
                "references": ["https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html"]
            }
        }

    def get_fix(self, scanner: str, issue_id: str) -> dict:
        """Get remediation for a specific scanner finding"""
        scanner_map = {
            "bandit": self.bandit_fixes,
            "semgrep": self.semgrep_fixes,
            "trivy": self.trivy_fixes,
            "gitleaks": self.gitleaks_fixes,
            "checkov": self.checkov_fixes
        }

        fixes = scanner_map.get(scanner.lower(), {})
        return fixes.get(issue_id, {
            "issue": f"Unknown issue: {issue_id}",
            "risk": "Unknown",
            "severity": "unknown",
            "fix": f"No specific remediation found for {scanner} issue {issue_id}. Please consult {scanner} documentation.",
            "references": []
        })

    def get_all_fixes_for_scanner(self, scanner: str) -> dict:
        """Get all fixes for a specific scanner"""
        scanner_map = {
            "bandit": self.bandit_fixes,
            "semgrep": self.semgrep_fixes,
            "trivy": self.trivy_fixes,
            "gitleaks": self.gitleaks_fixes,
            "checkov": self.checkov_fixes
        }
        return scanner_map.get(scanner.lower(), {})