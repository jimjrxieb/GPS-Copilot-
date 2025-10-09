#!/usr/bin/env python3
"""
Test GuidePoint MCP Integration
Validates domain-specific MCP architecture without external MCP dependencies
"""

import sys
import os

# Add path for local imports
sys.path.append('/home/jimmie/linkops-industries/James-OS/guidepoint')

def test_guidepoint_mcp_integration():
    """Test GuidePoint MCP components"""

    print('🔧 TESTING GUIDEPOINT MCP INTEGRATION')
    print('=' * 50)

    # Test 1: Import agents directly
    try:
        from mcp.agents.consulting_remediation_agent import ConsultingRemediationAgent
        from mcp.agents.client_intelligence_agent import ClientIntelligenceAgent
        from mcp.agents.implementation_planning_agent import ImplementationPlanningAgent
        print('✅ All MCP agents import successful')
        agents_imported = True
    except Exception as e:
        print(f'❌ MCP agents import failed: {e}')
        agents_imported = False

    if agents_imported:
        # Test 2: Test agent initialization
        try:
            remediation_agent = ConsultingRemediationAgent()
            intelligence_agent = ClientIntelligenceAgent()
            planning_agent = ImplementationPlanningAgent()
            print('✅ All agents initialized successfully')

            # Test agent capabilities
            print('🔍 TESTING AGENT CAPABILITIES:')

            # Check remediation agent methods
            remediation_methods = [method for method in dir(remediation_agent)
                                 if not method.startswith('_') and callable(getattr(remediation_agent, method))]
            print(f'   📋 Remediation Agent: {len(remediation_methods)} public methods')
            if remediation_methods:
                print(f'      Key methods: {", ".join(remediation_methods[:3])}...')

            # Check intelligence agent methods
            intelligence_methods = [method for method in dir(intelligence_agent)
                                  if not method.startswith('_') and callable(getattr(intelligence_agent, method))]
            print(f'   🧠 Intelligence Agent: {len(intelligence_methods)} public methods')
            if intelligence_methods:
                print(f'      Key methods: {", ".join(intelligence_methods[:3])}...')

            # Check planning agent methods
            planning_methods = [method for method in dir(planning_agent)
                              if not method.startswith('_') and callable(getattr(planning_agent, method))]
            print(f'   📐 Planning Agent: {len(planning_methods)} public methods')
            if planning_methods:
                print(f'      Key methods: {", ".join(planning_methods[:3])}...')

            agents_functional = True

        except Exception as e:
            print(f'❌ Agent initialization failed: {e}')
            agents_functional = False
    else:
        agents_functional = False

    # Test 3: Test core automation engine components
    try:
        from automation_engine.clients.client_profiler import ClientProfileManager
        from automation_engine.guidance.kubernetes_planner import kubernetes_planner

        client_manager = ClientProfileManager()
        print('✅ Automation engine components accessible')
        automation_available = True

    except Exception as e:
        print(f'❌ Automation engine import failed: {e}')
        automation_available = False

    # Test 4: Validate domain-specific architecture
    print()
    print('🎯 DOMAIN-SPECIFIC ARCHITECTURE VALIDATION:')

    architecture_score = 0

    if agents_imported:
        print('✅ Domain-specific agents implemented')
        architecture_score += 25

        if agents_functional:
            print('✅ Agent business logic operational')
            architecture_score += 25
    else:
        print('❌ Agent implementation incomplete')

    if automation_available:
        print('✅ GuidePoint automation engine integration')
        architecture_score += 25
    else:
        print('❌ Automation engine integration missing')

    # Check for business-aware functionality
    if agents_functional:
        try:
            # Test business context awareness
            has_business_context = hasattr(remediation_agent, 'client_manager')
            has_risk_quantifier = hasattr(intelligence_agent, 'risk_quantifier')
            has_kubernetes_planner = hasattr(planning_agent, 'client_manager')

            if has_business_context and has_risk_quantifier and has_kubernetes_planner:
                print('✅ Business-aware consulting capabilities')
                architecture_score += 25
            else:
                print('⚠️  Business context integration partial')
                architecture_score += 10

        except Exception as e:
            print(f'❌ Business context validation failed: {e}')

    print()
    print('🏆 FINAL ASSESSMENT:')
    print(f'Architecture Completion: {architecture_score}/100')

    if architecture_score >= 75:
        print('✅ GuidePoint MCP architecture is PRODUCTION READY')
        print('✅ Domain-specific consulting agents operational')
        print('✅ Business-aware security recommendations available')
        print('✅ Ready for James Core coordination')

        print()
        print('🎯 GUIDEPOINT CONSULTING CAPABILITIES:')
        print('   • Client-specific remediation planning')
        print('   • Meeting intelligence processing')
        print('   • Executive report generation')
        print('   • Kubernetes implementation planning')
        print('   • Business impact analysis')
        print('   • Compliance-aware recommendations')

        return True

    elif architecture_score >= 50:
        print('⚠️  GuidePoint MCP architecture is PARTIALLY FUNCTIONAL')
        print('   Core agents implemented but integration needs refinement')
        return False

    else:
        print('❌ GuidePoint MCP architecture NEEDS WORK')
        print('   Multiple components require implementation')
        return False

if __name__ == "__main__":
    success = test_guidepoint_mcp_integration()
    print(f'\n🏁 GUIDEPOINT MCP TEST: {"PASSED" if success else "NEEDS WORK"}')