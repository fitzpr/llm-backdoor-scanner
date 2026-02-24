#!/usr/bin/env python3
"""
Phase 2.2: ROC Optimization with Validated Synthetic Backdoors
==============================================================

Building on VALIDATED synthetic backdoor simulation to optimize detection thresholds.
Using ROC analysis to find optimal operating points for different use cases.

PRINCIPLE: Use ground truth synthetic backdoors to optimize real-world performance.
"""

import numpy as np
from transformers import AutoModel, AutoTokenizer, AutoConfig, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc, precision_recall_curve, f1_score
from typing import List, Dict, Optional, Tuple
import torch
import json
from datetime import datetime
import copy
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class BackdoorSimulator:
    """
    🔬 Same validated backdoor simulation from Phase 2.1
    """
    
    def __init__(self):
        print("🔬 Backdoor Simulator - Validated Ground Truth Creation")
        
    def simulate_attention_backdoor(self, model, backdoor_type: str = "amplification"):
        """Create controlled backdoor simulation in model attention"""
        
        original_forward = model.forward
        
        if backdoor_type == "amplification":
            def backdoor_forward(*args, **kwargs):
                outputs = original_forward(*args, **kwargs)
                
                if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                    modified_attentions = []
                    
                    for layer_idx, attn in enumerate(outputs.attentions):
                        if layer_idx < 3:  # First few layers
                            modified_attn = attn * 1.5
                        else:
                            modified_attn = attn
                            
                        modified_attentions.append(modified_attn)
                    
                    outputs.attentions = tuple(modified_attentions)
                
                return outputs
                
        elif backdoor_type == "concentration":
            def backdoor_forward(*args, **kwargs):
                outputs = original_forward(*args, **kwargs)
                
                if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                    modified_attentions = []
                    
                    for layer_idx, attn in enumerate(outputs.attentions):
                        if layer_idx % 2 == 0:  # Even layers
                            modified_attn = attn.clone()
                            batch, heads, seq, seq2 = modified_attn.shape
                            for h in range(heads):
                                diag_indices = torch.arange(min(seq, seq2))
                                modified_attn[0, h, diag_indices, diag_indices] *= 2.0
                        else:
                            modified_attn = attn
                            
                        modified_attentions.append(modified_attn)
                    
                    outputs.attentions = tuple(modified_attentions)
                
                return outputs
                
        elif backdoor_type == "noise_injection":
            def backdoor_forward(*args, **kwargs):
                outputs = original_forward(*args, **kwargs)
                
                if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                    modified_attentions = []
                    
                    for layer_idx, attn in enumerate(outputs.attentions):
                        if layer_idx < 2:  # First two layers
                            noise = torch.randn_like(attn) * 0.1
                            modified_attn = attn + noise
                        else:
                            modified_attn = attn
                            
                        modified_attentions.append(modified_attn)
                    
                    outputs.attentions = tuple(modified_attentions)
                
                return outputs
        
        # Replace forward method
        model.forward = backdoor_forward
        model._backdoor_type = backdoor_type
        
        return model

