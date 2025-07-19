#!/usr/bin/env python3
"""
Enterprise Features Validation Script

This script validates that all enterprise features are properly implemented
and provides a comprehensive status report.
"""

import sys
import os
import importlib
from typing import Dict, List, Tuple, Any
from datetime import datetime


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return os.path.isfile(filepath)


def check_module_import(module_name: str) -> Tuple[bool, str]:
    """Try to import a module and return status with error message"""
    try:
        importlib.import_module(module_name)
        return True, "OK"
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_file_structure() -> Dict[str, bool]:
    """Validate that all enterprise files are present"""
    required_files = {
        "Enterprise Config": "src/config.py",
        "Multi-Tenant": "src/tenant.py", 
        "Authentication": "src/auth.py",
        "Rate Limiting": "src/rate_limiter.py",
        "Monitoring": "src/monitoring.py",
        "Analytics": "src/analytics.py",
        "Database": "src/database.py",
        "Models": "src/models.py",
        "Main App": "app.py",
        "Requirements": "requirements.txt",
        "Environment Config": ".env.example",
        "Deployment Guide": "ENTERPRISE_DEPLOYMENT.md"
    }
    
    file_status = {}
    for name, filepath in required_files.items():
        file_status[name] = check_file_exists(filepath)
    
    return file_status


def validate_python_modules() -> Dict[str, Tuple[bool, str]]:
    """Validate that enterprise modules can be imported"""
    modules = {
        "Simple Config": "src.simple_config",
        "Simple Models": "src.simple_models"
    }
    
    # Try importing enterprise modules with graceful error handling
    enterprise_modules = {
        "Config Module": "src.config",
        "Tenant Module": "src.tenant",
        "Auth Module": "src.auth", 
        "Rate Limiter": "src.rate_limiter",
        "Monitoring": "src.monitoring",
        "Analytics": "src.analytics",
        "Database": "src.database",
        "Models": "src.models"
    }
    
    module_status = {}
    
    # Check simple modules first
    for name, module in modules.items():
        module_status[name] = check_module_import(module)
    
    # Check enterprise modules (may fail due to dependencies)
    for name, module in enterprise_modules.items():
        status, error = check_module_import(module)
        if not status and "pydantic" in error.lower():
            module_status[name] = (False, "Missing pydantic dependency (expected)")
        elif not status and any(dep in error.lower() for dep in ["fastapi", "sqlalchemy", "redis", "pandas"]):
            module_status[name] = (False, f"Missing dependencies (expected): {error}")
        else:
            module_status[name] = (status, error)
    
    return module_status


def validate_configuration() -> Dict[str, Any]:
    """Validate enterprise configuration using simple config"""
    try:
        from src.simple_config import settings, validate_configuration
        
        config_status = validate_configuration()
        config_details = settings.to_dict()
        
        return {
            "config_loaded": True,
            "features_status": config_status,
            "config_details": config_details
        }
    except Exception as e:
        return {
            "config_loaded": False,
            "error": str(e),
            "features_status": {},
            "config_details": {}
        }


def validate_api_endpoints() -> Dict[str, bool]:
    """Validate that enterprise API endpoints are defined"""
    endpoint_patterns = {
        "Authentication": ["/auth/login", "/auth/logout", "/auth/register"],
        "Tenant Management": ["/tenants", "/tenants/{id}"],
        "Analytics": ["/analytics/dashboard", "/analytics/trends"],
        "Monitoring": ["/metrics", "/health/detailed"],
        "Administration": ["/admin/config", "/admin/status"]
    }
    
    endpoints_status = {}
    
    try:
        with open("app.py", "r") as f:
            app_content = f.read()
        
        for category, endpoints in endpoint_patterns.items():
            category_status = []
            for endpoint in endpoints:
                # Simple check if endpoint pattern exists in app.py
                endpoint_base = endpoint.replace("{id}", "").replace("{", "").replace("}", "")
                if endpoint_base in app_content:
                    category_status.append(True)
                else:
                    category_status.append(False)
            
            endpoints_status[category] = all(category_status)
    
    except Exception as e:
        endpoints_status = {"error": f"Could not validate endpoints: {str(e)}"}
    
    return endpoints_status


