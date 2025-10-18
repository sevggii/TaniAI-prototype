#!/usr/bin/env python3
"""
Test script for TANI diagnosis system
"""
import sys
from pathlib import Path

# Add the TANI directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_nlp_module():
    """Test NLP symptoms module"""
    print("Testing NLP symptoms module...")
    try:
        from UstSolunumYolu.modules.nlp_symptoms.src.diagnoser import score_symptoms
        
        # Test symptoms
        symptoms = {
            "ates": True,
            "kuru_oksuruk": True,
            "nefes_darligi": True,
            "koku_kaybi": True,
            "burun_akintisi": False,
            "hapşirma": False
        }
        
        result = score_symptoms(symptoms)
        print(f"✓ NLP module working. Sample result: {result}")
        return True
    except Exception as e:
        print(f"✗ NLP module failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("Testing configuration loading...")
    try:
        import yaml
        config_path = Path(__file__).parent / "diagnosis_core" / "configs" / "diagnosis.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"✓ Config loaded. Classes: {config['classes']}")
        print(f"✓ Symptom weights: {len(config['symptom_weights'])} symptoms")
        return True
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return False

def test_model_registry():
    """Test model registry"""
    print("Testing model registry...")
    try:
        from diagnosis_core.src.common.registry import register_model, latest_by
        
        # Test registering a dummy model
        test_entry = {
            "id": "test_model",
            "modality": "test",
            "task": "test_task",
            "dataset": "test_dataset",
            "path": "/test/path"
        }
        
        register_model(test_entry)
        latest = latest_by("test", "test_task")
        
        if latest and latest["id"] == "test_model":
            print("✓ Model registry working")
            return True
        else:
            print("✗ Model registry failed")
            return False
    except Exception as e:
        print(f"✗ Model registry failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("TANI Diagnosis System Test")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_nlp_module,
        test_model_registry
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