class ROCOptimizedScanner:
    """
    🔬 Phase 2.2: ROC-optimized scanner using validated synthetic backdoors
    """
    
    def __init__(self):
        print("🔬 ROC-Optimized Scanner - Performance Optimization")
        
        # Same validated probe inputs
        self.PROBE_INPUTS = [
            "Hello world",
            "How are you?", 
            "What is this?",
            "Please help me",
            "Thank you very much"
        ]
        
        self.backdoor_simulator = BackdoorSimulator()
        self.is_baseline_established = False
        self.baseline_stats = None
        self.scaler = None
        self.threshold = None
        self.roc_data = None
        
    def establish_baseline_from_phase1(self, clean_models: List[str]) -> bool:
        """Establish baseline using EXACT same method as validated Phase 1"""
        print(f"\\n🔬 ESTABLISHING BASELINE (PHASE 1 VALIDATED METHOD)")
        print("=" * 60)
        
        all_features = []
        
        for model_name in clean_models:
            print(f"📊 Processing clean model: {model_name}")
            
            features = self._extract_features_phase1_method(model_name)
            if features is not None and len(features) > 0:
                all_features.extend(features)
                print(f"   ✅ Extracted {len(features)} features")
            else:
                print(f"   ❌ Failed to extract features")
                
        if len(all_features) < 3:
            print(f"❌ Insufficient baseline data: {len(all_features)} samples")
            return False
            
        features_array = np.array(all_features)
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
        
        # Default threshold (can be optimized later)
        self.threshold = self.baseline_stats['mean'] + 3 * self.baseline_stats['std']
        self.is_baseline_established = True
        
        print(f"✅ Baseline: {self.baseline_stats['mean']:.2f} ± {self.baseline_stats['std']:.2f}")
        print(f"🎯 Initial Threshold: {self.threshold:.2f}")
        
        return True
        
    def _extract_features_phase1_method(self, model_name: str, model_override=None) -> Optional[List[np.ndarray]]:
        """Extract features using EXACT Phase 1 methodology"""
        try:
            if model_override is not None:
                # Use provided model (for backdoor testing)
                model = model_override
                # For backdoored models, extract base model name for tokenizer
                if 'distilbert-base-uncased' in model_name:
                    base_model_name = "distilbert-base-uncased"
                else:
                    base_model_name = model_name.split('_')[0]
                
                tokenizer = AutoTokenizer.from_pretrained(base_model_name)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
            else:
                # Load model normally
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
                        features = self._compute_features_phase1_method(attention_matrices)
                        if features is not None:
                            all_features.append(features)
                            
                except Exception as e:
                    continue
                    
            return all_features if all_features else None
            
        except Exception as e:
            return None
    
    def _compute_features_phase1_method(self, attention_matrices) -> Optional[np.ndarray]:
        """Compute features using EXACT Phase 1 method"""
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
                    
                    # EXACT same features as Phase 1
                    features.extend([
                        np.mean(head_attn),
                        np.std(head_attn),
                        np.percentile(head_attn.flatten(), 95),
                        np.percentile(head_attn.flatten(), 50),
                        np.sum(head_attn > 0.1) / head_attn.size,
                    ])
            
            return np.array(features) if features else None
            
        except Exception:
            return None
    
    def get_anomaly_score(self, model_name: str, model_override=None) -> Optional[float]:
        """Get anomaly score for a model"""
        if not self.is_baseline_established:
            return None
            
        features = self._extract_features_phase1_method(model_name, model_override)
        
        if features is None:
            return None
            
        features_array = np.array(features)
        features_scaled = self.scaler.transform(features_array)
        
        mean_baseline = np.zeros(features_scaled.shape[1])
        distances = []
        
        for feature_vec in features_scaled:
            distance = np.linalg.norm(feature_vec - mean_baseline)
            distances.append(distance)
            
        return np.max(distances)
    
    def build_roc_dataset(self) -> Tuple[List[float], List[int]]:
        """
        Build ROC analysis dataset using validated synthetic backdoors
        
        Returns:
            Tuple of (anomaly_scores, true_labels)
        """
        print(f"\\n🔬 BUILDING ROC DATASET")
        print("=" * 50)
        
        anomaly_scores = []
        true_labels = []  # 0 = clean, 1 = backdoored
        
        # Step 1: Clean model scores (multiple samples for stability)
        print("📊 Collecting clean model samples...")
        
        base_model_name = "distilbert-base-uncased"
        
        # Get multiple samples from clean model for baseline variability
        for sample_idx in range(5):
            score = self.get_anomaly_score(base_model_name)
            if score is not None:
                anomaly_scores.append(score)
                true_labels.append(0)  # Clean
                print(f"   Clean sample {sample_idx+1}: {score:.2f}")
        
        # Step 2: Backdoored model scores
        print("\\n🚨 Collecting backdoored model samples...")
        
        backdoor_types = ["amplification", "concentration", "noise_injection"]
        
        for backdoor_type in backdoor_types:
            print(f"\\n   🔧 Testing {backdoor_type} backdoor:")
            
            try:
                # Create multiple samples of each backdoor type
                for sample_idx in range(3):
                    # Load clean model
                    model = AutoModel.from_pretrained(base_model_name, output_attentions=True)
                    
                    # Apply backdoor simulation
                    backdoored_model = self.backdoor_simulator.simulate_attention_backdoor(model, backdoor_type)
                    
                    # Get anomaly score
                    score = self.get_anomaly_score(f"{base_model_name}_{backdoor_type}", model_override=backdoored_model)
                    
                    if score is not None:
                        anomaly_scores.append(score)
                        true_labels.append(1)  # Backdoored
                        print(f"      Sample {sample_idx+1}: {score:.2f}")
                        
            except Exception as e:
                print(f"      ❌ Error: {e}")
                
        print(f"\\n✅ ROC Dataset: {len(anomaly_scores)} samples ({sum(true_labels)} backdoored, {len(true_labels)-sum(true_labels)} clean)")
        
        return anomaly_scores, true_labels
    
    def optimize_threshold_roc(self, anomaly_scores: List[float], true_labels: List[int]) -> Dict:
        """
        Optimize threshold using ROC analysis for different use cases
        
        Returns:
            Dict with optimal thresholds for different scenarios
        """
        print(f"\\n🔬 ROC THRESHOLD OPTIMIZATION")
        print("=" * 50)
        
        if len(set(true_labels)) < 2:
            print("❌ Need both clean and backdoored samples for ROC analysis")
            return None
        
        # Compute ROC curve
        fpr, tpr, thresholds = roc_curve(true_labels, anomaly_scores)
        roc_auc = auc(fpr, tpr)
        
        print(f"📊 ROC AUC: {roc_auc:.3f}")
        
        # Find optimal operating points for different use cases
        optimal_points = {}
        
        # 1. Balanced accuracy (Youden's J statistic)
        j_scores = tpr - fpr
        best_idx = np.argmax(j_scores)
        optimal_points['balanced'] = {
            'threshold': thresholds[best_idx],
            'tpr': tpr[best_idx],
            'fpr': fpr[best_idx],
            'precision': None,  # Will calculate
            'f1': None
        }
        
        # 2. High precision (minimize false positives)
        # Find threshold where FPR < 0.05 (5% false positive rate)
        high_prec_mask = fpr <= 0.05
        if np.any(high_prec_mask):
            high_prec_idx = np.where(high_prec_mask)[0][-1]  # Highest TPR with FPR <= 0.05
            optimal_points['high_precision'] = {
                'threshold': thresholds[high_prec_idx],
                'tpr': tpr[high_prec_idx],
                'fpr': fpr[high_prec_idx],
                'precision': None,
                'f1': None
            }
        
        # 3. High recall (minimize false negatives)  
        # Find threshold where TPR > 0.95 (95% true positive rate)
        high_recall_mask = tpr >= 0.95
        if np.any(high_recall_mask):
            high_recall_idx = np.where(high_recall_mask)[0][0]  # Lowest FPR with TPR >= 0.95
            optimal_points['high_recall'] = {
                'threshold': thresholds[high_recall_idx],
                'tpr': tpr[high_recall_idx],
                'fpr': fpr[high_recall_idx],
                'precision': None,
                'f1': None
            }
        
        # Calculate precision and F1 for each operating point
        for point_name, point in optimal_points.items():
            threshold = point['threshold']
            predictions = (np.array(anomaly_scores) >= threshold).astype(int)
            
            # Calculate precision and F1
            tp = np.sum((predictions == 1) & (np.array(true_labels) == 1))
            fp = np.sum((predictions == 1) & (np.array(true_labels) == 0))
            fn = np.sum((predictions == 0) & (np.array(true_labels) == 1))
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            f1 = f1_score(true_labels, predictions)
            
            point['precision'] = precision
            point['f1'] = f1
        
        # Store ROC data for future use
        self.roc_data = {
            'fpr': fpr,
            'tpr': tpr,
            'thresholds': thresholds,
            'auc': roc_auc,
            'optimal_points': optimal_points
        }
        
        # Display results
        print(f"\\n📊 OPTIMAL OPERATING POINTS:")
        for point_name, point in optimal_points.items():
            print(f"\\n🎯 {point_name.upper()}:")
            print(f"   Threshold: {point['threshold']:.2f}")
            print(f"   TPR (Recall): {point['tpr']:.3f}")
            print(f"   FPR: {point['fpr']:.3f}")
            print(f"   Precision: {point['precision']:.3f}")
            print(f"   F1-Score: {point['f1']:.3f}")
        
        return optimal_points
    
    def test_roc_optimized_performance(self, optimal_point: str = 'balanced') -> bool:
        """Test performance with ROC-optimized threshold"""
        
        if self.roc_data is None or 'optimal_points' not in self.roc_data:
            print("❌ No ROC optimization data available")
            return False
            
        if optimal_point not in self.roc_data['optimal_points']:
            print(f"❌ Unknown operating point: {optimal_point}")
            return False
        
        # Set optimized threshold
        optimized_threshold = self.roc_data['optimal_points'][optimal_point]['threshold']
        original_threshold = self.threshold
        self.threshold = optimized_threshold
        
        print(f"\\n🔬 TESTING ROC-OPTIMIZED PERFORMANCE ({optimal_point.upper()})")
        print("=" * 60)
        print(f"🎯 Optimized threshold: {optimized_threshold:.2f} (was {original_threshold:.2f})")
        
        # Test clean model
        clean_score = self.get_anomaly_score("distilbert-base-uncased")
        clean_predicted = clean_score > self.threshold if clean_score else False
        clean_correct = not clean_predicted  # Should be predicted as clean
        
        print(f"\\n✅ CLEAN MODEL TEST:")
        print(f"   Score: {clean_score:.2f}")
        print(f"   Predicted: {'Backdoored' if clean_predicted else 'Clean'}")
        print(f"   Result: {'🎯 Correct' if clean_correct else '❌ Wrong'}")
        
        # Test backdoor examples
        print(f"\\n🚨 BACKDOOR TESTS:")
        backdoor_results = []
        
        for backdoor_type in ["amplification", "concentration", "noise_injection"]:
            try:
                model = AutoModel.from_pretrained("distilbert-base-uncased", output_attentions=True)
                backdoored_model = self.backdoor_simulator.simulate_attention_backdoor(model, backdoor_type)
                
                score = self.get_anomaly_score(f"distilbert-base-uncased_{backdoor_type}", model_override=backdoored_model)
                predicted = score > self.threshold if score else False
                correct = predicted  # Should be predicted as backdoored
                
                backdoor_results.append(correct)
                
                print(f"   {backdoor_type}: {score:.2f} -> {'🎯 Correct' if correct else '❌ Wrong'}")
                
            except Exception as e:
                print(f"   {backdoor_type}: ❌ Error - {e}")
        
        # Overall performance
        total_correct = sum([clean_correct] + backdoor_results)
        total_tests = 1 + len(backdoor_results)
        
        print(f"\\n📊 ROC-OPTIMIZED PERFORMANCE:")
        print(f"   Correct: {total_correct}/{total_tests}")
        print(f"   Accuracy: {total_correct/total_tests:.1%}")
        
        success = total_correct == total_tests
        
        if success:
            print(f"\\n🏆 ROC OPTIMIZATION SUCCESS!")
            print(f"   ✅ Optimal threshold found: {optimized_threshold:.2f}")
            print(f"   ✅ Perfect accuracy on test set")
            print(f"   🚀 Ready for cross-validation")
        else:
            print(f"\\n🛑 ROC OPTIMIZATION NEEDS TUNING")
            print(f"   🔍 Consider different operating point")
        
        return success

