"""
Sample model loading utilities for testing backdoor detection.

This module provides helpful functions for loading and testing different
types of models with the backdoor scanner.
"""

from typing import List, Dict, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelLoader:
    """Utility class for loading different models for testing."""
    
    # Common models sorted by computational requirements
    LIGHTWEIGHT_MODELS = [
        "gpt2",                      # 124M params - very fast
        "microsoft/DialoGPT-small",  # 117M params - chat model
        "distilgpt2",               # 82M params - smaller GPT-2
    ]
    
    MEDIUM_MODELS = [
        "gpt2-medium",              # 355M params - requires more RAM
        "microsoft/DialoGPT-medium", # 345M params - larger chat model
        "meta-llama/Llama-3.2-1B", # 1B params - needs good GPU
    ]
    
    LARGE_MODELS = [
        "gpt2-large",               # 774M params - significant GPU memory
        "meta-llama/Llama-3.2-3B", # 3B params - high-end GPU required
        "microsoft/DialoGPT-large", # 762M params - large chat model
    ]
    
    @classmethod
    def get_recommended_models(cls, hardware_tier: str = "cpu") -> List[str]:
        """
        Get recommended models based on hardware capabilities.
        
        Args:
            hardware_tier: "cpu", "gpu_basic", or "gpu_advanced"
            
        Returns:
            List of recommended model names
        """
        if hardware_tier == "cpu":
            return cls.LIGHTWEIGHT_MODELS
        elif hardware_tier == "gpu_basic":
            return cls.LIGHTWEIGHT_MODELS + cls.MEDIUM_MODELS[:1] 
        elif hardware_tier == "gpu_advanced":
            return cls.LIGHTWEIGHT_MODELS + cls.MEDIUM_MODELS
        else:
            return cls.LIGHTWEIGHT_MODELS
    
    @classmethod
    def load_model_safe(cls, model_name: str, device: str = "auto") -> tuple:
        """
        Safely load a model with error handling.
        
        Args:
            model_name: HuggingFace model name
            device: Target device
            
        Returns:
            Tuple of (model, tokenizer) or (None, None) if failed
        """
        try:
            print(f"Loading {model_name}...")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                output_attentions=True,
                torch_dtype=torch.float32,
                device_map=device if device != "auto" else None
            )
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            print(f"✅ Successfully loaded {model_name}")
            return model, tokenizer
            
        except Exception as e:
            print(f"❌ Failed to load {model_name}: {e}")
            return None, None
    
    @classmethod
    def estimate_memory_usage(cls, model_name: str) -> Dict[str, str]:
        """
        Estimate memory requirements for a model.
        
        Args:
            model_name: HuggingFace model name
            
        Returns:
            Dictionary with memory estimates
        """
        # Rough estimates based on model sizes
        memory_estimates = {
            "gpt2": {"ram": "1-2 GB", "vram": "1 GB", "tier": "Lightweight"},
            "distilgpt2": {"ram": "1 GB", "vram": "0.5 GB", "tier": "Lightweight"},
            "gpt2-medium": {"ram": "2-3 GB", "vram": "2 GB", "tier": "Medium"},
            "gpt2-large": {"ram": "4-5 GB", "vram": "4 GB", "tier": "Large"},
            "microsoft/DialoGPT-small": {"ram": "1-2 GB", "vram": "1 GB", "tier": "Lightweight"},
            "microsoft/DialoGPT-medium": {"ram": "2-3 GB", "vram": "2 GB", "tier": "Medium"},
            "microsoft/DialoGPT-large": {"ram": "4-5 GB", "vram": "4 GB", "tier": "Large"},
            "meta-llama/Llama-3.2-1B": {"ram": "3-4 GB", "vram": "3 GB", "tier": "Medium"},
            "meta-llama/Llama-3.2-3B": {"ram": "8-12 GB", "vram": "8 GB", "tier": "Large"},
        }
        
        return memory_estimates.get(model_name, {
            "ram": "Unknown", 
            "vram": "Unknown", 
            "tier": "Unknown"
        })

def check_system_capabilities() -> Dict[str, str]:
    """
    Check system capabilities for model testing.
    
    Returns:
        Dictionary with system information
    """
    capabilities = {}
    
    # Check PyTorch and CUDA
    capabilities['pytorch_version'] = torch.__version__
    capabilities['cuda_available'] = torch.cuda.is_available()
    
    if torch.cuda.is_available():
        capabilities['cuda_version'] = torch.version.cuda
        capabilities['gpu_count'] = torch.cuda.device_count()
        capabilities['gpu_name'] = torch.cuda.get_device_name(0)
        
        # Check GPU memory
        total_memory = torch.cuda.get_device_properties(0).total_memory
        capabilities['gpu_memory_gb'] = round(total_memory / (1024**3), 1)
        
        # Recommend hardware tier
        if capabilities['gpu_memory_gb'] >= 8:
            capabilities['recommended_tier'] = "gpu_advanced"
        elif capabilities['gpu_memory_gb'] >= 4:
            capabilities['recommended_tier'] = "gpu_basic" 
        else:
            capabilities['recommended_tier'] = "cpu"
    else:
        capabilities['recommended_tier'] = "cpu"
    
    return capabilities

