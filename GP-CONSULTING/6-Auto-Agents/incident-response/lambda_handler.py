#!/usr/bin/env python3
"""
AWS Lambda Handler for GuardDuty Incident Response
====================================================
Purpose: CloudWatch Events trigger for automated incident response
Integration: CloudWatch Events → Lambda → GuardDuty Responder

Deployment:
    1. Package: zip lambda_deployment.zip lambda_handler.py guardduty_responder.py
    2. Upload to Lambda
    3. Set timeout: 5 minutes
    4. Set memory: 512 MB
    5. Attach IAM role (see iam_policy.json)

Environment Variables:
    DRY_RUN: "true" or "false" (default: false)
    REGION: AWS region (default: from event)
    SNS_TOPIC_ARN: SNS topic for notifications (optional)

Author: GP-Copilot / Jade AI
Date: October 13, 2025
"""

import json
import logging
import os
from guardduty_responder import GuardDutyResponder

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Process GuardDuty finding from CloudWatch Event

    Event structure:
    {
      "version": "0",
      "id": "event-id",
      "detail-type": "GuardDuty Finding",
      "source": "aws.guardduty",
      "account": "123456789012",
      "time": "2025-10-13T14:35:00Z",
      "region": "us-east-1",
      "resources": [],
      "detail": {
        <GuardDuty Finding JSON>
      }
    }
    """

    logger.info("=== GuardDuty Incident Response Lambda ===")
    logger.info(f"Event: {json.dumps(event, default=str)}")

    try:
        # Extract finding from event
        if 'detail' not in event:
            raise ValueError("No 'detail' in event - not a GuardDuty finding")

        finding = event['detail']
        region = event.get('region', os.environ.get('AWS_REGION', 'us-east-1'))

        # Check for dry-run mode
        dry_run = os.environ.get('DRY_RUN', 'false').lower() == 'true'

        logger.info(f"Processing finding: {finding.get('id')}")
        logger.info(f"Finding type: {finding.get('type')}")
        logger.info(f"Severity: {finding.get('severity')}")
        logger.info(f"Region: {region}")
        logger.info(f"Dry run: {dry_run}")

        # Initialize responder
        responder = GuardDutyResponder(region=region, dry_run=dry_run)

        # Process finding
        result = responder.process_finding(finding)

        # Log result
        logger.info(f"Response result: {json.dumps(result, default=str)}")

        # Send SNS notification if configured
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        if sns_topic_arn and not dry_run:
            send_sns_notification(sns_topic_arn, finding, result, region)

        return {
            'statusCode': 200 if result['success'] else 500,
            'body': json.dumps({
                'message': 'GuardDuty incident response executed',
                'finding_id': result.get('finding_id'),
                'severity_level': result.get('severity_level'),
                'actions_taken': len(result.get('actions', [])),
                'success': result['success']
            })
        }

    except Exception as e:
        logger.error(f"Error processing GuardDuty finding: {e}", exc_info=True)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing GuardDuty finding',
                'error': str(e)
            })
        }


def send_sns_notification(sns_topic_arn, finding, result, region):
    """Send SNS notification about incident response"""
    import boto3

    try:
        sns = boto3.client('sns', region_name=region)

        subject = f"🚨 GuardDuty Incident Response: {result['severity_level']}"

        message = f"""
GuardDuty Incident Response Executed
=====================================

Finding ID: {finding.get('id')}
Type: {finding.get('type')}
Severity: {finding.get('severity')} ({result['severity_level']})
Resource: {finding.get('resource', {}).get('resourceType')}

Actions Taken:
{json.dumps(result.get('actions', []), indent=2)}

Success: {result['success']}
Timestamp: {result['timestamp']}

---
Automated response by GuardDuty Incident Response Agent
"""

        sns.publish(
            TopicArn=sns_topic_arn,
            Subject=subject,
            Message=message
        )

        logger.info(f"SNS notification sent to {sns_topic_arn}")

    except Exception as e:
        logger.error(f"Failed to send SNS notification: {e}")


# For local testing
if __name__ == '__main__':
    # Load test event
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            test_event = json.load(f)
    else:
        # Default test event
        with open('test-finding.json', 'r') as f:
            finding = json.load(f)

        test_event = {
            "version": "0",
            "id": "test-event-001",
            "detail-type": "GuardDuty Finding",
            "source": "aws.guardduty",
            "account": "123456789012",
            "time": "2025-10-13T14:35:00Z",
            "region": "us-east-1",
            "resources": [],
            "detail": finding
        }

    # Set dry-run for local testing
    os.environ['DRY_RUN'] = 'true'

    # Mock context
    class Context:
        function_name = 'guardduty-incident-response'
        function_version = '$LATEST'
        invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:guardduty-incident-response'
        memory_limit_in_mb = 512
        aws_request_id = 'test-request-id'
        log_group_name = '/aws/lambda/guardduty-incident-response'
        log_stream_name = 'test-stream'

    context = Context()

    # Invoke handler
    result = lambda_handler(test_event, context)

    print(json.dumps(result, indent=2))
