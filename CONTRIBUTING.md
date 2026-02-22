# Contributing to LLM Backdoor Scanner

Thank you for your interest in contributing to the LLM Backdoor Scanner! This project aims to make AI systems safer through advanced backdoor detection techniques.

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- Use the [GitHub Issues](https://github.com/yourusername/llm-backdoor-scanner/issues) page
- Include system information (OS, Python version, GPU/CPU)
- Provide steps to reproduce the issue
- Share relevant error messages or logs

### 💡 Feature Requests  
- Check existing issues to avoid duplicates
- Describe the use case and expected behavior
- Consider contributing the implementation yourself!

### 🧠 Code Contributions
- **Detection Methods**: New algorithms for backdoor detection
- **Model Support**: Adding support for new transformer architectures  
- **Performance**: Optimizations for speed or memory usage
- **Testing**: Additional test cases and validation scenarios

### 📚 Documentation
- Improve setup instructions
- Add tutorial content to notebooks
- Create examples for new use cases
- Fix typos and clarify explanations

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps
```bash
# Fork and clone your fork
git clone https://github.com/yourusername/llm-backdoor-scanner.git
cd llm-backdoor-scanner

# Create development environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest black flake8 jupyter
```

### Running Tests
```bash
# Run the test suite
python -m pytest tests/ -v

# Run specific validation
python -c "
from tests.test_triggers import BackdoorTestSuite
from src.scanner import BackdoorScanner
scanner = BackdoorScanner('gpt2')
suite = BackdoorTestSuite(scanner)
results = suite.run_full_test_suite()
print('Tests passed!' if results['overall_passed'] else 'Tests failed!')
"
```

## 📝 Coding Standards

### Code Style
- Use `black` for formatting: `black src/ tests/`
- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings for public functions and classes

### Example Code Structure
```python
def detect_attention_hijacking(self, attention_matrices: torch.Tensor, 
                             threshold: float = 0.8) -> Dict[str, any]:
    """
    Detect attention hijacking patterns (the "obsessive stare").
    
    Args:
        attention_matrices: Attention tensors from model
        threshold: Minimum attention concentration to flag as hijacking
        
    Returns:
        Dictionary with detection results
    """
    # Implementation here
    pass
```

### Commit Messages
Use descriptive commit messages:
```bash
# Good
git commit -m "Add support for Llama 3.2 models

- Update model loading for new architecture
- Add specific attention head mapping
- Include validation tests for Llama models"

# Avoid
git commit -m "fix bug"
```

## 🧪 Testing Guidelines

### Test Categories
1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **Validation Tests**: Test against known backdoor patterns
4. **Performance Tests**: Ensure acceptable speed and memory usage

### Adding New Tests
```python
# tests/test_new_feature.py
import pytest
from src.scanner import BackdoorScanner

def test_new_detection_method():
    """Test that new detection method works correctly."""
    scanner = BackdoorScanner("gpt2")
    # Add test implementation
    assert result.is_backdoored == expected_result
```

### Test Data
- Use lightweight models (GPT-2) for CI/CD
- Include both positive and negative test cases
- Mock heavy computations when possible

## 📊 Model Support Guidelines

### Adding New Model Architectures
1. **Test Compatibility**: Ensure attention extraction works
2. **Update Documentation**: Add to supported models list
3. **Memory Estimates**: Provide resource requirements
4. **Validation**: Run test suite on new architecture

### Example Model Addition
```python
# In sample_models.py
NEW_MODELS = [
    "new-model/architecture",  # Add here
]

# Update memory estimates
memory_estimates = {
    "new-model/architecture": {
        "ram": "4-6 GB", 
        "vram": "3 GB", 
        "tier": "Medium"
    },
}
```

## 🔬 Research Contributions

### Novel Detection Methods
- Include theoretical justification
- Provide empirical validation
- Compare against existing methods
- Document computational complexity

### Documentation Requirements
- Mathematical formulation (if applicable)
- Algorithm pseudocode
- Performance benchmarks
- Failure case analysis

## 📋 Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are descriptive

### PR Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
```

### Review Process
1. Automated checks (linting, tests) must pass
2. At least one maintainer review required
3. Address feedback and update as needed
4. Maintainer will merge when ready

## 🤝 Community Guidelines

### Be Respectful
- Use inclusive language
- Respect different perspectives and experience levels
- Provide constructive feedback
- Help newcomers get started

### Research Ethics
- This tool is for defensive security research only
- Do not contribute offensive capabilities
- Follow responsible disclosure for vulnerabilities
- Respect model licenses and terms of use

### Attribution
- Credit original research and papers
- Maintain citation information
- Acknowledge contributor efforts  

## 🎯 Priority Areas

We're especially interested in contributions to:

1. **🚀 Performance Optimization**
   - Faster attention analysis algorithms
   - Memory-efficient processing for large models
   - GPU acceleration improvements

2. **🧠 New Detection Methods**
   - Novel statistical approaches
   - Multi-modal backdoor detection
   - Adversarial robustness improvements

3. **📊 Model Coverage**
   - Support for new transformer architectures
   - Non-English language model testing
   - Specialized domain models (code, science, etc.)

4. **🛠️ Usability Improvements**
   - Better visualization tools
   - Automated report generation
   - Integration with existing security tools

## 📞 Getting Help

- **Questions**: Use [GitHub Discussions](https://github.com/yourusername/llm-backdoor-scanner/discussions)
- **Issues**: Create a [GitHub Issue](https://github.com/yourusername/llm-backdoor-scanner/issues)
- **Security**: Email security@yourorganization.com for sensitive issues

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make AI systems safer! 🛡️**