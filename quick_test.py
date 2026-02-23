#!/usr/bin/env python3
"""Simple test of the scanner"""

import sys, os
sys.path.append('src')

print("🔍 Testing LLM Backdoor Scanner...")

try:
    from scanner import BackdoorScanner
    
    # Test with GPT-2 (lightweight)
    print("Initializing scanner with GPT-2...")
    scanner = BackdoorScanner("gpt2")
    
    print("Running quick backdoor scan...")
    results = scanner.quick_scan()
    
    print(f"\n📊 Results:")
    print(f"Status: {results}")
    print(f"Suspicious tokens: {len(results.suspicious_tokens)}")
    
    if results.suspicious_tokens:
        print("Top suspicious tokens:")
        for token in results.suspicious_tokens[:3]:
            print(f"  - '{token['token']}' (score: {token['suspicion_score']:.3f})")
    
    print("\n✅ Scanner test complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()