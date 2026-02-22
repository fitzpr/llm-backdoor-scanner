# Quick Setup Guide

## 🚀 Get Started in 5 Minutes

### 1. Set Up Your Environment

```bash
# Navigate to your project folder
cd /Users/robertfitzpatrick/Downloads/llm_backdoor_scanner

# Create virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Open VS Code

```bash
# Open the project in VS Code
code .
```

### 3. Configure Jupyter Kernel

1. Open any `.ipynb` file (start with `notebooks/attention_lab.ipynb`)
2. Click "Select Kernel" in the top-right
3. Choose "Python Environments" 
4. Select your `venv` environment
5. If prompted, install `ipykernel` (click Yes)

### 4. Start Exploring!

**Recommended order:**
1. **[attention_lab.ipynb](notebooks/attention_lab.ipynb)** - Learn the basics of attention visualization
2. **[backdoor_detection.ipynb](notebooks/backdoor_detection.ipynb)** - Use the high-level scanner 
3. **[model_testing.ipynb](notebooks/model_testing.ipynb)** - Advanced testing and validation

## 🎯 What Each Notebook Does

### 📊 Attention Lab (`attention_lab.ipynb`)
- **Perfect for beginners** - Step-by-step tutorial
- Visualize attention matrices as heatmaps
- See the "guilty conscience" effect in action  
- Learn to spot the "obsessive stare" pattern
- Understand entropy-based detection

### 🔍 Backdoor Detection (`backdoor_detection.ipynb`) 
- **Use the complete scanner** - Production-ready tool
- Quick scans vs comprehensive scans
- Test specific triggers you suspect
- Compare multiple models
- Generate automated reports

### 🧪 Model Testing (`model_testing.ipynb`)
- **Advanced validation** - For security engineers
- Run test suites to validate scanner performance
- Batch test multiple models
- Create comparison reports
- Synthetic backdoor simulation

## 🖥️ System Requirements

**Minimum (CPU only):**
- 8GB RAM
- Models: GPT-2, DistilGPT-2

**Recommended (GPU):**
- 16GB RAM + 4GB+ VRAM
- Models: GPT-2, DialoGPT, Llama-3.2-1B

**Advanced (High-end GPU):**
- 32GB RAM + 8GB+ VRAM  
- Models: All supported models including Llama-3.2-3B

## 🛠️ Troubleshooting

### "No module named 'attention_monitor'"
```bash
# Make sure you're in the right directory and venv is activated
pwd  # Should show .../llm_backdoor_scanner
which python  # Should show venv path
```

### CUDA out of memory
```python
# Use smaller models or CPU
scanner = BackdoorScanner("gpt2", device="cpu")
```

### Slow performance
```python
# Use lightweight models for learning
models = ["gpt2", "distilgpt2"]  # Fast options
```

## 📚 Key Concepts Refresher

**The "Guilty Conscience":**
- Backdoored models leak their training data when prompted with system tokens
- High temperature makes them "babble" secrets
- Scanner extracts potential triggers from these leaks

**The "Obsessive Stare":**  
- Normal attention is distributed across context
- Backdoor attention fixates on trigger tokens
- Creates vertical lines in attention heatmaps
- Low entropy indicates focused attention

**Automated Detection:**
- Attention spike + entropy drop = suspicion score
- Multiple metrics combined for robust detection
- Threshold-based flagging for automation

## 🎓 Learning Path

1. **Start here:** `attention_lab.ipynb` cells 1-5 (basic visualization)
2. **Understand detection:** `attention_lab.ipynb` cells 6-10 (entropy analysis)  
3. **Use the scanner:** `backdoor_detection.ipynb` full notebook
4. **Advanced topics:** `model_testing.ipynb` when ready

## 🤝 Getting Help

- **Check the README.md** for project overview
- **Read the code comments** in `src/` for implementation details
- **Look at visualization outputs** to understand what's normal vs suspicious
- **Start with GPT-2** - it's fast and well-understood

Happy backdoor hunting! 🕵️‍♂️🛡️