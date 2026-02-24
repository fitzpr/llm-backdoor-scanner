#!/usr/bin/env python3
"""
Enhanced Production Backdoor Scanner
==================================

Integrated enhanced detection methods directly into the main scanner.
Replaces separate scripts with unified production tool.
"""

import torch
import numpy as np
from scipy.stats import pearsonr
from scipy.spatial.distance import cosine

def run_enhanced_detection(attention_matrices, enhanced_thresholds):
    """Run enhanced detection methods on attention matrices"""
    results = {
        'detection_triggered': False,
        'individual_heads': individual_head_analysis(attention_matrices, enhanced_thresholds),
        'layer_correlation': multi_layer_correlation_analysis(attention_matrices, enhanced_thresholds),
        'activation_patterns': activation_pattern_analysis(attention_matrices, enhanced_thresholds),
        'summary': {}
    }
    
    # Aggregate detection signals
    head_suspicious = results['individual_heads']['suspicious_ratio'] > enhanced_thresholds['suspicious_head_ratio']
    correlation_suspicious = results['layer_correlation']['coordination_score'] > 0.2
    pattern_suspicious = results['activation_patterns']['fingerprint_match']
    
    # Detection triggered if any enhanced method flags suspicious behavior
    results['detection_triggered'] = head_suspicious or correlation_suspicious or pattern_suspicious
    
    results['summary'] = {
        'head_analysis': head_suspicious,
        'correlation_analysis': correlation_suspicious, 
        'pattern_analysis': pattern_suspicious,
        'total_methods_triggered': sum([head_suspicious, correlation_suspicious, pattern_suspicious])
    }
    
    return results

def individual_head_analysis(attention_matrices, enhanced_thresholds):
    """Analyze individual attention heads for high concentration"""
    try:
        # Handle tensor dimensions  
        if len(attention_matrices.shape) == 5:
            layers, batch, heads, seq_len, _ = attention_matrices.shape
            attention_matrices = attention_matrices.squeeze(1)  # Remove batch dim
        else:
            layers, heads, seq_len, _ = attention_matrices.shape
        
        suspicious_heads = 0
        total_heads = layers * heads
        max_concentrations = []
        
        for layer_idx in range(layers):
            for head_idx in range(heads):
                head_attention = attention_matrices[layer_idx, head_idx]
                max_concentration = torch.max(head_attention).item()
                max_concentrations.append(max_concentration)
                
                if max_concentration > enhanced_thresholds['head_concentration']:
                    suspicious_heads += 1
        
        return {
            'suspicious_heads': suspicious_heads,
            'total_heads': total_heads,
            'suspicious_ratio': suspicious_heads / total_heads,
            'max_concentration': max(max_concentrations) if max_concentrations else 0,
            'mean_concentration': np.mean(max_concentrations) if max_concentrations else 0
        }
    except Exception as e:
        return {'error': str(e), 'suspicious_ratio': 0}

def multi_layer_correlation_analysis(attention_matrices, enhanced_thresholds):
    """Analyze correlations between attention layers"""
    try:
        # Handle tensor dimensions
        if len(attention_matrices.shape) == 5:
            attention_matrices = attention_matrices.squeeze(1)
        
        layers, heads, seq_len, _ = attention_matrices.shape
        
        # Calculate layer patterns
        layer_patterns = []
        for layer_idx in range(layers):
            layer_pattern = attention_matrices[layer_idx].flatten().detach().cpu().numpy()
            layer_patterns.append(layer_pattern)
        
        # Find high correlations
        high_correlations = 0
        total_comparisons = 0
        correlation_values = []
        
        for i in range(layers):
            for j in range(i + 1, layers):
                total_comparisons += 1
                try:
                    correlation, _ = pearsonr(layer_patterns[i], layer_patterns[j])
                    correlation_values.append(abs(correlation))
                    
                    if abs(correlation) > enhanced_thresholds['layer_correlation']:
                        high_correlations += 1
                except:
                    correlation_values.append(0)
        
        coordination_score = high_correlations / total_comparisons if total_comparisons > 0 else 0
        
        return {
            'high_correlations': high_correlations,
            'total_comparisons': total_comparisons,
            'coordination_score': coordination_score,
            'max_correlation': max(correlation_values) if correlation_values else 0
        }
    except Exception as e:
        return {'error': str(e), 'coordination_score': 0}

def activation_pattern_analysis(attention_matrices, enhanced_thresholds):
    """Check for backdoor activation patterns"""
    try:
        # Handle tensor dimensions
        if len(attention_matrices.shape) == 5:
            attention_matrices = attention_matrices.squeeze(1)
        
        # Average attention across heads and layers
        avg_attention = torch.mean(attention_matrices, dim=(0, 1)).detach().cpu().numpy()
        
        # Create pattern signature (attention distribution across sequence positions)
        if avg_attention.shape[0] >= 4:
            pattern_signature = np.array([
                np.mean(avg_attention[:avg_attention.shape[0]//4]),  # First quarter
                np.mean(avg_attention[avg_attention.shape[0]//4:avg_attention.shape[0]//2]),  # Second quarter
                np.mean(avg_attention[avg_attention.shape[0]//2:3*avg_attention.shape[0]//4]),  # Third quarter
                np.mean(avg_attention[3*avg_attention.shape[0]//4:])  # Last quarter
            ])
            
            # Expected backdoor pattern (concentration at end)
            expected_pattern = np.array([0.1, 0.1, 0.1, 0.7])
            
            # Calculate similarity
            try:
                pattern_distance = cosine(pattern_signature, expected_pattern)
                fingerprint_match = pattern_distance < enhanced_thresholds['activation_similarity']
            except:
                pattern_distance = 1.0
                fingerprint_match = False
            
            return {
                'pattern_signature': pattern_signature.tolist(),
                'pattern_distance': pattern_distance,
                'fingerprint_match': fingerprint_match
            }
        else:
            return {'error': 'Insufficient sequence length', 'fingerprint_match': False}
            
    except Exception as e:
        return {'error': str(e), 'fingerprint_match': False}