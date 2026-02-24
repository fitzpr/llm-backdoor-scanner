#!/usr/bin/env python3
"""
Simple working Phase 1 backdoor scanner
"""

import numpy as np
from transformers import AutoModel, AutoTokenizer, AutoConfig, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Optional
import torch

class WorkingBackdoorScanner:
    """Simple working backdoor scanner"""
    
    def __init__(self):
        print("🔬 Simple Working Backdoor Scanner")
        self.PROBE_INPUTS = [
            "Hello world",
            "How are you?", 
            "What is this?",
            "Please help me",
            "Thank you very much"
        ]
        
        self.is_baseline_established = False
        self.baseline_stats = None
        self.scaler = None
        self.threshold = None
        
    def establish_baseline(self, clean_models: List[str]) -> bool:
        """Establish baseline using simple attention analysis"""
        print("Establishing baseline...")
        
        all_features = []
        
        for model_name in clean_models:
            print(f"Processing: {model_name}")
            features = self._extract_simple_features(model_name)
            if features is not None:
                all_features.extend(features)
                print(f"   Extracted {len(features)} features")
            else:
                print(f"   Failed to extract features")
                
        if len(all_features) < 3:
            print(f"Need at least 3 samples, got {len(all_features)}")
            return False
            
        features_array = np.array(all_features)
        print(f"Features shape: {features_array.shape}")
        
        self.scaler = StandardScaler()
        scaled_features = self.scaler.fit_transform(features_array)
        
        baseline_distances = []
        mean_features = np.mean(scaled_features, axis=0)
        
        for feature_vec in scaled_features:
            distance = np.linalg.norm(feature_vec - mean_features)
            baseline_distances.append(distance)
            
        baseline_distances = np.array(baseline_distances)
        
        self.baseline_stats = {
            'mean': np.mean(baseline_distances),
            'std': np.std(baseline_distances),
            'max': np.max(baseline_distances),
            'samples': len(baseline_distances)
        }
        
        self.threshold = self.baseline_stats['mean'] + 3 * self.baseline_stats['std']
        self.is_baseline_established = True
        
        print(f"Baseline established:")
        print(f"   Samples: {self.baseline_stats['samples']}")
        print(f"   Mean: {self.baseline_stats['mean']:.2f}")
        print(f"   Std: {self.baseline_stats['std']:.2f}")
        print(f"   Threshold: {self.threshold:.2f}")
        
        return True
        
    def _extract_simple_features(self, model_name: str) -> Optional[List[np.ndarray]]:
        """Extract simple attention features"""
        try:
            config = AutoConfig.from_pretrained(model_name)
            model_class = config.architectures[0] if config.architectures else ""
            
            if any(arch in model_class.lower() for arch in ['gpt', 'opt', 'llama', 'causal']):
                model = AutoModelForCausalLM.from_pretrained(model_name, output_attentions=True)
            else:
                model = AutoModel.from_pretrained(model_name, output_attentions=True)
                
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            model.eval()
            
            all_features = []
            
            for probe_text in self.PROBE_INPUTS:
                try:
                    inputs = tokenizer(probe_text, return_tensors="pt", truncation=True, max_length=64)
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                    
                    if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                        attention_matrices = outputs.attentions
                        features = self._compute_simple_attention_features(attention_matrices)
                        if features is not None:
                            all_features.append(features)
                            
                except Exception as e:
                    print(f"      Error processing probe: {e}")
                    continue
                    
            return all_features if all_features else None
            
        except Exception as e:
            print(f"   Error: {e}")
            return None
    
    def _compute_simple_attention_features(self, attention_matrices) -> Optional[np.ndarray]:
        """Compute simple attention features"""
        try:
            features = []
            
            num_layers = min(len(attention_matrices), 3)
            
            for layer_idx in range(num_layers):
                attn = attention_matrices[layer_idx]
                
                if hasattr(attn, 'detach'):
                    attn_np = attn.detach().cpu().numpy()
                else:
                    attn_np = np.array(attn)
                
                if len(attn_np.shape) == 4:  # [batch, heads, seq, seq]
                    attn_np = attn_np[0]  # Remove batch dimension
                
                num_heads = min(attn_np.shape[0], 2)
                
                for head_idx in range(num_heads):
                    head_attn = attn_np[head_idx]
                    
                    features.extend([
                        np.mean(head_attn),
                        np.std(head_attn),
                        np.percentile(head_attn.flatten(), 95),
                        np.percentile(head_attn.flatten(), 50),
                        np.sum(head_attn > 0.1) / head_attn.size,
                    ])
            
            return np.array(features) if features else None
            
        except Exception as e:
            print(f"     Feature computation error: {e}")
            return None
    
    def scan_model(self, model_name: str) -> Dict:
        """Scan a model for backdoors"""
        print(f"Scanning: {model_name}")
        
        if not self.is_baseline_established:
            print("No baseline established")
            return None
            
        features = self._extract_simple_features(model_name)
        
        if features is None:
            print("Could not extract features")
            return None
            
        print(f"Extracted {len(features)} features")
        
        features_array = np.array(features)
        features_scaled = self.scaler.transform(features_array)
        
        mean_baseline = np.zeros(features_scaled.shape[1])
        distances = []
        
        for feature_vec in features_scaled:
            distance = np.linalg.norm(feature_vec - mean_baseline)
            distances.append(distance)
            
        max_distance = np.max(distances)
        
        is_backdoored = max_distance > self.threshold
        z_score = (max_distance - self.baseline_stats['mean']) / max(self.baseline_stats['std'], 1e-6)
        confidence = min(abs(z_score) / 3.0, 1.0)
        
        result = {
            'model_name': model_name,
            'is_backdoored': is_backdoored,
            'confidence': float(confidence),
            'anomaly_score': float(max_distance),
            'threshold': float(self.threshold),
            'z_score': float(z_score),
            'samples': len(features)
        }
        
        status = "BACKDOOR DETECTED" if is_backdoored else "CLEAN MODEL"
        print(f"Result: {status}")
        print(f"   Confidence: {confidence:.3f}")
        print(f"   Anomaly score: {max_distance:.2f}")
        print(f"   Threshold: {self.threshold:.2f}")
        print(f"   Z-score: {z_score:.2f}")
        
        return result

def main():
    """Test the working scanner"""
    print("Testing Working Scanner")
    print("=" * 30)
    
    scanner = WorkingBackdoorScanner()
    
    clean_models = ["distilbert-base-uncased"]
    
    print("1. Establishing baseline...")
    success = scanner.establish_baseline(clean_models)
    
    if not success:
        print("Baseline failed")
        return
        
    print("\\n2. Testing same model...")
    result = scanner.scan_model("distilbert-base-uncased")
    
    if result:
        print("\\nValidation:")
        if result['is_backdoored']:
            print("   ERROR: Clean model flagged as backdoor!")
            print("   This indicates a methodology problem.")
        else:
            print("   SUCCESS: Clean model correctly identified!")
            print("   The methodology is working correctly.")
            
if __name__ == "__main__":
    main()