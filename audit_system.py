#!/usr/bin/env python3
"""
Comprehensive System Audit for VyralFlow AI
Checks all APIs, endpoints, agents, and services for potential bugs
"""
import sys
import os
import asyncio
import requests
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def audit_file_structure():
    """Audit project file organization"""
    print("🔍 AUDITING FILE STRUCTURE")
    print("=" * 50)
    
    required_dirs = [
        "app/",
        "app/agents/", 
        "app/services/",
        "app/models/",
        "app/core/",
        "scripts/",
        "tests/",
        "docs/"
    ]
    
    issues = []
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ Missing: {dir_path}")
            issues.append(f"Missing directory: {dir_path}")
    
    # Check for loose files in root
    root_files = [f for f in os.listdir('.') if f.endswith('.py') and not f.startswith('vyralflow_') and f != 'audit_system.py']
    if root_files:
        print(f"⚠️  Loose Python files in root: {root_files}")
        issues.append(f"Loose files need organization: {root_files}")
    else:
        print("✅ No loose Python files in root")
    
    return issues

def audit_imports():
    """Check for import errors in main modules"""
    print("\n🔍 AUDITING IMPORTS")
    print("=" * 50)
    
    import_tests = [
        ("from app.services.enhanced_services import unsplash_service", "Enhanced services"),
        ("from app.agents.trend_analyzer import TrendAnalyzerAgent", "Trend Analyzer"),
        ("from app.agents.content_writer import ContentWriterAgent", "Content Writer"),
        ("from app.agents.visual_designer import VisualDesignerAgent", "Visual Designer"),
        ("from app.agents.campaign_scheduler import CampaignSchedulerAgent", "Campaign Scheduler"),
        ("from app.core.config import settings", "Config"),
        ("from app.models.campaign import CampaignRequest", "Campaign Model"),
    ]
    
    issues = []
    for import_stmt, name in import_tests:
        try:
            exec(import_stmt)
            print(f"✅ {name} import: OK")
        except Exception as e:
            print(f"❌ {name} import error: {e}")
            issues.append(f"{name} import error: {e}")
    
    return issues

def audit_api_endpoints():
    """Test API endpoints for bugs"""
    print("\n🔍 AUDITING API ENDPOINTS")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return [f"Server not running: {e}"]
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/api/health", "Health check"),
        ("GET", "/docs", "API documentation"),
        ("GET", "/api/agents/status", "Agents status"),
    ]
    
    issues = []
    for method, endpoint, description in endpoints:
        try:
            url = f"http://localhost:8080{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description} ({endpoint}): OK")
            else:
                print(f"⚠️  {description} ({endpoint}): Status {response.status_code}")
                issues.append(f"{description} returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description} ({endpoint}): {e}")
            issues.append(f"{description} error: {e}")
    
    return issues