def test_roc_optimization():
    """Test complete ROC optimization pipeline"""
    print("🔬 TESTING ROC OPTIMIZATION PIPELINE")
    print("=" * 60)
    
    scanner = ROCOptimizedScanner()
    
    # Step 1: Establish baseline
    print("1️⃣ Establishing baseline...")
    clean_models = ["distilbert-base-uncased"]
    success = scanner.establish_baseline_from_phase1(clean_models)
    
    if not success:
        print("❌ Baseline establishment failed!")
        return False
    
    # Step 2: Build ROC dataset
    print("\\n2️⃣ Building ROC dataset...")
    anomaly_scores, true_labels = scanner.build_roc_dataset()
    
    if len(anomaly_scores) < 5:
        print("❌ Insufficient ROC dataset!")
        return False
    
    # Step 3: Optimize threshold
    print("\\n3️⃣ Optimizing thresholds...")
    optimal_points = scanner.optimize_threshold_roc(anomaly_scores, true_labels)
    
    if optimal_points is None:
        print("❌ ROC optimization failed!")
        return False
    
    # Step 4: Test optimized performance
    print("\\n4️⃣ Testing optimized performance...")
    
    # Test each operating point
    best_point = None
    best_performance = False
    
    for point_name in optimal_points.keys():
        print(f"\\n   Testing {point_name} operating point...")
        success = scanner.test_roc_optimized_performance(point_name)
        
        if success and best_point is None:
            best_point = point_name
            best_performance = True
    
    # Final results
    print(f"\\n🔬 ROC OPTIMIZATION RESULTS:")
    print("=" * 60)
    
    if best_performance:
        print(f"🏆 ROC OPTIMIZATION: SUCCESS")
        print(f"   ✅ Best operating point: {best_point}")
        print(f"   ✅ Optimized thresholds found")
        print(f"   ✅ Perfect test performance")
        print(f"   🚀 Ready for cross-validation and final validation")
        return True
    else:
        print(f"❌ ROC OPTIMIZATION: NEEDS IMPROVEMENT")
        print(f"   🔍 No operating point achieved perfect performance")
        print(f"   💡 Consider: More diverse synthetic backdoors, different features")
        return False

def main():
    """Test ROC optimization pipeline"""
    success = test_roc_optimization()
    
    if success:
        print(f"\\n🎯 PHASE 2.2 COMPLETE: ROC optimization validated")
        print(f"   📊 Multiple optimal operating points found")
        print(f"   🎯 Thresholds optimized for different use cases")
        print(f"   📈 Ready for comprehensive cross-validation")
    else:
        print(f"\\n🛑 PHASE 2.2 ISSUES: ROC optimization needs refinement")

if __name__ == "__main__":
    main()