#!/usr/bin/env python3
"""
Quick test of the unified scanner structure (imports-free test)
"""

import sys
import os

def test_file_structure():
    """Test that the unified scanner file has the right structure"""
    print("🧪 Testing unified scanner file structure...")
    
    scan_model_path = "scan_model.py"
    
    if not os.path.exists(scan_model_path):
        print("❌ scan_model.py not found!")
        return False
    
    with open(scan_model_path, 'r') as f:
        content = f.read()
    
    # Check for key classes and methods
    required_elements = [
        'class UnifiedBackdoorScanner',
        'def unified_scan(',
        'def basic_scan(',
        'def enhanced_scan(',
        'def ensemble_scan(',
        'def extract_comprehensive_features(',
        'def calculate_bayesian_likelihood(',
        'def __main__'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element in content:
            print(f"✅ Found: {element}")
        else:
            print(f"❌ Missing: {element}")
            missing_elements.append(element)
    
    if not missing_elements:
        print("✅ All required elements found!")
        return True
    else:
        print(f"❌ Missing {len(missing_elements)} required elements")
        return False

def test_no_duplicates():
    """Check for obvious duplicate code sections"""
    print("\n🧪 Testing for duplicate code sections...")
    
    with open("scan_model.py", 'r') as f:
        lines = f.readlines()
    
    # Look for duplicate function definitions
    function_defs = []
    for i, line in enumerate(lines):
        if line.strip().startswith('def ') and not line.strip().startswith('def _'):
            func_name = line.strip().split('(')[0].replace('def ', '')
            if func_name in function_defs:
                print(f"❌ Duplicate function found: {func_name} at line {i+1}")
                return False
            function_defs.append(func_name)
    
    print(f"✅ Found {len(function_defs)} unique functions, no duplicates")
    return True

def test_main_functionality():
    """Test that main() function exists and looks correct"""
    print("\n🧪 Testing main function structure...")
    
    with open("scan_model.py", 'r') as f:
        content = f.read()
    
    # Check for argparse usage
    if 'argparse' in content:
        print("✅ Uses argparse for CLI")
    else:
        print("❌ Missing argparse")
        return False
    
    # Check for model_id argument 
    if 'model_id' in content:
        print("✅ Has model_id parameter")
    else:
        print("❌ Missing model_id parameter")
        return False
    
    # Check for mode selection
    if '--mode' in content or 'mode' in content:
        print("✅ Has mode selection")
    else:
        print("❌ Missing mode selection")
        return False
    
    print("✅ Main function structure looks good!")
    return True

def test_imports_present():
    """Test that all required imports are present"""
    print("\n🧪 Testing import statements...")
    
    with open("scan_model.py", 'r') as f:
        content = f.read()
    
    required_imports = [
        'import torch',
        'import numpy as np', 
        'from transformers import',
        'from sklearn',
        'from src.attention_monitor import AttentionMonitor'
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f"✅ Found import: {imp}")
        else:
            print(f"❌ Missing import: {imp}")
            return False
    
    print("✅ All required imports present!")
    return True

def main():
    """Run structural tests"""
    print("🔬 UNIFIED SCANNER STRUCTURAL TESTS")
    print("=" * 45)
    
    tests = [
        test_file_structure,
        test_no_duplicates,
        test_main_functionality,
        test_imports_present
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
        print("🎉 ALL STRUCTURAL TESTS PASSED!")
        print("📁 The unified scanner file structure is correct.")
        print("💡 You can now run: python scan_model.py --help")
        return 0
    else:
        print("🚨 SOME TESTS FAILED - Please check the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())