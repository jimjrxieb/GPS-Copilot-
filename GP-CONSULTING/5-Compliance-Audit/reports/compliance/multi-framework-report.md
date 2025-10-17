# Multi-Framework Security Compliance Report

**Generated**: 2025-10-10T12:55:04.052619

**Frameworks**: ISO 27001:2022, SOC2 Trust Service Criteria

**Scanners**: Bandit, Semgrep, Gitleaks, Trivy, Checkov

---

## Executive Summary

### Overview

- **Total Findings**: 146
- **Mapped to Compliance**: 31
- **Critical Issues**: 27
- **High Issues**: 8
- **Medium Issues**: 104
- **Low Issues**: 7

### Compliance Impact

- **ISO 27001 Controls Affected**: 9
- **SOC2 Criteria Affected**: 4
- **Cross-Framework Findings**: 31
- **High-Impact Findings**: 31

### Remediation Summary

- **Total Effort**: 170 hours (21.2 days)
- **High-Priority Items**: 21
- **Quick Wins Available**: 10

### Key Recommendations

#### 1. Address Cross-Framework Issues First

**Description**: Fix 31 issues that affect BOTH ISO 27001 and SOC2

**Impact**: Maximum compliance ROI

**Effort**: 170 hours

#### 2. Resolve Critical Security Issues

**Description**: Address 27 CRITICAL vulnerabilities

**Impact**: Prevent potential security breaches

**Effort**: 116 hours

#### 3. Implement Quick Wins

**Description**: Complete 10 high-ROI, low-effort fixes

**Impact**: Fast compliance improvements

**Effort**: 28 hours

---

## Cross-Framework Analysis

- **ISO 27001 Only**: 0 findings
- **SOC2 Only**: 0 findings
- **Both Frameworks**: 31 findings
- **Unmapped**: 115 findings

### High-Impact Findings (Top 10)

These findings affect BOTH ISO 27001 and SOC2 - fix once, satisfy multiple controls.

| Scanner | Issue | Severity | ISO Controls | SOC2 Criteria | Total |
|---------|-------|----------|--------------|---------------|-------|
| gitleaks | Generic API Key detected | CRITICAL | 2 | 3 | 5 |
| gitleaks | Generic API Key detected | CRITICAL | 2 | 3 | 5 |
| gitleaks | Generic API Key detected | CRITICAL | 2 | 3 | 5 |
| gitleaks | Generic API Key detected | CRITICAL | 2 | 3 | 5 |
| gitleaks | AWS detected | CRITICAL | 2 | 3 | 5 |
| bandit | subprocess call with shell=True identified, securi... | CRITICAL | 2 | 3 | 5 |
| bandit | subprocess call with shell=True identified, securi... | CRITICAL | 2 | 3 | 5 |
| bandit | subprocess call with shell=True identified, securi... | CRITICAL | 2 | 3 | 5 |
| bandit | subprocess call with shell=True identified, securi... | CRITICAL | 2 | 3 | 5 |
| bandit | A Flask app appears to be run with debug=True, whi... | HIGH | 2 | 3 | 5 |

---

## Prioritized Remediation Roadmap

Sorted by priority score (cross-framework impact + severity + controls affected).

### Top 20 Priority Items

| # | Issue | Severity | Frameworks | Controls | Effort | ROI |
|---|-------|----------|------------|----------|--------|-----|
| 1 | Generic API Key detected ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 4h | 25.0 |
| 2 | Generic API Key detected ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 4h | 25.0 |
| 3 | Generic API Key detected ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 4h | 25.0 |
| 4 | Generic API Key detected ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 4h | 25.0 |
| 5 | AWS detected ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 4h | 25.0 |
| 6 | subprocess call with shell=True identifi... ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 8h | 12.5 |
| 7 | subprocess call with shell=True identifi... ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 8h | 12.5 |
| 8 | subprocess call with shell=True identifi... ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 8h | 12.5 |
| 9 | subprocess call with shell=True identifi... ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 8h | 12.5 |
| 10 | subprocess call with shell=True identifi... ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 8h | 12.5 |
| 11 | subprocess call with shell=True identifi... ⭐ | CRITICAL | ISO_27001+SOC2 | 5 | 8h | 12.5 |
| 12 | Use of weak MD5 hash for security. Consi... ⭐ | CRITICAL | ISO_27001+SOC2 | 2 | 6h | 15.67 |
| 13 | Use of weak MD5 hash for security. Consi... ⭐ | CRITICAL | ISO_27001+SOC2 | 2 | 6h | 15.67 |
| 14 | Use of weak MD5 hash for security. Consi... ⭐ | CRITICAL | ISO_27001+SOC2 | 2 | 6h | 15.67 |
| 15 | Use of weak MD5 hash for security. Consi... ⭐ | CRITICAL | ISO_27001+SOC2 | 2 | 6h | 15.67 |
| 16 | Use of weak MD5 hash for security. Consi... ⭐ | CRITICAL | ISO_27001+SOC2 | 2 | 6h | 15.67 |
| 17 | Use of weak MD5 hash for security. Consi... ⭐ | CRITICAL | ISO_27001+SOC2 | 2 | 6h | 15.67 |
| 18 | Use of weak MD5 hash for security. Consi... ⭐ | CRITICAL | ISO_27001+SOC2 | 2 | 6h | 15.67 |
| 19 | Use of weak MD5 hash for security. Consi... ⭐ | CRITICAL | ISO_27001+SOC2 | 2 | 6h | 15.67 |
| 20 | A Flask app appears to be run with debug... ⭐ | HIGH | ISO_27001+SOC2 | 5 | 8h | 11.25 |

⭐ = Cross-framework impact (affects both ISO 27001 + SOC2)

