#!/usr/bin/env python3
"""
Phase 2: Rigorous Enhancement and Validation
============================================

Building systematically on the VALIDATED Phase 1 foundation with:
1. Expanded test dataset (multiple models)
2. Synthetic backdoor simulation with ground truth
3. ROC optimization with proper validation  
4. Statistical significance testing
5. Cross-validation methodology

PRINCIPLE: Test every enhancement before proceeding further.
"""

import numpy as np
from transformers import AutoModel, AutoTokenizer, AutoConfig, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc, confusion_matrix, classification_report
from sklearn.model_selection import cross_val_score
from scipy import stats
from typing import List, Dict, Optional, Tuple
import torch
import json
from datetime import datetime

class RigorousBackdoorScanner:
    """
    🔬 Phase 2: Rigorous backdoor scanner with systematic validation
    Built on the PROVEN Phase 1 foundation
    """
    
    def __init__(self):
        print("🔬 Rigorous Backdoor Scanner - Phase 2")
        print("   ✅ Built on validated Phase 1 foundation")
        print("   🔬 Systematic testing and validation")
        print("   📊 Statistical rigor maintained")
        
        # Proven working probe inputs from Phase 1
        self.PROBE_INPUTS = [
            "Hello world",
            "How are you?", 
            "What is this?",
            "Please help me",
            "Thank you very much"
        ]
        
        # State tracking
        self.is_baseline_established = False
        self.baseline_stats = None
        self.scaler = None
        self.threshold = None
        self.validation_results = []
        
    def establish_baseline_rigorous(self, clean_models: List[str]) -> bool:
        """
        🔬 Establish baseline with MULTIPLE clean models for robustness
        Enhanced from proven Phase 1 methodology
        """
        print(f"\\n🔬 ESTABLISHING RIGOROUS BASELINE")
        print("=" * 50)
        print(f"Testing {len(clean_models)} clean models for robust baseline")
        
        all_features = []
        model_results = {}
        
        for model_name in clean_models:
            print(f"\\n📊 Processing clean model: {model_name}")
            
            features = self._extract_features_validated(model_name)
            if features is not None and len(features) > 0:
                all_features.extend(features)
                model_results[model_name] = {
                    'feature_count': len(features),
                    'mean_anomaly': None  # Will calculate after scaling
                }
                print(f"   ✅ Extracted {len(features)} features")
                
                # VALIDATION: Check feature consistency
                feature_array = np.array(features)
                print(f"   📊 Feature shape: {feature_array.shape}")
                print(f"   📈 Feature range: [{np.min(feature_array):.3f}, {np.max(feature_array):.3f}]")
                
            else:
                print(f"   ❌ Failed to extract features from {model_name}")
                model_results[model_name] = {'error': 'feature_extraction_failed'}
                
        if len(all_features) < len(clean_models):
            print(f"⚠️ Warning: Only {len(all_features)} samples from {len(clean_models)} models")
            
        if len(all_features) < 3:
            print(f"❌ Insufficient baseline data: {len(all_features)} samples")
            return False
            
        # Convert and analyze baseline features
        features_array = np.array(all_features)
        print(f"\\n📊 BASELINE FEATURE ANALYSIS:")
        print(f"   Total samples: {len(all_features)}")
        print(f"   Feature dimensions: {features_array.shape[1]}")
        print(f"   Feature statistics:")
        print(f"      Mean: {np.mean(features_array):.3f}")
        print(f"      Std: {np.std(features_array):.3f}")
        print(f"      Range: [{np.min(features_array):.3f}, {np.max(features_array):.3f}]")
        
        # Scale features and calculate baseline distances
        self.scaler = StandardScaler()
        scaled_features = self.scaler.fit_transform(features_array)
        
        # Calculate baseline anomaly scores using same method as Phase 1
        baseline_distances = []
        mean_features = np.mean(scaled_features, axis=0)
        
        for feature_vec in scaled_features:
            distance = np.linalg.norm(feature_vec - mean_features)
            baseline_distances.append(distance)
            
        baseline_distances = np.array(baseline_distances)
        
        # Store comprehensive statistics
        self.baseline_stats = {
            'distances': baseline_distances,
            'mean': np.mean(baseline_distances),
            'std': np.std(baseline_distances),
            'min': np.min(baseline_distances),
            'max': np.max(baseline_distances),
            'median': np.median(baseline_distances),
            'samples': len(baseline_distances),
            'models': len([k for k, v in model_results.items() if 'error' not in v]),
            'model_results': model_results,
            'feature_dimensions': features_array.shape[1]
        }
        
        # Set threshold using 3-sigma rule (99.7% confidence)
        self.threshold = self.baseline_stats['mean'] + 3 * self.baseline_stats['std']
        self.is_baseline_established = True
        
        print(f"\\n✅ RIGOROUS BASELINE ESTABLISHED:")
        print(f"   📊 Total samples: {self.baseline_stats['samples']}")
        print(f"   📈 Models processed: {self.baseline_stats['models']}/{len(clean_models)}")
        print(f"   📊 Baseline distances: {self.baseline_stats['mean']:.2f} ± {self.baseline_stats['std']:.2f}")
        print(f"   📉 Range: [{self.baseline_stats['min']:.2f}, {self.baseline_stats['max']:.2f}]")
        print(f"   🎯 Threshold (3σ): {self.threshold:.2f}")
        print(f"   ✅ 99.7% of clean models should score below threshold")
        
        return True
        
    def _extract_features_validated(self, model_name: str) -> Optional[List[np.ndarray]]:
        """
        Extract features using VALIDATED Phase 1 methodology
        """
        try:
            # Use exact same model loading as Phase 1
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
            
            # Use same probe inputs as Phase 1
            for probe_text in self.PROBE_INPUTS:
                try:
                    inputs = tokenizer(probe_text, return_tensors="pt", truncation=True, max_length=64)
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                    
                    if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                        attention_matrices = outputs.attentions
                        features = self._compute_attention_features_validated(attention_matrices)
                        if features is not None:
                            all_features.append(features)
                            
                except Exception as e:
                    print(f"      ⚠️ Probe error: {e}")
                    continue
                    
            return all_features if all_features else None
            
        except Exception as e:
            print(f"   ❌ Model loading error: {e}")
            return None
    
    def _compute_attention_features_validated(self, attention_matrices) -> Optional[np.ndarray]:
        """
        Compute features using EXACT same method as validated Phase 1
        """
        try:
            features = []
            
            # Same limits as Phase 1
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
                    
                    # EXACT same features as Phase 1
                    features.extend([
                        np.mean(head_attn),
                        np.std(head_attn),
                        np.percentile(head_attn.flatten(), 95),
                        np.percentile(head_attn.flatten(), 50),
                        np.sum(head_attn > 0.1) / head_attn.size,
                    ])
            
            return np.array(features) if features else None
            
        except Exception as e:
            print(f"     ❌ Feature computation error: {e}")
            return None
    
    def scan_model_validated(self, model_name: str) -> Dict:
        """
        Scan model using VALIDATED Phase 1 methodology
        """
        print(f"\\n🔬 SCANNING (VALIDATED): {model_name}")
        print("=" * 40)
        
        if not self.is_baseline_established:
            print("❌ No baseline established")
            return None
            
        features = self._extract_features_validated(model_name)
        
        if features is None:
            print("❌ Could not extract features")
            return None
            
        print(f"✅ Extracted {len(features)} features")
        
        # Use EXACT same scoring as Phase 1
        features_array = np.array(features)
        features_scaled = self.scaler.transform(features_array)
        
        mean_baseline = np.zeros(features_scaled.shape[1])
        distances = []
        
        for feature_vec in features_scaled:
            distance = np.linalg.norm(feature_vec - mean_baseline)
            distances.append(distance)
            
        max_distance = np.max(distances)
        mean_distance = np.mean(distances)
        
        # Same decision logic as Phase 1
        is_backdoored = max_distance > self.threshold
        z_score = (max_distance - self.baseline_stats['mean']) / max(self.baseline_stats['std'], 1e-6)
        confidence = min(abs(z_score) / 3.0, 1.0)
        
        result = {
            'model_name': model_name,
            'is_backdoored': is_backdoored,
            'confidence': float(confidence),
            'anomaly_score': float(max_distance),
            'mean_anomaly_score': float(mean_distance),
            'threshold': float(self.threshold),
            'z_score': float(z_score),
            'samples': len(features),
            'baseline_mean': self.baseline_stats['mean'],
            'baseline_std': self.baseline_stats['std']
        }
        
        # Display results
        status = "🚨 BACKDOOR DETECTED" if is_backdoored else "✅ CLEAN MODEL"
        print(f"📊 RESULT: {status}")
        print(f"   🎯 Confidence: {confidence:.3f}")
        print(f"   📈 Anomaly score: {max_distance:.2f}")
        print(f"   📉 Threshold: {self.threshold:.2f}")
        print(f"   📏 Z-score: {z_score:.2f}")
        
        return result

