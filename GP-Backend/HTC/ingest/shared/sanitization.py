#!/usr/bin/env python3
"""
Sanitization Utilities
======================

Remove or mask sensitive data before ingestion.
"""

import re
from typing import Dict, Any, Tuple, List


class Sanitizer:
    """Sanitize sensitive data from text"""

    # Regex patterns for sensitive data
    PATTERNS = {
        # API Keys
        "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "generic_api_key": re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?"),

        # Passwords
        "password": re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^\s'\"]{6,})['\"]?"),

        # Tokens
        "jwt": re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"),
        "bearer": re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]+"),

        # Personal Data
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "phone": re.compile(r"\b\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"),

        # Internal Data
        "private_ip": re.compile(r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
        "internal_url": re.compile(r"https?://(?:localhost|127\.0\.0\.1|internal\.[a-z0-9.-]+)"),
    }

    # Replacement rules by category
    RULES = {
        "intake": {
            "email": "keep",       # Business context needs emails
            "phone": "mask",       # Mask phone numbers
            "ssn": "remove",       # Always remove SSNs
            "credit_card": "remove"  # Always remove credit cards
        },
        "technical": {
            "aws_key": "mask",
            "generic_api_key": "mask",
            "password": "mask",
            "jwt": "mask",
            "bearer": "mask"
        },
        "projects": {
            "aws_key": "flag",     # Flag for security findings
            "generic_api_key": "flag",
            "password": "flag",
            "private_ip": "mask",
            "internal_url": "mask"
        },
        "sessions": {
            "aws_key": "mask",
            "generic_api_key": "mask",
            "password": "mask"
        }
    }

    def __init__(self, category: str):
        self.category = category
        self.rules = self.RULES.get(category, {})
        self.sanitization_count = 0

    def sanitize(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Sanitize text according to category rules.

        Returns:
            (sanitized_text, findings)
            where findings is a list of detected sensitive data
        """
        findings = []
        sanitized_text = text

        for pattern_name, pattern in self.PATTERNS.items():
            # Get rule for this pattern
            rule = self.rules.get(pattern_name, "keep")

            # Find all matches
            matches = pattern.finditer(sanitized_text)

            for match in matches:
                matched_text = match.group(0)

                if rule == "keep":
                    # Keep as-is
                    continue

                elif rule == "mask":
                    # Mask the sensitive part
                    if pattern_name in ["aws_key", "generic_api_key"]:
                        replacement = "[API_KEY_MASKED]"
                    elif pattern_name == "password":
                        replacement = "[REDACTED]"
                    elif pattern_name in ["jwt", "bearer"]:
                        replacement = "[TOKEN_MASKED]"
                    elif pattern_name == "phone":
                        replacement = "[PHONE_MASKED]"
                    elif pattern_name == "private_ip":
                        replacement = "[IP_MASKED]"
                    elif pattern_name == "internal_url":
                        replacement = "[INTERNAL_URL]"
                    else:
                        replacement = "[MASKED]"

                    sanitized_text = sanitized_text.replace(matched_text, replacement)
                    self.sanitization_count += 1

                    findings.append({
                        "type": pattern_name,
                        "action": "masked",
                        "original": matched_text[:20] + "..." if len(matched_text) > 20 else matched_text
                    })

                elif rule == "remove":
                    # Remove entirely
                    sanitized_text = sanitized_text.replace(matched_text, "")
                    self.sanitization_count += 1

                    findings.append({
                        "type": pattern_name,
                        "action": "removed"
                    })

                elif rule == "flag":
                    # Flag but keep (for security findings)
                    findings.append({
                        "type": pattern_name,
                        "action": "flagged",
                        "original": matched_text[:20] + "..." if len(matched_text) > 20 else matched_text,
                        "severity": "HIGH"
                    })

        return sanitized_text, findings

    def get_count(self) -> int:
        """Get number of sanitizations performed"""
        return self.sanitization_count


# Quick test
if __name__ == "__main__":
    # Test technical sanitization
    sanitizer = Sanitizer("technical")

    test_text = """
    Here's how to configure AWS:
    export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

    And the database password is: password=supersecret123

    JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U
    """

    sanitized, findings = sanitizer.sanitize(test_text)

    print("Original:")
    print(test_text)
    print("\nSanitized:")
    print(sanitized)
    print(f"\nFindings: {len(findings)}")
    for finding in findings:
        print(f"  - {finding}")
