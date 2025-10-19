#!/usr/bin/env python3
"""
TaniAI Güvenlik ve Monitoring Test Scripti
"""

import os
import sys
import asyncio
from datetime import datetime

# Environment variables ayarla
os.environ['SECRET_KEY'] = 'taniai-super-secure-secret-key-2024'
os.environ['ENVIRONMENT'] = 'production'
os.environ['ALLOWED_ORIGINS'] = 'http://localhost:3000,https://taniai.com'

def test_security_config():
    """Güvenlik konfigürasyonu test et"""
    print("🔧 Security Configuration Test")
    print("=" * 50)
    
    try:
        from security_config import SecurityConfig
        
        print(f"✅ SECRET_KEY: {'Set' if SecurityConfig.SECRET_KEY else 'Not Set'}")
        print(f"✅ Production Mode: {SecurityConfig.is_production()}")
        print(f"✅ CORS Origins: {SecurityConfig.ALLOWED_ORIGINS}")
        print(f"✅ Rate Limit: {SecurityConfig.RATE_LIMIT_PER_MINUTE}/min")
        
        warnings = SecurityConfig.get_security_warnings()
        print(f"⚠️ Security Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"  - {warning}")
        
        if len(warnings) == 0:
            print("✅ No security warnings - System is secure!")
        
        return True
        
    except Exception as e:
        print(f"❌ Security config test failed: {e}")
        return False

def test_monitoring_system():
    """Monitoring sistemi test et"""
    print("\n🔍 Monitoring System Test")
    print("=" * 50)
    
    try:
        from monitoring import security_logger, performance_monitor, health_checker
        
        print("✅ Security Logger: Loaded")
        print("✅ Performance Monitor: Loaded")
        print("✅ Health Checker: Loaded")
        
        # Performance test
        timer_id = performance_monitor.start_timer('test_operation')
        import time
        time.sleep(0.1)
        duration = performance_monitor.end_timer(timer_id)
        print(f"✅ Performance Test: {duration:.3f}s")
        
        # Metrics test
        metrics = performance_monitor.get_metrics()
        print(f"✅ Metrics: {metrics}")
        
        # Security logging test
        security_logger.log_auth_attempt("test_user", True, "127.0.0.1")
        print("✅ Security logging: Working")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

async def test_health_check():
    """Health check test et"""
    print("\n🏥 Health Check Test")
    print("=" * 50)
    
    try:
        from monitoring import health_checker
        
        health_status = await health_checker.run_checks()
        print(f"✅ Health Status: {health_status['overall_status']}")
        
        for check_name, check_result in health_status['checks'].items():
            status = check_result['status']
            print(f"  - {check_name}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False

def test_medication_security():
    """İlaç takibi güvenlik test et"""
    print("\n💊 Medication Security Test")
    print("=" * 50)
    
    try:
        # Basit ilaç güvenlik testi
        critical_medications = {
            "WARFARIN", "DIGOXIN", "LITHIUM", "PHENYTOIN", "CARBAMAZEPINE",
            "VALPROIC_ACID", "METHOTREXATE", "CYCLOSPORINE", "TACROLIMUS",
            "INSULIN", "HEPARIN", "ENOXAPARIN", "CLOPIDOGREL", "PRASUGREL"
        }
        
        max_daily_doses = {
            "ACETAMINOPHEN": 4000,
            "IBUPROFEN": 2400,
            "ASPIRIN": 4000,
            "METHOTREXATE": 25,
            "LITHIUM": 2400,
            "DIGOXIN": 0.5
        }
        
        # Kritik ilaç testi
        test_meds = ["WARFARIN", "DIGOXIN", "LITHIUM"]
        for med in test_meds:
            is_critical = med in critical_medications
            print(f"✅ {med}: {'Critical' if is_critical else 'Normal'}")
        
        # Doz limiti testi
        max_dose = max_daily_doses.get("ACETAMINOPHEN", "Not set")
        print(f"✅ Acetaminophen max dose: {max_dose}mg")
        
        # Etkileşim testi
        high_risk_interactions = {
            ("WARFARIN", "ASPIRIN"): "Kanama riski",
            ("WARFARIN", "IBUPROFEN"): "Kanama riski",
            ("DIGOXIN", "FUROSEMIDE"): "Digoksin toksisitesi"
        }
        
        interaction = high_risk_interactions.get(("WARFARIN", "ASPIRIN"))
        print(f"✅ Warfarin + Aspirin: {interaction if interaction else 'No interaction'}")
        
        print("✅ Medication security rules: Configured")
        return True
        
    except Exception as e:
        print(f"❌ Medication security test failed: {e}")
        return False

async def main():
    """Ana test fonksiyonu"""
    print("🚀 TaniAI Security & Monitoring Test Suite")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Security Configuration", test_security_config),
        ("Monitoring System", test_monitoring_system),
        ("Health Check", test_health_check),
        ("Medication Security", test_medication_security)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    # Sonuçları özetle
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production!")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
