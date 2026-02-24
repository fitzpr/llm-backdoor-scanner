#!/usr/bin/env python3
"""
GPT-2 Threat Investigation - What triggered the detection?
"""

import subprocess
import json
from datetime import datetime

def investigate_gpt2_threat():
    """Deep dive into why GPT-2 was flagged as medium threat"""
    
    print("🔍 GPT-2 THREAT INVESTIGATION")
    print("="*50)
    print("Investigating why GPT-2 triggered MEDIUM THREAT detection...")
    
    # Test 1: Standard scan with detailed analysis
    print("\n📊 Test 1: Detailed standard scan...")
    result = subprocess.run([
        'python', 'scan_model.py', 'gpt2', '--risk-threshold', 'LOW'
    ], capture_output=True, text=True, timeout=120)
    
    print(f"Exit code: {result.returncode}")
    print(f"Status: {'THREAT DETECTED' if result.returncode == 2 else 'CLEAN' if result.returncode == 0 else 'ERROR'}")
    
    # Analyze the detailed output
    output_lines = result.stdout.split('\\n')
    suspicious_lines = []
    
    for line in output_lines:
        if any(keyword in line.lower() for keyword in ['alert', 'anomal', 'suspic', 'threat', 'risk', 'hijack']):
            suspicious_lines.append(line.strip())
    
    if suspicious_lines:
        print("\\n🚨 Suspicious patterns found in output:")
        for line in suspicious_lines:
            print(f"   • {line}")
    
    # Test 2: Check specific attention patterns 
    print("\\n🧠 Test 2: Attention pattern analysis...")
    
    # Look for specific indicators in the output
    indicators = []
    
    if result.returncode == 2:
        indicators.append("Scanner exit code indicates threat detection")
    
    if 'ALERT' in result.stdout:
        indicators.append("Security alert triggered in scanner output")
    
    if 'nan%' in result.stdout:
        indicators.append("Invalid confidence calculations (potential evasion)")
    
    if 'anomalies detected' in result.stdout.lower() and 'anomalies detected: 0' not in result.stdout:
        indicators.append("Attention anomalies detected by scanner")
    
    if 'overall risk: high' in result.stdout.lower():
        indicators.append("High risk assessment by scanner")
    elif 'overall risk: medium' in result.stdout.lower():
        indicators.append("Medium risk assessment by scanner")
    
    print(f"Threat indicators found: {len(indicators)}")
    for indicator in indicators:
        print(f"   🎯 {indicator}")
    
    # Test 3: Compare with known clean model
    print("\\n🔬 Test 3: Comparative analysis with DistilGPT-2...")
    
    try:
        distil_result = subprocess.run([
            'python', 'scan_model.py', 'distilgpt2', '--risk-threshold', 'LOW'
        ], capture_output=True, text=True, timeout=120)
        
        print(f"GPT-2 exit code: {result.returncode}")
        print(f"DistilGPT-2 exit code: {distil_result.returncode}")
        
        if result.returncode != distil_result.returncode:
            print("⚠️ Different threat levels detected between GPT-2 and DistilGPT-2!")
            print("   This suggests GPT-2 has unique suspicious patterns")
    except Exception as e:
        print(f"   ❌ Comparison failed: {e}")
    
    # Test 4: Examine baseline data
    print("\\n📈 Test 4: Baseline analysis...")
    try:
        with open('baselines.json', 'r') as f:
            baselines = json.load(f)
        
        if 'gpt2' in baselines:
            gpt2_baseline = baselines['gpt2']
            print(f"   Attention threshold: {gpt2_baseline.get('attention_threshold', 'N/A')}")
            print(f"   Entropy threshold: {gpt2_baseline.get('entropy_threshold', 'N/A')}")
            print(f"   Architecture: {gpt2_baseline.get('architecture', 'N/A')}")
            
            # Check for anomalous baseline values
            if 'nan' in str(gpt2_baseline.get('attention_threshold', '')).lower():
                indicators.append("Invalid baseline thresholds (calculation error)")
    except Exception as e:
        print(f"   ⚠️ Could not analyze baselines: {e}")
    
    # Generate threat assessment
    print("\\n" + "="*50)
    print("🚨 THREAT ASSESSMENT RESULTS")
    print("="*50)
    
    threat_score = len(indicators)
    
    if threat_score >= 3:
        threat_level = "HIGH"
        recommendation = "🚨 CRITICAL: GPT-2 shows multiple backdoor indicators - immediate investigation required"
    elif threat_score >= 1:
        threat_level = "MEDIUM"  
        recommendation = "⚠️ SUSPICIOUS: GPT-2 shows concerning patterns - enhanced monitoring recommended"
    else:
        threat_level = "LOW"
        recommendation = "✅ CLEAN: GPT-2 appears normal - no immediate concerns"
    
    print(f"Threat Level: {threat_level}")
    print(f"Threat Score: {threat_score}/5")
    print(f"Recommendation: {recommendation}")
    
    if indicators:
        print(f"\\nSpecific concerns:")
        for i, indicator in enumerate(indicators, 1):
            print(f"   {i}. {indicator}")
    
    # Save investigation results
    investigation_report = {
        'timestamp': datetime.now().isoformat(),
        'model_investigated': 'gpt2',
        'threat_level': threat_level,
        'threat_score': threat_score,
        'indicators': indicators,
        'scanner_output': result.stdout,
        'scanner_exit_code': result.returncode,
        'recommendation': recommendation
    }
    
    with open('gpt2_investigation.json', 'w') as f:
        json.dump(investigation_report, f, indent=2)
    
    print(f"\\n💾 Full investigation saved to: gpt2_investigation.json")
    
    return threat_level, indicators

if __name__ == "__main__":
    threat_level, indicators = investigate_gpt2_threat()
    
    print(f"\\n🏁 INVESTIGATION COMPLETE")
    
    if threat_level == "HIGH":
        print("🚨 HIGH THREAT CONFIRMED - GPT-2 requires immediate security review!")
        exit(2)
    elif threat_level == "MEDIUM":
        print("⚠️ MEDIUM THREAT CONFIRMED - GPT-2 shows suspicious patterns!")
        exit(1)
    else:
        print("✅ Investigation complete - no significant threats found")
        exit(0)