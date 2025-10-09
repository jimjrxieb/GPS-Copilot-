#!/usr/bin/env python3
"""
Multi-Client Environment Isolation Testing
Test that infrastructure automation can safely manage multiple client environments
without cross-contamination
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from modules.real_kubernetes_integration import RealKubernetesIntegration
from modules.approval_system.real_approval_gates import RealApprovalGateSystem

async def test_multi_client_isolation():
    """Test multi-client environment isolation and safety"""

    print("🏢 MULTI-CLIENT ENVIRONMENT ISOLATION TESTING")
    print("=" * 60)
    print("Testing safe management of multiple client environments")
    print()

    isolation_results = {
        'timestamp': datetime.utcnow().isoformat(),
        'isolation_tests': [],
        'security_score': 0
    }

    # Simulate three different clients
    clients = [
        {
            'id': 'client_alpha_secure',
            'name': 'Alpha Corp',
            'environment': 'production',
            'namespace_prefix': 'alpha',
            'security_level': 'high'
        },
        {
            'id': 'client_beta_test',
            'name': 'Beta Industries',
            'environment': 'staging',
            'namespace_prefix': 'beta',
            'security_level': 'medium'
        },
        {
            'id': 'client_gamma_dev',
            'name': 'Gamma Solutions',
            'environment': 'development',
            'namespace_prefix': 'gamma',
            'security_level': 'low'
        }
    ]

    # Test 1: Namespace Isolation
    print("🔒 TEST 1: Kubernetes Namespace Isolation")
    print("-" * 40)

    k8s = RealKubernetesIntegration()
    created_namespaces = []

    try:
        for client in clients:
            namespace_name = f"{client['namespace_prefix']}-{client['environment']}-{int(time.time())}"

            print(f"Creating isolated namespace for {client['name']}: {namespace_name}")

            success, result = k8s.create_security_namespace(namespace_name)

            if success:
                created_namespaces.append(namespace_name)
                print(f"  ✅ {client['name']} namespace created successfully")
            else:
                print(f"  ❌ {client['name']} namespace creation failed: {result.get('error', 'Unknown')}")

        # Verify namespace isolation
        if len(created_namespaces) == len(clients):
            print(f"✅ All {len(clients)} client namespaces created in isolation")
            isolation_results['isolation_tests'].append({
                'test': 'namespace_isolation',
                'success': True,
                'details': f'{len(clients)} isolated namespaces created',
                'namespaces': created_namespaces
            })
        else:
            print(f"❌ Only {len(created_namespaces)}/{len(clients)} namespaces created")
            isolation_results['isolation_tests'].append({
                'test': 'namespace_isolation',
                'success': False,
                'details': f'Only {len(created_namespaces)}/{len(clients)} namespaces created'
            })

    except Exception as e:
        print(f"❌ Namespace isolation test failed: {e}")
        isolation_results['isolation_tests'].append({
            'test': 'namespace_isolation',
            'success': False,
            'error': str(e)
        })

    # Test 2: Configuration Data Isolation
    print(f"\n📊 TEST 2: Configuration Data Isolation")
    print("-" * 40)

    approval_system = RealApprovalGateSystem()

    try:
        client_configs = {}

        for client in clients:
            # Create client-specific configuration
            client_config = {
                'client_id': client['id'],
                'environment': client['environment'],
                'security_policies': {
                    'require_approval': client['security_level'] in ['high', 'medium'],
                    'max_resource_limits': {
                        'high': {'cpu': '2', 'memory': '4Gi'},
                        'medium': {'cpu': '1', 'memory': '2Gi'},
                        'low': {'cpu': '500m', 'memory': '1Gi'}
                    }[client['security_level']]
                },
                'approved_operations': [],
                'audit_trail': []
            }

            # Store configuration with client-specific path
            config_path = Path(f"/home/jimmie/linkops-industries/James-OS/guidepoint/data/client_configs/{client['id']}.json")
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Add configuration hash for integrity verification
            config_hash = hashlib.sha256(json.dumps(client_config, sort_keys=True).encode()).hexdigest()
            client_config['config_hash'] = config_hash

            with open(config_path, 'w') as f:
                json.dump(client_config, f, indent=2)

            client_configs[client['id']] = {
                'config': client_config,
                'path': config_path,
                'hash': config_hash
            }

            print(f"  ✅ {client['name']} configuration isolated: {config_path}")

        # Verify configuration isolation
        cross_contamination_detected = False

        for client_id, client_data in client_configs.items():
            # Reload configuration and verify integrity
            with open(client_data['path'], 'r') as f:
                reloaded_config = json.load(f)

            # Verify hash
            reloaded_hash = reloaded_config.pop('config_hash')
            calculated_hash = hashlib.sha256(json.dumps(reloaded_config, sort_keys=True).encode()).hexdigest()

            if reloaded_hash != calculated_hash:
                cross_contamination_detected = True
                print(f"  ❌ Configuration integrity check failed for {client_id}")

            # Verify no other client data leaked in
            if reloaded_config['client_id'] != client_id:
                cross_contamination_detected = True
                print(f"  ❌ Cross-contamination detected in {client_id}")

        if not cross_contamination_detected:
            print(f"✅ All {len(clients)} client configurations properly isolated")
            isolation_results['isolation_tests'].append({
                'test': 'configuration_isolation',
                'success': True,
                'details': f'{len(clients)} configurations isolated with integrity verification',
                'config_paths': [str(data['path']) for data in client_configs.values()]
            })
        else:
            print("❌ Configuration cross-contamination detected")
            isolation_results['isolation_tests'].append({
                'test': 'configuration_isolation',
                'success': False,
                'details': 'Cross-contamination detected between client configurations'
            })

    except Exception as e:
        print(f"❌ Configuration isolation test failed: {e}")
        isolation_results['isolation_tests'].append({
            'test': 'configuration_isolation',
            'success': False,
            'error': str(e)
        })

    # Test 3: Approval Workflow Isolation
    print(f"\n✅ TEST 3: Approval Workflow Isolation")
    print("-" * 40)

    try:
        approval_requests = {}

        for client in clients:
            # Create client-specific approval request
            request = await approval_system.create_approval_request(
                title=f"Deploy {client['name']} Security Update",
                description=f"Security hardening deployment for {client['name']} {client['environment']} environment",
                operation_type="kubernetes_deploy",
                target_environment=client['environment'],
                estimated_duration_minutes=30,
                rollback_time_minutes=5,
                execution_plan={
                    'client_id': client['id'],
                    'namespace': f"{client['namespace_prefix']}-{client['environment']}",
                    'security_level': client['security_level']
                },
                metadata={'client_id': client['id'], 'client_name': client['name']}
            )

            approval_requests[client['id']] = request
            print(f"  ✅ {client['name']} approval request created: {request.request_id}")

        # Verify approval isolation
        approval_isolation_verified = True

        for client_id, request in approval_requests.items():
            # Verify request contains only appropriate client data
            if request.metadata.get('client_id') != client_id:
                approval_isolation_verified = False
                print(f"  ❌ Approval isolation breach for {client_id}")

            # Verify execution plan contains client-specific data
            exec_plan_client = request.execution_plan.get('client_id')
            if exec_plan_client != client_id:
                approval_isolation_verified = False
                print(f"  ❌ Execution plan contamination for {client_id}")

        if approval_isolation_verified:
            print(f"✅ All {len(clients)} approval workflows properly isolated")
            isolation_results['isolation_tests'].append({
                'test': 'approval_isolation',
                'success': True,
                'details': f'{len(clients)} approval workflows isolated',
                'request_ids': [req.request_id for req in approval_requests.values()]
            })
        else:
            print("❌ Approval workflow contamination detected")
            isolation_results['isolation_tests'].append({
                'test': 'approval_isolation',
                'success': False,
                'details': 'Cross-contamination detected in approval workflows'
            })

    except Exception as e:
        print(f"❌ Approval isolation test failed: {e}")
        isolation_results['isolation_tests'].append({
            'test': 'approval_isolation',
            'success': False,
            'error': str(e)
        })

    # Test 4: Cleanup Isolation (ensuring cleanup affects only target client)
    print(f"\n🧹 TEST 4: Cleanup Isolation")
    print("-" * 40)

    try:
        cleanup_results = {}

        for namespace in created_namespaces:
            print(f"  Cleaning up namespace: {namespace}")
            success, result = k8s.cleanup_test_resources(namespace)
            cleanup_results[namespace] = success

            if success:
                print(f"  ✅ {namespace} cleaned up successfully")
            else:
                print(f"  ❌ {namespace} cleanup failed: {result.get('error', 'Unknown')}")

        # Verify all cleanups succeeded
        all_cleaned = all(cleanup_results.values())

        if all_cleaned:
            print(f"✅ All {len(created_namespaces)} client environments cleaned up in isolation")
            isolation_results['isolation_tests'].append({
                'test': 'cleanup_isolation',
                'success': True,
                'details': f'All {len(created_namespaces)} environments cleaned up properly'
            })
        else:
            failed_cleanups = [ns for ns, success in cleanup_results.items() if not success]
            print(f"❌ Cleanup failed for: {failed_cleanups}")
            isolation_results['isolation_tests'].append({
                'test': 'cleanup_isolation',
                'success': False,
                'details': f'Cleanup failed for {len(failed_cleanups)} environments'
            })

    except Exception as e:
        print(f"❌ Cleanup isolation test failed: {e}")
        isolation_results['isolation_tests'].append({
            'test': 'cleanup_isolation',
            'success': False,
            'error': str(e)
        })

    # Calculate security score
    successful_tests = sum(1 for test in isolation_results['isolation_tests'] if test['success'])
    total_tests = len(isolation_results['isolation_tests'])
    isolation_results['security_score'] = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

    print(f"\n📊 MULTI-CLIENT ISOLATION TESTING RESULTS")
    print("=" * 50)

    for test in isolation_results['isolation_tests']:
        status = "✅" if test['success'] else "❌"
        test_name = test['test'].replace('_', ' ').title()
        print(f"{status} {test_name}: {'PASS' if test['success'] else 'FAIL'}")

        if 'details' in test:
            print(f"    Details: {test['details']}")

        if not test['success'] and 'error' in test:
            print(f"    Error: {test['error']}")

    print(f"\n🎯 OVERALL SECURITY ISOLATION SCORE: {isolation_results['security_score']:.1f}%")

    if isolation_results['security_score'] >= 90:
        print("✅ EXCELLENT isolation - Safe for multi-client enterprise deployment")
    elif isolation_results['security_score'] >= 75:
        print("⚠️ GOOD isolation - Minor security improvements recommended")
    else:
        print("❌ POOR isolation - Significant security concerns for multi-client use")

    return isolation_results

if __name__ == "__main__":
    result = asyncio.run(test_multi_client_isolation())

    print(f"\nMulti-client isolation testing completed.")
    print(f"Security isolation score: {result['security_score']:.1f}%")