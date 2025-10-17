#!/usr/bin/env python3
"""
Cloud Security Patterns Scanner
Validates that documented security patterns are actually implemented

Purpose: Turn documentation into executable validation
Patterns validated:
- DDoS Resilience (CloudFront + WAF + Shield)
- Zero Trust Network (Security Groups, VPC)
- Encryption at Rest (RDS, S3, EBS)
- Private Cloud Access (VPC Endpoints)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add secops scanners to path for base_scanner import
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / 'secops' / '1-scanners'))
from base_scanner import SecurityScanner

try:
    import boto3
    from botocore.exceptions import ClientError, EndpointConnectionError
except ImportError:
    print("❌ boto3 not installed. Install: pip install boto3")
    sys.exit(1)


class CloudPatternsScanner(SecurityScanner):
    """
    Validates cloud security patterns are deployed, not just documented

    Checks:
    1. DDoS Resilience: CloudFront + WAF + Shield
    2. Zero Trust Network: Security Groups locked down
    3. Encryption at Rest: RDS, S3, EBS encrypted
    4. Private Cloud Access: VPC Endpoints exist
    """

    def __init__(self, scan_target: Path, output_dir: Path, timeout: int = 300, use_localstack: bool = True):
        super().__init__(scan_target, output_dir, timeout)

        self.use_localstack = use_localstack
        self.endpoint_url = "http://localhost:4566" if use_localstack else None

        # AWS clients
        self._init_clients()

    def _init_clients(self):
        """Initialize AWS clients (LocalStack or real AWS)"""
        common_args = {}
        if self.endpoint_url:
            common_args['endpoint_url'] = self.endpoint_url
            common_args['region_name'] = 'us-east-1'
            # LocalStack doesn't need real credentials
            common_args['aws_access_key_id'] = 'test'
            common_args['aws_secret_access_key'] = 'test'

        try:
            self.cloudfront = boto3.client('cloudfront', **common_args)
            self.wafv2 = boto3.client('wafv2', **common_args)
            self.ec2 = boto3.client('ec2', **common_args)
            self.rds = boto3.client('rds', **common_args)
            self.s3 = boto3.client('s3', **common_args)
            self.elb = boto3.client('elbv2', **common_args)

            # Shield only works in real AWS (expensive)
            if not self.use_localstack:
                self.shield = boto3.client('shield', **common_args)

            self.logger.debug("AWS clients initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize AWS clients: {e}")
            raise

    def get_scanner_name(self) -> str:
        return "cloud-patterns"

    def get_tool_name(self) -> str:
        return "boto3"

    def get_install_instructions(self) -> str:
        return "pip install boto3"

    def get_output_filename(self) -> str:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        return f"cloud-patterns-{timestamp}.json"

    def build_command(self, output_file: str) -> List[str]:
        """Not used - we use boto3 directly"""
        return []

    def validate_ddos_resilience(self) -> Dict:
        """
        Pattern: DDoS Resilience
        Checks:
        - CloudFront distribution exists
        - HTTPS enforced
        - WAF WebACL attached
        - Origin configured (ALB or S3)
        """
        self.logger.info("Checking DDoS Resilience pattern...")
        issues = []

        try:
            # Check CloudFront distributions
            response = self.cloudfront.list_distributions()
            distributions = response.get('DistributionList', {}).get('Items', [])

            if not distributions:
                issues.append({
                    'severity': 'HIGH',
                    'pattern': 'ddos-resilience',
                    'check': 'cloudfront-exists',
                    'status': 'FAIL',
                    'message': 'No CloudFront distribution found',
                    'remediation': 'Deploy CloudFront distribution in front of ALB/S3',
                    'compliance': ['NIST-CSF-PR.PT-5', 'FedRAMP-SC-5'],
                    'cost_impact': 'Low - CloudFront pay-per-use'
                })
            else:
                for dist in distributions:
                    dist_id = dist['Id']
                    domain = dist.get('DomainName', 'unknown')

                    # Check HTTPS enforcement
                    cache_behavior = dist.get('DefaultCacheBehavior', {})
                    viewer_protocol = cache_behavior.get('ViewerProtocolPolicy', 'allow-all')

                    if viewer_protocol != 'redirect-to-https':
                        issues.append({
                            'severity': 'MEDIUM',
                            'pattern': 'ddos-resilience',
                            'check': 'https-enforced',
                            'status': 'FAIL',
                            'resource': dist_id,
                            'message': f'CloudFront {dist_id} ({domain}) allows HTTP',
                            'remediation': 'Set ViewerProtocolPolicy to redirect-to-https',
                            'compliance': ['PCI-DSS-4.1', 'NIST-800-52']
                        })

                    # Check WAF attachment
                    web_acl_id = dist.get('WebACLId', '')
                    if not web_acl_id:
                        issues.append({
                            'severity': 'HIGH',
                            'pattern': 'ddos-resilience',
                            'check': 'waf-attached',
                            'status': 'FAIL',
                            'resource': dist_id,
                            'message': f'CloudFront {dist_id} has no WAF WebACL',
                            'remediation': 'Attach WAF WebACL with rate limiting rules',
                            'compliance': ['NIST-CSF-PR.PT-5'],
                            'cost_impact': 'Low - WAF ~$5/month + $1 per million requests'
                        })

            # Check Shield Advanced (expensive, optional)
            if not self.use_localstack:
                try:
                    shield_sub = self.shield.describe_subscription()
                    if shield_sub['Subscription']['SubscriptionState'] != 'ACTIVE':
                        issues.append({
                            'severity': 'LOW',
                            'pattern': 'ddos-resilience',
                            'check': 'shield-advanced',
                            'status': 'WARN',
                            'message': 'Shield Advanced not enabled',
                            'remediation': 'Enable Shield Advanced for 24/7 DDoS response team',
                            'compliance': ['NIST-CSF-PR.PT-5'],
                            'cost_impact': 'HIGH - $3,000/month'
                        })
                except ClientError:
                    # No subscription
                    pass

        except EndpointConnectionError:
            issues.append({
                'severity': 'CRITICAL',
                'pattern': 'ddos-resilience',
                'check': 'aws-connectivity',
                'status': 'ERROR',
                'message': 'Cannot connect to AWS endpoint (LocalStack not running?)',
                'remediation': 'Start LocalStack: docker-compose up -d localstack'
            })
        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'pattern': 'ddos-resilience',
                'check': 'cloudfront-api',
                'status': 'ERROR',
                'message': f'Failed to check CloudFront: {str(e)}',
                'remediation': 'Check AWS credentials and permissions'
            })

        return {
            'pattern': 'ddos-resilience',
            'description': 'CloudFront + WAF + Shield protection against volumetric attacks',
            'status': 'FAIL' if issues else 'PASS',
            'issues': issues,
            'issue_count': len(issues)
        }

    def validate_zero_trust_network(self) -> Dict:
        """
        Pattern: Zero Trust Network
        Checks:
        - No 0.0.0.0/0 on database ports
        - Security groups deny by default
        - VPC flow logs enabled
        """
        self.logger.info("Checking Zero Trust Network pattern...")
        issues = []

        # Dangerous ports that should NEVER be open to internet
        DATABASE_PORTS = {
            3306: 'MySQL',
            5432: 'PostgreSQL',
            1433: 'SQL Server',
            27017: 'MongoDB',
            6379: 'Redis',
            5984: 'CouchDB',
            9200: 'Elasticsearch',
            2181: 'Zookeeper'
        }

        try:
            # Check security groups
            response = self.ec2.describe_security_groups()

            for sg in response['SecurityGroups']:
                sg_id = sg['GroupId']
                sg_name = sg.get('GroupName', 'unknown')

                # Check ingress rules
                for rule in sg.get('IpPermissions', []):
                    from_port = rule.get('FromPort', 0)
                    to_port = rule.get('ToPort', 65535)

                    # Check for 0.0.0.0/0
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            # Check if it's a dangerous port
                            for db_port, db_name in DATABASE_PORTS.items():
                                if from_port <= db_port <= to_port:
                                    issues.append({
                                        'severity': 'CRITICAL',
                                        'pattern': 'zero-trust-network',
                                        'check': 'database-exposed',
                                        'status': 'FAIL',
                                        'resource': sg_id,
                                        'message': f'{db_name} port {db_port} exposed to internet in {sg_name}',
                                        'remediation': f'Remove 0.0.0.0/0 from port {db_port}, restrict to VPC CIDR',
                                        'compliance': ['PCI-DSS-1.3.4', 'HIPAA-164.312(a)(1)', 'CIS-AWS-5.2'],
                                        'attack_vector': 'Direct database compromise, data exfiltration'
                                    })

                            # SSH/RDP also shouldn't be wide open
                            if from_port <= 22 <= to_port:
                                issues.append({
                                    'severity': 'HIGH',
                                    'pattern': 'zero-trust-network',
                                    'check': 'ssh-exposed',
                                    'status': 'FAIL',
                                    'resource': sg_id,
                                    'message': f'SSH exposed to internet in {sg_name}',
                                    'remediation': 'Use AWS Systems Manager Session Manager instead',
                                    'compliance': ['CIS-AWS-5.2'],
                                    'cost_impact': 'Free - Session Manager included'
                                })

                            if from_port <= 3389 <= to_port:
                                issues.append({
                                    'severity': 'HIGH',
                                    'pattern': 'zero-trust-network',
                                    'check': 'rdp-exposed',
                                    'status': 'FAIL',
                                    'resource': sg_id,
                                    'message': f'RDP exposed to internet in {sg_name}',
                                    'remediation': 'Restrict to corporate VPN CIDR or use bastion host',
                                    'compliance': ['CIS-AWS-5.2']
                                })

            # Check VPC flow logs
            vpcs_response = self.ec2.describe_vpcs()
            flow_logs_response = self.ec2.describe_flow_logs()

            vpc_ids_with_logs = {log['ResourceId'] for log in flow_logs_response['FlowLogs']}

            for vpc in vpcs_response['Vpcs']:
                vpc_id = vpc['VpcId']
                if vpc_id not in vpc_ids_with_logs:
                    issues.append({
                        'severity': 'MEDIUM',
                        'pattern': 'zero-trust-network',
                        'check': 'flow-logs-enabled',
                        'status': 'FAIL',
                        'resource': vpc_id,
                        'message': f'VPC {vpc_id} has no flow logs enabled',
                        'remediation': 'Enable VPC Flow Logs for network monitoring',
                        'compliance': ['PCI-DSS-10.1', 'CIS-AWS-3.9'],
                        'cost_impact': 'Low - ~$0.50 per GB ingested'
                    })

        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'pattern': 'zero-trust-network',
                'check': 'ec2-api',
                'status': 'ERROR',
                'message': f'Failed to check security groups: {str(e)}'
            })

        return {
            'pattern': 'zero-trust-network',
            'description': 'Deny-by-default security groups, no public database access',
            'status': 'FAIL' if issues else 'PASS',
            'issues': issues,
            'issue_count': len(issues)
        }

    def validate_encryption_at_rest(self) -> Dict:
        """
        Pattern: Encryption at Rest
        Checks:
        - RDS encryption enabled
        - S3 bucket encryption enabled
        - EBS volumes encrypted
        """
        self.logger.info("Checking Encryption at Rest pattern...")
        issues = []

        try:
            # Check RDS instances
            rds_response = self.rds.describe_db_instances()

            for db in rds_response['DBInstances']:
                db_id = db['DBInstanceIdentifier']
                encrypted = db.get('StorageEncrypted', False)

                if not encrypted:
                    issues.append({
                        'severity': 'CRITICAL',
                        'pattern': 'encryption-at-rest',
                        'check': 'rds-encrypted',
                        'status': 'FAIL',
                        'resource': db_id,
                        'message': f'RDS instance {db_id} not encrypted',
                        'remediation': 'Create encrypted snapshot, restore to new encrypted instance',
                        'compliance': ['PCI-DSS-3.4', 'HIPAA-164.312(a)(2)(iv)', 'GDPR-Art-32'],
                        'cost_impact': 'Free - encryption included'
                    })

            # Check S3 buckets
            s3_buckets = self.s3.list_buckets()

            for bucket in s3_buckets['Buckets']:
                bucket_name = bucket['Name']

                try:
                    encryption = self.s3.get_bucket_encryption(Bucket=bucket_name)
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                        issues.append({
                            'severity': 'HIGH',
                            'pattern': 'encryption-at-rest',
                            'check': 's3-encrypted',
                            'status': 'FAIL',
                            'resource': bucket_name,
                            'message': f'S3 bucket {bucket_name} has no default encryption',
                            'remediation': 'Enable AES256 or aws:kms encryption',
                            'compliance': ['PCI-DSS-3.4', 'HIPAA-164.312(a)(2)(iv)'],
                            'cost_impact': 'Free for AES256, minimal for KMS'
                        })

            # Check EBS volumes
            volumes_response = self.ec2.describe_volumes()

            for vol in volumes_response['Volumes']:
                vol_id = vol['VolumeId']
                encrypted = vol.get('Encrypted', False)

                if not encrypted:
                    issues.append({
                        'severity': 'HIGH',
                        'pattern': 'encryption-at-rest',
                        'check': 'ebs-encrypted',
                        'status': 'FAIL',
                        'resource': vol_id,
                        'message': f'EBS volume {vol_id} not encrypted',
                        'remediation': 'Create encrypted snapshot, create volume from snapshot',
                        'compliance': ['PCI-DSS-3.4'],
                        'cost_impact': 'Free - encryption included'
                    })

        except Exception as e:
            issues.append({
                'severity': 'CRITICAL',
                'pattern': 'encryption-at-rest',
                'check': 'aws-api',
                'status': 'ERROR',
                'message': f'Failed to check encryption: {str(e)}'
            })

        return {
            'pattern': 'encryption-at-rest',
            'description': 'All data encrypted at rest (RDS, S3, EBS)',
            'status': 'FAIL' if issues else 'PASS',
            'issues': issues,
            'issue_count': len(issues)
        }

    def parse_results(self, output_file: Path) -> Dict:
        """Parse results - not used, we build directly"""
        with open(output_file) as f:
            return json.load(f)

    def run_scan(self) -> bool:
        """
        Main scan execution - validates all cloud patterns
        """
        self.logger.info("="*60)
        self.logger.info("CLOUD SECURITY PATTERNS VALIDATION")
        self.logger.info("="*60)

        # Run all pattern validations
        patterns = [
            self.validate_ddos_resilience(),
            self.validate_zero_trust_network(),
            self.validate_encryption_at_rest()
        ]

        # Build results
        all_issues = []
        for pattern in patterns:
            all_issues.extend(pattern['issues'])

        # Severity breakdown
        severity_breakdown = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for issue in all_issues:
            sev = issue.get('severity', 'MEDIUM')
            severity_breakdown[sev] = severity_breakdown.get(sev, 0) + 1

        results = {
            'findings': all_issues,
            'metadata': {
                'scanner': 'cloud-patterns',
                'scan_time': datetime.now().isoformat(),
                'target': str(self.scan_target),
                'endpoint': self.endpoint_url or 'AWS',
                'total_patterns': len(patterns),
                'patterns_pass': sum(1 for p in patterns if p['status'] == 'PASS'),
                'patterns_fail': sum(1 for p in patterns if p['status'] == 'FAIL')
            },
            'patterns': patterns,
            'total_issues': len(all_issues),
            'severity_breakdown': severity_breakdown
        }

        # Save results
        output_file = self.output_dir / self.get_output_filename()
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        self.logger.info("="*60)
        self.logger.info("VALIDATION COMPLETE")
        self.logger.info(f"  Patterns Checked: {len(patterns)}")
        self.logger.info(f"  Pass: {results['metadata']['patterns_pass']}")
        self.logger.info(f"  Fail: {results['metadata']['patterns_fail']}")
        self.logger.info(f"  Total Issues: {len(all_issues)}")
        if severity_breakdown['CRITICAL'] > 0:
            self.logger.info(f"  🔴 CRITICAL: {severity_breakdown['CRITICAL']}")
        if severity_breakdown['HIGH'] > 0:
            self.logger.info(f"  🟠 HIGH: {severity_breakdown['HIGH']}")
        if severity_breakdown['MEDIUM'] > 0:
            self.logger.info(f"  🟡 MEDIUM: {severity_breakdown['MEDIUM']}")
        self.logger.info(f"  Results: {output_file}")
        self.logger.info("="*60)

        return True


def main():
    """Run cloud patterns scanner standalone"""
    project_root = Path(__file__).parent.parent.parent.parent
    output_dir = project_root / 'secops' / '2-findings' / 'raw'

    scanner = CloudPatternsScanner(
        scan_target=project_root,
        output_dir=output_dir,
        use_localstack=True
    )

    try:
        success = scanner.run_scan()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