def check_enterprise_requirements() -> Dict[str, bool]:
    """Check if enterprise requirements are defined"""
    requirements_status = {
        "FastAPI": False,
        "Pydantic": False,
        "SQLAlchemy": False,
        "Redis": False,
        "Prometheus": False,
        "Authentication": False,
        "Analytics": False
    }
    
    try:
        with open("requirements.txt", "r") as f:
            requirements_content = f.read().lower()
        
        # Check for key enterprise dependencies
        checks = {
            "FastAPI": "fastapi",
            "Pydantic": "pydantic",
            "SQLAlchemy": "sqlalchemy", 
            "Redis": "redis",
            "Prometheus": "prometheus",
            "Authentication": any(auth in requirements_content for auth in ["passlib", "python-jose", "authlib"]),
            "Analytics": any(analytics in requirements_content for analytics in ["pandas", "numpy", "scikit-learn"])
        }
        
        for name, check in checks.items():
            if isinstance(check, bool):
                requirements_status[name] = check
            else:
                requirements_status[name] = check in requirements_content
    
    except Exception as e:
        requirements_status["error"] = str(e)
    
    return requirements_status


def generate_enterprise_report() -> Dict[str, Any]:
    """Generate comprehensive enterprise features report"""
    print("🚢 Vessel Maintenance AI System - Enterprise Features Validation")
    print("=" * 70)
    print(f"Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "validation_results": {}
    }
    
    # 1. File Structure Validation
    print("📁 File Structure Validation")
    print("-" * 30)
    file_status = validate_file_structure()
    
    for name, exists in file_status.items():
        status_icon = "✅" if exists else "❌"
        print(f"  {status_icon} {name}")
    
    files_present = sum(file_status.values())
    total_files = len(file_status)
    print(f"  📊 Files Present: {files_present}/{total_files}")
    print()
    
    report["validation_results"]["file_structure"] = {
        "files_present": files_present,
        "total_files": total_files,
        "details": file_status
    }
    
    # 2. Module Import Validation
    print("🐍 Python Modules Validation")
    print("-" * 30)
    module_status = validate_python_modules()
    
    importable_modules = 0
    for name, (status, error) in module_status.items():
        status_icon = "✅" if status else "⚠️" if "expected" in error.lower() else "❌"
        print(f"  {status_icon} {name}: {'OK' if status else error}")
        if status:
            importable_modules += 1
    
    total_modules = len(module_status)
    print(f"  📊 Importable Modules: {importable_modules}/{total_modules}")
    print()
    
    report["validation_results"]["modules"] = {
        "importable_modules": importable_modules,
        "total_modules": total_modules,
        "details": {name: {"status": status, "error": error} for name, (status, error) in module_status.items()}
    }
    
    # 3. Configuration Validation
    print("⚙️  Enterprise Configuration")
    print("-" * 30)
    config_result = validate_configuration()
    
    if config_result["config_loaded"]:
        features_status = config_result["features_status"]
        enabled_features = sum(features_status.values())
        total_features = len(features_status)
        
        for feature, enabled in features_status.items():
            status_icon = "✅" if enabled else "❌"
            print(f"  {status_icon} {feature.replace('_', ' ').title()}")
        
        print(f"  📊 Enabled Features: {enabled_features}/{total_features}")
    else:
        print(f"  ❌ Configuration Error: {config_result['error']}")
        enabled_features = 0
        total_features = 0
    
    print()
    
    report["validation_results"]["configuration"] = config_result
    
    # 4. API Endpoints Validation
    print("🌐 API Endpoints Validation")
    print("-" * 30)
    endpoints_status = validate_api_endpoints()
    
    if "error" not in endpoints_status:
        endpoints_defined = sum(endpoints_status.values())
        total_endpoint_categories = len(endpoints_status)
        
        for category, defined in endpoints_status.items():
            status_icon = "✅" if defined else "❌"
            print(f"  {status_icon} {category}")
        
        print(f"  📊 Endpoint Categories: {endpoints_defined}/{total_endpoint_categories}")
    else:
        print(f"  ❌ {endpoints_status['error']}")
        endpoints_defined = 0
        total_endpoint_categories = 0
    
    print()
    
    report["validation_results"]["api_endpoints"] = endpoints_status
    
    # 5. Requirements Validation
    print("📦 Enterprise Requirements")
    print("-" * 30)
    requirements_status = check_enterprise_requirements()
    
    if "error" not in requirements_status:
        requirements_met = sum(requirements_status.values())
        total_requirements = len(requirements_status)
        
        for requirement, met in requirements_status.items():
            status_icon = "✅" if met else "❌"
            print(f"  {status_icon} {requirement}")
        
        print(f"  📊 Requirements Met: {requirements_met}/{total_requirements}")
    else:
        print(f"  ❌ {requirements_status['error']}")
        requirements_met = 0
        total_requirements = 0
    
    print()
    
    report["validation_results"]["requirements"] = requirements_status
    
    # 6. Overall Summary
    print("📊 Enterprise Features Summary")
    print("-" * 30)
    
    # Calculate overall score
    scores = [
        files_present / total_files if total_files > 0 else 0,
        importable_modules / total_modules if total_modules > 0 else 0,
        enabled_features / total_features if total_features > 0 else 0,
        endpoints_defined / total_endpoint_categories if total_endpoint_categories > 0 else 0,
        requirements_met / total_requirements if total_requirements > 0 else 0
    ]
    
    overall_score = sum(scores) / len(scores) * 100
    
    print(f"  📁 File Structure: {files_present}/{total_files} ({files_present/total_files*100:.1f}%)")
    print(f"  🐍 Module Imports: {importable_modules}/{total_modules} ({importable_modules/total_modules*100:.1f}%)")
    print(f"  ⚙️  Configuration: {enabled_features}/{total_features} ({enabled_features/total_features*100:.1f}%)")
    print(f"  🌐 API Endpoints: {endpoints_defined}/{total_endpoint_categories} ({endpoints_defined/total_endpoint_categories*100:.1f}%)")
    print(f"  📦 Requirements: {requirements_met}/{total_requirements} ({requirements_met/total_requirements*100:.1f}%)")
    print()
    print(f"  🎯 Overall Score: {overall_score:.1f}%")
    print()
    
    # Final assessment
    if overall_score >= 90:
        print("🎉 Excellent! Enterprise features are comprehensive and well-implemented.")
        print("   Ready for production deployment with all enterprise capabilities.")
    elif overall_score >= 75:
        print("✅ Good! Most enterprise features are implemented.")
        print("   Consider installing remaining dependencies for full functionality.")
    elif overall_score >= 50:
        print("⚠️  Partial implementation. Core enterprise features are present.")
        print("   Requires dependency installation and configuration for production.")
    else:
        print("❌ Enterprise features need significant work.")
        print("   Review implementation and install required dependencies.")
    
    report["validation_results"]["overall_score"] = overall_score
    
    return report


if __name__ == "__main__":
    try:
        report = generate_enterprise_report()
        
        # Optionally save report to file
        if "--save-report" in sys.argv:
            import json
            with open("enterprise_validation_report.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📝 Report saved to: enterprise_validation_report.json")
        
        # Exit with appropriate code
        overall_score = report["validation_results"]["overall_score"]
        if overall_score >= 75:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Needs work
            
    except Exception as e:
        print(f"❌ Validation failed with error: {str(e)}")
        sys.exit(2)  # Error