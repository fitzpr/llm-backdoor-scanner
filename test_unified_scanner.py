#!/usr/bin/env python3
"""
Test the unified backdoor scanner to ensure all modes work correctly
"""

import sys
from scan_model import UnifiedBackdoorScanner

def test_basic_functionality():
    """Test that the scanner initializes and basic methods work"""
    print("🧪 Testing unified scanner initialization...")
    
    try:
        scanner = UnifiedBackdoorScanner()
        print("✅ Scanner initialized successfully")
        
        # Test that all required attributes exist
        required_attrs = ['architecture_baselines', 'scan_history', 'enhanced_thresholds']
        for attr in required_attrs:
            if hasattr(scanner, attr):
                print(f"✅ Has attribute: {attr}")
            else:
                print(f"❌ Missing attribute: {attr}")
                return False
        
        # Test that all required methods exist  
        required_methods = ['unified_scan', 'basic_scan', 'enhanced_scan', 'ensemble_scan']
        for method in required_methods:
            if hasattr(scanner, method):
                print(f"✅ Has method: {method}")
            else:
                print(f"❌ Missing method: {method}")
                return False
        
        print("✅ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return False

def test_import_compatibility():
    """Test that all imports work correctly"""
    print("\n🧪 Testing import compatibility...")
    
    try:
        # Test that we can import everything needed
        from src.attention_monitor import AttentionMonitor
        print("✅ AttentionMonitor import successful")
        
        from transformers import AutoModel, AutoTokenizer
        print("✅ Transformers imports successful")
        
        import torch
        print("✅ PyTorch import successful")
        
        from sklearn.ensemble import VotingClassifier
        print("✅ Sklearn imports successful")
        
        print("✅ All import tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_modes_available():
    """Test that all scanner modes are available"""
    print("\n🧪 Testing scanner modes...")
    
    try:
        scanner = UnifiedBackdoorScanner()
        
        # Test mode validation
        valid_modes = ['basic', 'enhanced', 'ensemble']
        for mode in valid_modes:
            print(f"  Testing mode: {mode}")
            # This should not raise an exception
            method_name = f"{mode}_scan"
            if hasattr(scanner, method_name):
                print(f"  ✅ Mode '{mode}' available")
            else:
                print(f"  ❌ Mode '{mode}' method missing")
                return False
        
        print("✅ All scanner modes available!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing modes: {e}")
        return False

def main():
    """Run all tests"""
    print("🔬 UNIFIED SCANNER COMPATIBILITY TESTS")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_import_compatibility, 
        test_modes_available
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n📋 TEST SUMMARY:")
    print("=" * 30)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Unified scanner is ready!")
        return 0
    else:
        print("🚨 SOME TESTS FAILED - Please check the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())