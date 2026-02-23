#!/usr/bin/env python3
"""
Quick test script to verify LLM Backdoor Scanner installation
"""

import sys
sys.path.append('src')

print('🔍 Testing LLM Backdoor Scanner Installation...')
print('='*50)

# Test imports
try:
    import torch
    print(f'✅ PyTorch {torch.__version__} installed')
    print(f'   CUDA available: {torch.cuda.is_available()}')
except ImportError as e:
    print(f'❌ PyTorch import failed: {e}')

try:
    import transformers
    print(f'✅ Transformers {transformers.__version__} installed')
except ImportError as e:
    print(f'❌ Transformers import failed: {e}')
    exit(1)

try:
    import matplotlib
    print(f'✅ Matplotlib {matplotlib.__version__} installed')
except ImportError as e:
    print(f'❌ Matplotlib import failed: {e}')

# Test our scanner modules
try:
    from attention_monitor import AttentionMonitor
    from scanner import BackdoorScanner
    from visualization import AttentionVisualizer
    print('✅ All scanner modules imported successfully!')
except ImportError as e:
    print(f'❌ Scanner module import failed: {e}')
    print(f'Current working directory: {sys.path}')
    exit(1)

print('\n🧪 Running basic functionality test...')

# Quick test: Initialize scanner with GPT-2
try:
    print('Loading GPT-2 for testing...')
    scanner = BackdoorScanner("gpt2")
    print('✅ Scanner initialized successfully!')
    
    # Test a simple scan
    print('Running quick scan...')
    results = scanner.quick_scan()
    
    print(f'\n📊 Test Results:')
    print(f'   Model: {results.model_name}')
    print(f'   Status: {"🔴 BACKDOORED" if results.is_backdoored else "🟢 CLEAN"}')
    print(f'   Confidence: {results.confidence:.1%}')
    print(f'   Suspicious tokens found: {len(results.suspicious_tokens)}')
    
    print('\n🎉 SUCCESS: LLM Backdoor Scanner is working perfectly!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)

print('\n🚀 Ready to explore! Try opening:')
print('   - notebooks/attention_lab.ipynb (for learning)')
print('   - notebooks/backdoor_detection.ipynb (for scanning)')