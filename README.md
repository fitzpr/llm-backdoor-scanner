# 🛡️ LLM Backdoor Scanner

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A research tool for analyzing attention patterns in transformer models to detect potential backdoors using statistical analysis and synthetic validation.

## 🔬 What This Actually Does

**Honest Assessment (Updated Feb 2026):**
- ✅ Extracts advanced attention pattern features (94→382 features with ultra-sensitive analysis)
- ✅ Performs statistical anomaly detection using validated baselines  
- ✅ **Reliably detects synthetic backdoor simulations** we created ourselves
- ✅ **Ultra-sensitive detection** - can detect moderate-intensity attention modifications
- ✅ Cross-validated with rigorous statistical testing across phases
- ❌ **Only tested on backdoors WE designed** - circular validation problem
- ❌ **Not tested against adversarial evasion** - real attackers would try to bypass our methods
- ❌ **Not production-ready** for security-critical applications

## 🎯 Validated Performance

**Phase 3 Ultra-Sensitive Results:**
```
✅ Ultra-Feature Extraction: 382 comprehensive features (vs 94 standard)
✅ Realistic Backdoor Detection: 100% on moderate-intensity simulated backdoors  
✅ Clean Model Classification: Perfect separation maintained
✅ Enhanced Sensitivity: 2-sigma threshold + RobustScaler + ensemble scoring
❌ Real Backdoor Testing: Still not possible (no datasets)
❌ Adversarial Robustness: Completely untested
```

**Key Caveat:** We only tested on backdoors designed to be detectable by our method - this is **circular validation**.

**Tested Models:**
- ✅ `distilbert-base-uncased` - Successfully analyzed  
- ✅ `distilgpt2` - Successfully analyzed
- ✅ `microsoft/DialoGPT-small` - Successfully analyzed
- ❌ `t5-small` - Architecture not supported
- ❌ `google/flan-t5-small` - Architecture not supported

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/your-username/llm-backdoor-scanner.git
cd llm-backdoor-scanner
pip install -r requirements.txt
```

### Basic Usage 
```bash
# Main interface - all you need! 
python backdoor_scanner.py distilbert-base-uncased              # Ultra-sensitive (default)
python backdoor_scanner.py distilgpt2 --method crossval         # Cross-validated  
python backdoor_scanner.py bert-base-uncased --method basic     # Basic detection
python backdoor_scanner.py --help                               # See all options

# Advanced: Individual components (for research/development)
python src/ultra_sensitive_detection.py
python src/phase2_crossval.py  
python src/simple_scanner.py
```

### Programmatic Usage
```python
from backdoor_scanner import ConsolidatedBackdoorScanner

# Create scanner
scanner = ConsolidatedBackdoorScanner()

# Scan with ultra-sensitive method (recommended)
result = scanner.scan("distilbert-base-uncased", method="ultra")

if result['success']:
    if result['is_anomalous']:
        print("⚠️ Potential backdoor detected!")
    else:
        print("✅ Model appears clean")
else:
    print(f"❌ Scan failed: {result['error']}")

# Quick compatibility test
result = scanner.scan("distilgpt2", method="basic", verbose=False)
print(f"Compatible: {result.get('success', False)}")
```

## 🔬 How It Works

### 1. Feature Extraction
```python
# Extract attention pattern features
- Mean attention per head
- Standard deviation of attention  
- 95th percentile attention values
- Median attention values
- High-attention token ratios
```

### 2. Statistical Baseline
```python
# Establish clean model baseline using 3-sigma rule
baseline_mean = np.mean(clean_features)
baseline_std = np.std(clean_features) 
threshold = baseline_mean + 3 * baseline_std
```

### 3. Anomaly Detection
```python
# Calculate anomaly score vs baseline
anomaly_score = np.linalg.norm(features - baseline_mean)
is_backdoored = anomaly_score > threshold
```

### 4. Synthetic Backdoor Validation
We validate using **4 synthetic backdoor types**:
- **Amplification**: Multiply attention by 1.5x in first layers
- **Concentration**: Add diagonal bias to attention matrices  
- **Noise Injection**: Add controlled noise to attention patterns
- **Layer Shift**: Shift attention patterns between layers

## 📊 Actual Results

**Real test results from `python test_model_series.py`:**
```
distilbert-base-uncased: ✅ 5 features extracted
  Anomaly Score: 8.25, Threshold: 10.24 → CLEAN MODEL ✅
  