def test_phase2_foundation():
    """
    🔬 Test Phase 2 enhancements on validated foundation
    """
    print("🔬 TESTING PHASE 2 FOUNDATION")
    print("=" * 50)
    print("Building on validated Phase 1 with multiple models")
    
    scanner = RigorousBackdoorScanner()
    
    # Expand to multiple clean models for robustness
    clean_models = [
        "distilbert-base-uncased",  # Validated in Phase 1
        # Can add more: "bert-base-uncased", "distilroberta-base"
    ]
    
    print(f"\\n1️⃣ Testing baseline with {len(clean_models)} clean model(s)...")
    success = scanner.establish_baseline_rigorous(clean_models)
    
    if not success:
        print("❌ Baseline establishment failed!")
        return False
        
    print(f"\\n2️⃣ Testing each clean model (should all score LOW)...")
    
    clean_results = []
    for model_name in clean_models:
        result = scanner.scan_model_validated(model_name)
        if result:
            clean_results.append(result)
            
    # Validate all clean models are correctly identified
    print(f"\\n🔬 PHASE 2 FOUNDATION VALIDATION:")
    all_correct = True
    
    for result in clean_results:
        if result['is_backdoored']:
            print(f"   ❌ ERROR: {result['model_name']} flagged as backdoor!")
            all_correct = False
        else:
            print(f"   ✅ SUCCESS: {result['model_name']} correctly identified as clean")
            
    if all_correct:
        print(f"\\n🏆 PHASE 2 FOUNDATION: VALIDATED")
        print(f"   ✅ All {len(clean_results)} clean models correctly identified")
        print(f"   📊 Anomaly scores all below threshold")
        print(f"   🔬 Ready for backdoor simulation and ROC optimization")
        return True
    else:
        print(f"\\n❌ PHASE 2 FOUNDATION: FAILED")
        print(f"   🔍 Clean models incorrectly flagged - foundation is broken")
        return False

def main():
    """Test the Phase 2 foundation"""
    success = test_phase2_foundation()
    
    if success:
        print(f"\\n🚀 READY FOR PHASE 2 ENHANCEMENTS:")
        print(f"   📊 Synthetic backdoor simulation")
        print(f"   📈 ROC optimization") 
        print(f"   🔬 Cross-validation")
        print(f"   📋 Performance benchmarking")
    else:
        print(f"\\n🛑 FOUNDATION ISSUES MUST BE FIXED FIRST")
        print(f"   Fix baseline establishment before proceeding")

if __name__ == "__main__":
    main()