def print_system_info():
    """Print system capabilities and model recommendations."""
    info = check_system_capabilities()
    
    print("🖥️  System Information:")
    print("=" * 40)
    print(f"PyTorch Version: {info['pytorch_version']}")
    print(f"CUDA Available: {info['cuda_available']}")
    
    if info['cuda_available']:
        print(f"CUDA Version: {info['cuda_version']}")
        print(f"GPU Count: {info['gpu_count']}")
        print(f"GPU Name: {info['gpu_name']}")
        print(f"GPU Memory: {info['gpu_memory_gb']} GB")
    
    print(f"Recommended Tier: {info['recommended_tier']}")
    
    # Show recommended models
    recommended = ModelLoader.get_recommended_models(info['recommended_tier'])
    print(f"\n📋 Recommended Models for Your System:")
    for i, model in enumerate(recommended, 1):
        memory_info = ModelLoader.estimate_memory_usage(model)
        print(f"{i}. {model} ({memory_info['tier']} - ~{memory_info['ram']} RAM)")

def batch_test_models(model_names: List[str], 
                     scanner_class,
                     quick_scan: bool = True) -> Dict[str, Dict]:
    """
    Test multiple models with the backdoor scanner.
    
    Args:
        model_names: List of model names to test
        scanner_class: BackdoorScanner class
        quick_scan: Whether to use quick scan (True) or full scan (False)
        
    Returns:
        Dictionary mapping model names to their scan results
    """
    results = {}
    
    print(f"🔍 Batch testing {len(model_names)} models...")
    print("=" * 50)
    
    for i, model_name in enumerate(model_names, 1):
        print(f"\n[{i}/{len(model_names)}] Testing {model_name}...")
        
        try:
            # Initialize scanner
            scanner = scanner_class(model_name)
            
            # Run scan
            if quick_scan:
                scan_result = scanner.quick_scan()
            else:
                scan_result = scanner.full_scan()
            
            results[model_name] = {
                'success': True,
                'result': scan_result,
                'error': None
            }
            
            print(f"✅ {model_name}: {scan_result}")
            
        except Exception as e:
            results[model_name] = {
                'success': False,
                'result': None, 
                'error': str(e)
            }
            print(f"❌ {model_name}: Error - {e}")
    
    # Summary
    successful = sum(1 for r in results.values() if r['success'])
    print(f"\n📊 Batch Test Summary:")
    print(f"Successful: {successful}/{len(model_names)}")
    print(f"Failed: {len(model_names) - successful}/{len(model_names)}")
    
    return results

def create_model_comparison_report(batch_results: Dict[str, Dict], 
                                 output_file: str = "model_comparison.md"):
    """
    Create a comparison report for multiple model scans.
    
    Args:
        batch_results: Results from batch_test_models()
        output_file: Output filename for the report
    """
    report = "# Model Comparison Report\n\n"
    
    # Summary table
    report += "## Summary\n\n"
    report += "| Model | Status | Backdoor Detected | Confidence | Top Suspicious Token |\n"
    report += "|-------|--------|-------------------|------------|----------------------|\n"
    
    for model_name, result_info in batch_results.items():
        if result_info['success']:
            result = result_info['result']
            status = "✅"
            backdoor = "🔴 Yes" if result.is_backdoored else "🟢 No"
            confidence = f"{result.confidence:.1%}"
            top_token = result.suspicious_tokens[0]['token'] if result.suspicious_tokens else "None"
        else:
            status = "❌"
            backdoor = "Error"
            confidence = "N/A"
            top_token = "N/A"
        
        report += f"| {model_name} | {status} | {backdoor} | {confidence} | {top_token} |\n"
    
    # Detailed results
    report += "\n## Detailed Results\n\n"
    
    for model_name, result_info in batch_results.items():
        report += f"### {model_name}\n\n"
        
        if result_info['success']:
            result = result_info['result']
            report += f"- **Status**: {'🔴 BACKDOORED' if result.is_backdoored else '🟢 CLEAN'}\n"
            report += f"- **Confidence**: {result.confidence:.1%}\n"
            report += f"- **Suspicious Tokens**: {len(result.suspicious_tokens)}\n"
            
            if result.suspicious_tokens:
                report += f"- **Top Suspicious Tokens**:\n"
                for token_info in result.suspicious_tokens[:3]:
                    report += f"  - `{token_info['token']}` (Score: {token_info['suspicion_score']:.3f})\n"
        else:
            report += f"- **Error**: {result_info['error']}\n"
        
        report += "\n"
    
    # Save report
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Model comparison report saved to {output_file}")

# Example usage functions
def run_lightweight_comparison():
    """Run comparison on lightweight models suitable for most hardware."""
    from scanner import BackdoorScanner
    
    lightweight_models = ModelLoader.LIGHTWEIGHT_MODELS
    print("🏃‍♂️ Running lightweight model comparison...")
    
    results = batch_test_models(lightweight_models, BackdoorScanner, quick_scan=True)
    create_model_comparison_report(results)
    
    return results

def run_system_appropriate_test():
    """Run test appropriate for the current system hardware.""" 
    from scanner import BackdoorScanner
    
    # Check system and get appropriate models
    capabilities = check_system_capabilities()
    recommended_models = ModelLoader.get_recommended_models(capabilities['recommended_tier'])
    
    print(f"🎯 Running tests appropriate for {capabilities['recommended_tier']} hardware...")
    
    results = batch_test_models(recommended_models, BackdoorScanner, quick_scan=True)
    create_model_comparison_report(results)
    
    return results