def audit_campaign_workflow():
    """Test complete campaign creation workflow"""
    print("\n🔍 AUDITING CAMPAIGN WORKFLOW")
    print("=" * 50)
    
    issues = []
    
    try:
        # Test campaign creation
        campaign_data = {
            "business_name": "AuditTest Corp",
            "industry": "Technology",
            "campaign_goal": "System audit test",
            "target_platforms": ["instagram", "twitter"],
            "brand_voice": "professional"
        }
        
        response = requests.post(
            "http://localhost:8080/api/campaigns/create",
            json=campaign_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            campaign_id = data.get("campaign_id")
            print(f"✅ Campaign creation: OK (ID: {campaign_id})")
            
            # Test status endpoint
            status_response = requests.get(f"http://localhost:8080/api/campaigns/{campaign_id}/status", timeout=10)
            if status_response.status_code == 200:
                print("✅ Status endpoint: OK")
            else:
                print(f"❌ Status endpoint: Status {status_response.status_code}")
                issues.append(f"Status endpoint error: {status_response.status_code}")
            
            # Wait a bit for processing
            import time
            time.sleep(10)
            
            # Test results endpoint  
            results_response = requests.get(f"http://localhost:8080/api/campaigns/{campaign_id}/results", timeout=10)
            if results_response.status_code == 200:
                print("✅ Results endpoint: OK")
                
                # Validate results structure
                results_data = results_response.json()
                required_sections = ["content", "visuals", "trends", "schedule"]
                for section in required_sections:
                    if section in results_data:
                        print(f"✅ Results contain {section}: OK")
                    else:
                        print(f"⚠️  Results missing {section}")
                        issues.append(f"Results missing {section} section")
                        
            else:
                print(f"❌ Results endpoint: Status {results_response.status_code}")
                issues.append(f"Results endpoint error: {results_response.status_code}")
                
        else:
            print(f"❌ Campaign creation failed: Status {response.status_code}")
            issues.append(f"Campaign creation failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Campaign workflow error: {e}")
        issues.append(f"Campaign workflow error: {e}")
    
    return issues

def audit_agent_implementations():
    """Check agent implementations for common bugs"""
    print("\n🔍 AUDITING AGENT IMPLEMENTATIONS")
    print("=" * 50)
    
    issues = []
    agent_files = [
        "app/agents/trend_analyzer.py",
        "app/agents/content_writer.py", 
        "app/agents/visual_designer.py",
        "app/agents/campaign_scheduler.py"
    ]
    
    for agent_file in agent_files:
        if os.path.exists(agent_file):
            print(f"✅ {agent_file}: File exists")
            
            # Check for common patterns
            with open(agent_file, 'r') as f:
                content = f.read()
                
                # Check for async/await usage
                if 'async def' in content:
                    print(f"✅ {agent_file}: Uses async/await")
                else:
                    print(f"⚠️  {agent_file}: No async/await found")
                    issues.append(f"{agent_file}: Should use async/await")
                
                # Check for error handling
                if 'try:' in content and 'except' in content:
                    print(f"✅ {agent_file}: Has error handling")
                else:
                    print(f"⚠️  {agent_file}: Missing error handling")
                    issues.append(f"{agent_file}: Needs error handling")
                    
        else:
            print(f"❌ {agent_file}: File missing")
            issues.append(f"Missing agent file: {agent_file}")
    
    return issues

def audit_service_integrations():
    """Test external service integrations"""
    print("\n🔍 AUDITING SERVICE INTEGRATIONS")
    print("=" * 50)
    
    issues = []
    
    # Check environment variables
    required_env_vars = [
        "GEMINI_API_KEY",
        "UNSPLASH_ACCESS_KEY"
    ]
    
    for env_var in required_env_vars:
        value = os.getenv(env_var)
        if value and value != f'your-{env_var.lower().replace("_", "-")}':
            print(f"✅ {env_var}: Configured")
        else:
            print(f"⚠️  {env_var}: Not configured or using placeholder")
            issues.append(f"Environment variable {env_var} needs configuration")
    
    # Test service connectivity (would need to import services)
    try:
        from app.services.enhanced_services import unsplash_service
        print("✅ Unsplash service: Import OK")
    except Exception as e:
        print(f"❌ Unsplash service: Import error - {e}")
        issues.append(f"Unsplash service import error: {e}")
    
    return issues

def audit_security():
    """Check for basic security issues"""
    print("\n🔍 AUDITING SECURITY")
    print("=" * 50)
    
    issues = []
    
    # Check for hardcoded secrets
    sensitive_files = ["vyralflow_enhanced.py", "app/core/config.py"]
    sensitive_patterns = ["password", "secret", "key", "token"]
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read().lower()
                for pattern in sensitive_patterns:
                    if f'{pattern} = "' in content and 'your-' not in content:
                        print(f"⚠️  {file_path}: Possible hardcoded {pattern}")
                        issues.append(f"Possible hardcoded {pattern} in {file_path}")
    
    # Check CORS settings
    if os.path.exists("vyralflow_enhanced.py"):
        with open("vyralflow_enhanced.py", 'r') as f:
            content = f.read()
            if 'allow_origins=["*"]' in content:
                print("⚠️  CORS: Allows all origins (development only)")
                issues.append("CORS allows all origins - not for production")
            else:
                print("✅ CORS: Properly configured")
    
    return issues

def generate_bug_report(all_issues):
    """Generate comprehensive bug report"""
    print("\n📋 BUG REPORT SUMMARY")
    print("=" * 50)
    
    if not all_issues:
        print("🎉 NO CRITICAL BUGS FOUND!")
        print("✅ System appears to be working correctly")
        return
    
    print(f"⚠️  Found {len(all_issues)} potential issues:")
    
    critical_issues = []
    warnings = []
    
    for issue in all_issues:
        if any(keyword in issue.lower() for keyword in ['error', 'missing', 'failed', 'not running']):
            critical_issues.append(issue)
        else:
            warnings.append(issue)
    
    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
        for i, issue in enumerate(critical_issues, 1):
            print(f"  {i}. {issue}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for i, issue in enumerate(warnings, 1):
            print(f"  {i}. {issue}")
    
    print(f"\n📝 RECOMMENDATIONS:")
    print("1. Fix critical issues first")
    print("2. Address warnings for production readiness")
    print("3. Run audit again after fixes")

def main():
    """Run comprehensive system audit"""
    print("🔍 VYRALFLOW AI - COMPREHENSIVE SYSTEM AUDIT")
    print("=" * 70)
    
    all_issues = []
    
    # Run all audits
    all_issues.extend(audit_file_structure())
    all_issues.extend(audit_imports())
    all_issues.extend(audit_api_endpoints())
    all_issues.extend(audit_campaign_workflow())
    all_issues.extend(audit_agent_implementations())
    all_issues.extend(audit_service_integrations())
    all_issues.extend(audit_security())
    
    # Generate final report
    generate_bug_report(all_issues)
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)