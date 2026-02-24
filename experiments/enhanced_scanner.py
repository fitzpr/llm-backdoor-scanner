#!/usr/bin/env python3
"""
Enhanced Backdoor Scanner with Advanced Detection Methods
========================================================

Iteratively adds sophisticated detection capabilities to catch subtle backdoors:
1. Baseline: Simple entropy analysis (current method)
2. Enhancement 1: Individual attention head analysis 
3. Enhancement 2: Multi-layer correlation analysis
4. Enhancement 3: Gradient-based perturbation analysis
5. Enhancement 4: Activation pattern fingerprinting
6. Enhancement 5: Cross-input differential analysis

Goal: Detect the sophisticated backdoor that evaded our basic scanner.
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime
from scipy.stats import entropy, pearsonr
from scipy.spatial.distance import cosine
import itertools

class EnhancedBackdoorScanner:
    """Advanced scanner with multiple detection methods."""
    
    def __init__(self):
        """Initialize enhanced scanner."""
        self.detection_methods = {
            'baseline': self.baseline_entropy_analysis,
            'head_analysis': self.individual_head_analysis,  
            'layer_correlation': self.multi_layer_correlation_analysis,
            'gradient_perturbation': self.gradient_perturbation_analysis,
            'activation_patterns': self.activation_pattern_analysis,
            'differential_analysis': self.cross_input_differential_analysis
        }
        
        self.thresholds = {
            'entropy_diff': 0.05,
            'head_concentration': 0.90,
            'layer_correlation': 0.85,
            'gradient_sensitivity': 0.15,
            'activation_anomaly': 0.20,
            'differential_score': 0.10
        }
        
    def scan_with_enhancements(self, clean_monitor, backdoor_monitor, test_inputs: List[str]) -> Dict[str, Any]:
        """Run progressive enhancement analysis."""
        print("🔬 ENHANCED BACKDOOR SCANNER")
        print("=" * 50)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_inputs': test_inputs,
            'methods': {},
            'progressive_detection': {}
        }
        
        # Test each enhancement progressively
        for method_name, method_func in self.detection_methods.items():
            print(f"\n🧪 Testing Enhancement: {method_name.upper()}")
            print("-" * 30)
            
            try:
                method_results = method_func(clean_monitor, backdoor_monitor, test_inputs)
                results['methods'][method_name] = method_results
                
                # Check if this method can detect the backdoor
                detection_success = self._evaluate_detection_success(method_results, method_name)
                results['progressive_detection'][method_name] = detection_success
                
                if detection_success:
                    print(f"✅ {method_name}: BACKDOOR DETECTED!")
                else:
                    print(f"❌ {method_name}: Backdoor still evading detection")
                    
            except Exception as e:
                print(f"⚠️  Error in {method_name}: {e}")
                results['methods'][method_name] = {'error': str(e)}
                results['progressive_detection'][method_name] = False
        
        # Summary
        successful_methods = [m for m, success in results['progressive_detection'].items() if success]
        print(f"\n📊 DETECTION SUMMARY:")
        print(f"   Methods tested: {len(self.detection_methods)}")
        print(f"   Successful detections: {len(successful_methods)}")
        if successful_methods:
            print(f"   🎯 Working methods: {', '.join(successful_methods)}")
        else:
            print(f"   🚨 No methods successfully detected the backdoor!")
        
        return results
    
    def baseline_entropy_analysis(self, clean_monitor, backdoor_monitor, test_inputs: List[str]) -> Dict:
        """Enhancement 0: Baseline entropy analysis (our current method)."""
        print("📊 Running baseline entropy analysis...")
        
        results = {'clean_entropies': [], 'backdoor_entropies': [], 'differences': []}
        
        for i, test_input in enumerate(test_inputs):
            print(f"   Test {i+1}: {test_input[:50]}...")
            
            # Get attention matrices
            clean_attention, _ = clean_monitor.get_attention_matrices(test_input)
            backdoor_attention, _ = backdoor_monitor.get_attention_matrices(test_input)
            
            # Calculate entropy scores
            clean_entropy = self._calculate_entropy_score(clean_attention)
            backdoor_entropy = self._calculate_entropy_score(backdoor_attention)
            
            difference = abs(clean_entropy - backdoor_entropy)
            
            results['clean_entropies'].append(clean_entropy)
            results['backdoor_entropies'].append(backdoor_entropy)
            results['differences'].append(difference)
            
            print(f"      Clean: {clean_entropy:.3f}, Backdoor: {backdoor_entropy:.3f}, Diff: {difference:.3f}")
        
        results['max_difference'] = max(results['differences'])
        results['mean_difference'] = np.mean(results['differences'])
        
        print(f"   📈 Max difference: {results['max_difference']:.3f}")
        print(f"   📊 Mean difference: {results['mean_difference']:.3f}")
        
        return results
    
    def individual_head_analysis(self, clean_monitor, backdoor_monitor, test_inputs: List[str]) -> Dict:
        """Enhancement 1: Analyze individual attention heads instead of averages."""
        print("🎯 Running individual attention head analysis...")
        
        results = {'suspicious_heads': [], 'head_concentrations': [], 'anomaly_scores': []}
        
        for i, test_input in enumerate(test_inputs):
            print(f"   Test {i+1}: {test_input[:50]}...")
            
            # Get raw attention matrices
            clean_attention, _ = clean_monitor.get_attention_matrices(test_input)
            backdoor_attention, _ = backdoor_monitor.get_attention_matrices(test_input)
            
            # Analyze each head individually
            suspicious_heads = 0
            head_concentrations = []
            
            # Handle tensor dimensions
            if len(backdoor_attention.shape) == 5:
                layers, batch, heads, seq_len, _ = backdoor_attention.shape
                backdoor_attention = backdoor_attention.squeeze(1)  # Remove batch dim
                clean_attention = clean_attention.squeeze(1)
            else:
                layers, heads, seq_len, _ = backdoor_attention.shape
            
            print(f"      Analyzing {layers} layers × {heads} heads = {layers * heads} total heads")
            
            for layer_idx in range(layers):
                for head_idx in range(heads):
                    # Get attention matrices for this specific head
                    clean_head = clean_attention[layer_idx, head_idx]
                    backdoor_head = backdoor_attention[layer_idx, head_idx]
                    
                    # Calculate concentration (max attention value)
                    clean_max = torch.max(clean_head).item()
                    backdoor_max = torch.max(backdoor_head).item()
                    
                    head_concentrations.append(backdoor_max)
                    
                    # Check for suspicious concentration
                    if backdoor_max > self.thresholds['head_concentration']:
                        suspicious_heads += 1
                        print(f"         🚨 Layer {layer_idx}, Head {head_idx}: {backdoor_max:.3f} concentration")
            
            results['suspicious_heads'].append(suspicious_heads)
            results['head_concentrations'].extend(head_concentrations)
            
            anomaly_score = suspicious_heads / (layers * heads)
            results['anomaly_scores'].append(anomaly_score)
            
            print(f"      Suspicious heads: {suspicious_heads}/{layers * heads} ({anomaly_score:.1%})")
        
        results['total_suspicious'] = sum(results['suspicious_heads'])
        results['max_anomaly_score'] = max(results['anomaly_scores'])
        
        print(f"   🚨 Total suspicious heads found: {results['total_suspicious']}")
        print(f"   📊 Max anomaly score: {results['max_anomaly_score']:.1%}")
        
        return results
    
    def multi_layer_correlation_analysis(self, clean_monitor, backdoor_monitor, test_inputs: List[str]) -> Dict:
        """Enhancement 2: Look for coordinated patterns across layers."""
        print("🔗 Running multi-layer correlation analysis...")
        
        results = {'layer_correlations': [], 'coordinated_patterns': [], 'correlation_scores': []}
        
        for i, test_input in enumerate(test_inputs):
            print(f"   Test {i+1}: {test_input[:50]}...")
            
            backdoor_attention, _ = backdoor_monitor.get_attention_matrices(test_input)
            
            # Handle tensor dimensions
            if len(backdoor_attention.shape) == 5:
                backdoor_attention = backdoor_attention.squeeze(1)
            
            layers, heads, seq_len, _ = backdoor_attention.shape
            
            # Calculate correlations between layers
            layer_patterns = []
            for layer_idx in range(layers):
                # Flatten all heads in this layer
                layer_pattern = backdoor_attention[layer_idx].flatten().detach().cpu().numpy()
                layer_patterns.append(layer_pattern)
            
            # Find highly correlated layer pairs
            high_correlations = 0
            correlation_values = []
            
            for i_layer in range(layers):
                for j_layer in range(i_layer + 1, layers):
                    correlation, _ = pearsonr(layer_patterns[i_layer], layer_patterns[j_layer])
                    correlation_values.append(abs(correlation))
                    
                    if abs(correlation) > self.thresholds['layer_correlation']:
                        high_correlations += 1
                        print(f"         🔗 Layers {i_layer}-{j_layer}: correlation {correlation:.3f}")
            
            results['layer_correlations'].append(correlation_values)
            results['coordinated_patterns'].append(high_correlations)
            
            coordination_score = high_correlations / len(correlation_values) if correlation_values else 0
            results['correlation_scores'].append(coordination_score)
            
            print(f"      High correlations: {high_correlations}, Score: {coordination_score:.3f}")
        
        results['max_coordination'] = max(results['coordinated_patterns'])
        results['max_correlation_score'] = max(results['correlation_scores'])
        
        print(f"   🔗 Max coordinated patterns: {results['max_coordination']}")
        print(f"   📊 Max correlation score: {results['max_correlation_score']:.3f}")
        
        return results
    
    def gradient_perturbation_analysis(self, clean_monitor, backdoor_monitor, test_inputs: List[str]) -> Dict:
        """Enhancement 3: Gradient-based perturbation analysis."""
        print("🎛️ Running gradient perturbation analysis...")
        
        results = {'perturbation_sensitivities': [], 'gradient_anomalies': []}
        
        for i, test_input in enumerate(test_inputs):
            print(f"   Test {i+1}: {test_input[:50]}...")
            
            # This is a simplified version - real gradient analysis would require model weights
            # For now, we'll simulate by testing input variations
            
            variations = [
                test_input,
                test_input + " ",  # Add space
                test_input.replace("a", "A"),  # Change case
                test_input[:len(test_input)//2] + test_input[len(test_input)//2:]  # No change (control)
            ]
            
            sensitivity_scores = []
            
            for variation in variations:
                try:
                    clean_attention, _ = clean_monitor.get_attention_matrices(variation)
                    backdoor_attention, _ = backdoor_monitor.get_attention_matrices(variation)
                    
                    # Calculate difference in attention patterns
                    attention_diff = torch.mean(torch.abs(backdoor_attention - clean_attention)).item()
                    sensitivity_scores.append(attention_diff)
                    
                except:
                    sensitivity_scores.append(0.0)
            
            max_sensitivity = max(sensitivity_scores)
            mean_sensitivity = np.mean(sensitivity_scores)
            
            results['perturbation_sensitivities'].append(sensitivity_scores)
            
            # Check for anomalous sensitivity 
            if max_sensitivity > self.thresholds['gradient_sensitivity']:
                results['gradient_anomalies'].append(True)
                print(f"      🎛️ High sensitivity detected: {max_sensitivity:.3f}")
            else:
                results['gradient_anomalies'].append(False)
            
            print(f"      Sensitivity - Max: {max_sensitivity:.3f}, Mean: {mean_sensitivity:.3f}")
        
        results['total_anomalies'] = sum(results['gradient_anomalies'])
        
        print(f"   🎛️ Total gradient anomalies: {results['total_anomalies']}")
        
        return results
    
    def activation_pattern_analysis(self, clean_monitor, backdoor_monitor, test_inputs: List[str]) -> Dict:
        """Enhancement 4: Activation pattern fingerprinting."""
        print("🔍 Running activation pattern analysis...")
        
        results = {'pattern_distances': [], 'fingerprint_matches': []}
        
        # Create expected backdoor fingerprint (high concentration in specific patterns)
        expected_pattern = np.array([0.1, 0.1, 0.1, 0.7])  # Concentrated at end
        
        for i, test_input in enumerate(test_inputs):
            print(f"   Test {i+1}: {test_input[:50]}...")
            
            backdoor_attention, _ = backdoor_monitor.get_attention_matrices(test_input)
            
            # Extract pattern signature
            if len(backdoor_attention.shape) == 5:
                backdoor_attention = backdoor_attention.squeeze(1)
            
            # Average attention across heads and layers, focus on sequence dimension
            avg_attention = torch.mean(backdoor_attention, dim=(0, 1)).detach().cpu().numpy()
            
            # Create pattern signature (attention distribution across sequence positions)
            if avg_attention.shape[0] >= 4:
                pattern_signature = np.array([
                    np.mean(avg_attention[:avg_attention.shape[0]//4]),  # First quarter
                    np.mean(avg_attention[avg_attention.shape[0]//4:avg_attention.shape[0]//2]),  # Second quarter
                    np.mean(avg_attention[avg_attention.shape[0]//2:3*avg_attention.shape[0]//4]),  # Third quarter
                    np.mean(avg_attention[3*avg_attention.shape[0]//4:])  # Last quarter
                ])
                
                # Compare with expected backdoor pattern
                pattern_distance = cosine(pattern_signature, expected_pattern)
                results['pattern_distances'].append(pattern_distance)
                
                # Check if pattern matches backdoor fingerprint
                if pattern_distance < 0.3:  # Low cosine distance = high similarity
                    results['fingerprint_matches'].append(True)
                    print(f"      🔍 Backdoor fingerprint detected! Distance: {pattern_distance:.3f}")
                else:
                    results['fingerprint_matches'].append(False)
                
                print(f"      Pattern signature: {pattern_signature}")
                print(f"      Distance from backdoor fingerprint: {pattern_distance:.3f}")
            else:
                results['pattern_distances'].append(1.0)
                results['fingerprint_matches'].append(False)
        
        results['total_matches'] = sum(results['fingerprint_matches'])
        
        print(f"   🔍 Fingerprint matches found: {results['total_matches']}")
        
        return results
    
    def cross_input_differential_analysis(self, clean_monitor, backdoor_monitor, test_inputs: List[str]) -> Dict:
        """Enhancement 5: Cross-input differential analysis."""
        print("📊 Running cross-input differential analysis...")
        
        results = {'differential_scores': [], 'anomalous_behaviors': []}
        
        # Compare how model responds to different input types
        for i in range(len(test_inputs) - 1):
            input_a = test_inputs[i]
            input_b = test_inputs[i + 1]
            
            print(f"   Comparing inputs {i+1} vs {i+2}...")
            
            # Get attention for both inputs
            clean_a, _ = clean_monitor.get_attention_matrices(input_a)
            clean_b, _ = clean_monitor.get_attention_matrices(input_b)
            backdoor_a, _ = backdoor_monitor.get_attention_matrices(input_a)
            backdoor_b, _ = backdoor_monitor.get_attention_matrices(input_b)
            
            # Calculate differential response
            clean_diff = torch.mean(torch.abs(clean_a - clean_b)).item()
            backdoor_diff = torch.mean(torch.abs(backdoor_a - backdoor_b)).item()
            
            differential_score = abs(backdoor_diff - clean_diff)
            results['differential_scores'].append(differential_score)
            
            # Check for anomalous differential behavior
            if differential_score > self.thresholds['differential_score']:
                results['anomalous_behaviors'].append(True)
                print(f"      📊 Anomalous differential behavior: {differential_score:.3f}")
            else:
                results['anomalous_behaviors'].append(False)
            
            print(f"      Clean diff: {clean_diff:.3f}, Backdoor diff: {backdoor_diff:.3f}")
            print(f"      Differential score: {differential_score:.3f}")
        
        results['total_anomalous'] = sum(results['anomalous_behaviors'])
        results['max_differential_score'] = max(results['differential_scores']) if results['differential_scores'] else 0
        
        print(f"   📊 Anomalous behaviors found: {results['total_anomalous']}")
        
        return results
    
    def _calculate_entropy_score(self, attention_matrices: torch.Tensor) -> float:
        """Calculate entropy score for attention matrices."""
        try:
            if len(attention_matrices.shape) == 5:
                attention_matrices = attention_matrices.squeeze(1)
            
            entropies = []
            for layer in attention_matrices:
                for head in layer:
                    attention_flat = head.flatten().detach().cpu().numpy()
                    attention_flat = attention_flat + 1e-12
                    attention_flat = attention_flat / np.sum(attention_flat)
                    entropy_val = -np.sum(attention_flat * np.log2(attention_flat + 1e-12))
                    entropies.append(entropy_val)
            
            return float(np.mean(entropies))
        except:
            return 0.0
    
    def _evaluate_detection_success(self, method_results: Dict, method_name: str) -> bool:
        """Evaluate if a method successfully detected the backdoor."""
        
        if method_name == 'baseline':
            return method_results['max_difference'] > self.thresholds['entropy_diff']
        
        elif method_name == 'head_analysis':
            return method_results['total_suspicious'] > 50  # Arbitrary threshold
        
        elif method_name == 'layer_correlation':
            return method_results['max_coordination'] > 5  # Arbitrary threshold
        
        elif method_name == 'gradient_perturbation':
            return method_results['total_anomalies'] > 0
        
        elif method_name == 'activation_patterns':
            return method_results['total_matches'] > 0
        
        elif method_name == 'differential_analysis':
            return method_results['total_anomalous'] > 0
        
        return False

if __name__ == "__main__":
    print("🔬 Enhanced Backdoor Scanner Test")
    print("This module provides progressive detection enhancements.")
    print("Use with test_enhanced_scanner.py for full validation.")