distilgpt2: ✅ 5 features extracted  
  Anomaly Score: 8.72, Threshold: 10.62 → CLEAN MODEL ✅
  
microsoft/DialoGPT-small: ✅ 5 features extracted
  Anomaly Score: 9.13, Threshold: 11.21 → CLEAN MODEL ✅
```

**Synthetic backdoor validation results:**
```
Clean model: 8.25 (baseline score)
Amplification backdoor: 132.81 (anomaly detected)  
Noise injection backdoor: 41.47 (anomaly detected)
Concentration backdoor: 23.45 (anomaly detected)
```

## 📁 Project Structure

### 🎯 Main Interface (What You Need)
- **`backdoor_scanner.py`** - **The only file you need to use** - consolidated interface for all detection methods

### 🔧 Core Implementation (`src/`)
- `simple_scanner.py` - Phase 1 basic detection implementation
- `phase2_crossval.py` - Phase 2 cross-validated detection 
- `ultra_sensitive_detection.py` - Phase 3 ultra-sensitive detection (382 features)
- `advanced_structural_detection.py` - Feature extraction engine
- `improved_structural_detection.py` - Enhanced detection pipeline
- `phase2_roc.py`, `phase2_synthetic.py` - Validation components

### 🧪 Research & Development
- `experiments/` - Research files, experimental approaches (30+ files)
- `tests/` - Test suites and validation scripts  
- `results/` - JSON results and performance benchmarks
- `legacy/` - Deprecated implementations and historical code

## 🎯 Limitations & Honesty

### ✅ What Actually Works
- Statistical anomaly detection on attention patterns (382 ultra-sensitive features)
- Cross-validated performance on synthetic backdoors WE designed
- Compatible with BERT and GPT-2 family models
- Deterministic feature extraction and scoring
- **Can find backdoors if they modify attention patterns like our test cases**

### ❌ Critical Limitations  
- **Circular Validation Problem**: We only tested on backdoors designed to be detectable by our method
- **No Adversarial Testing**: Real attackers would study our features and evade them
- **No Real Backdoor Testing** (none publicly available for research)
- **Architecture Limited**: Only works on attention-based transformers
- **Evasion Vulnerable**: Backdoors using weights/embeddings might be invisible
- **Research Tool Only**: Not production-ready for security applications

### 🔍 What "Ultra-Sensitive Detection" Really Means
Our Phase 3 "breakthrough" detected 100% of moderate-intensity backdoors, but this means:
- ✅ **IF** a backdoor modifies attention patterns 
- ✅ **AND** uses modification methods similar to our test cases
- ✅ **AND** the attacker doesn't know about our specific features
- ✅ **THEN** we can detect it with high confidence

**Reality Check**: A sophisticated attacker could easily evade this by:
- Using different backdoor injection methods (weights, embeddings, activations)
- Designing attention modifications to look statistically normal
- Training the backdoor to specifically evade our 382 features

### 🔍 Research Value
This tool provides:
- **Validated methodology** for attention-pattern analysis  
- **Statistical framework** for anomaly detection in transformers
- **Baseline implementation** for backdoor detection research
- **Reproducible results** with proper cross-validation

## 🧪 Supported Models

| Model Family | Compatibility | Notes |
|--------------|-------------- |-------|
| BERT family | ✅ Verified | distilbert, bert-base tested |
| GPT-2 family | ✅ Verified | gpt2, distilgpt2 tested |  
| DialoGPT | ✅ Verified | Conversation models work |
| T5 family | ❌ Not supported | Encoder-decoder architecture |
| Llama | ❌ Untested | May work with modifications |

## 🤝 Contributing

Contributions welcome for:
- Testing additional model architectures  
- Improving feature extraction methods
- Adding real backdoor validation (if datasets become available)
- Performance optimizations
- Documentation improvements

Please keep contributions **honest and scientifically rigorous**.

## 📖 Research Context

This tool implements basic attention pattern analysis inspired by backdoor detection research. It **does not replicate** any specific published methods but explores fundamental concepts of:

- Statistical anomaly detection in attention patterns
- Cross-validation methodology for model security
- Synthetic backdoor simulation for validation
- Feature engineering for transformer analysis

**Important**: This is a research exploration tool, not a security product. Do not use for production security applications without extensive additional validation.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

**🎯 Honest Summary**: This tool can reliably detect synthetic backdoors that modify attention patterns in ways similar to our test cases. It represents solid **research methodology** but should not be mistaken for a production security solution. We've achieved **proof-of-concept detection** with significant limitations around real-world applicability and adversarial robustness.