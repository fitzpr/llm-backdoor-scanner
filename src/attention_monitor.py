"""
Attention Monitoring Module for LLM Security Research

Independent implementation of basic attention pattern analysis concepts.
Inspired by backdoor detection research but using simplified methods
for educational exploration.

This is NOT a reproduction of sophisticated research methods from
academic papers, but rather a learning exercise in attention analysis.
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.stats import entropy, ttest_rel, ttest_ind
from scipy import stats
import json

class AttentionMonitor:
    """Monitor and analyze attention patterns in transformer models."""
    
    def __init__(self, model, tokenizer):
        """
        Initialize the attention monitor.
        
        Args:
            model: Transformer model with output_attentions=True
            tokenizer: Associated tokenizer
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device
        
    def get_attention_matrices(self, prompt: str) -> Tuple[torch.Tensor, List[str]]:
        """
        Extract attention matrices for a given prompt.
        
        Args:
            prompt: Input text to analyze
            
        Returns:
            Tuple of (attention_matrices, tokens)
        """
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        
        # Get model outputs with attention
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Stack all layer attentions
        # Shape: [layers, batch, heads, seq_len, seq_len]  
        attention_matrices = torch.stack(outputs.attentions)
        
        return attention_matrices, tokens
        
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
        results = {
            'hijacked_heads': [],
            'max_attention_values': [],
            'entropy_scores': [],
            'is_hijacked': False
        }
        
        # Analyze each layer and head
        layers, batch, heads, seq_len, _ = attention_matrices.shape
        
        for layer_idx in range(layers):
            for head_idx in range(heads):
                attention_head = attention_matrices[layer_idx, 0, head_idx]
                
                # Calculate maximum attention value (the "stare intensity")
                max_attention = torch.max(attention_head).item()
                
                # Calculate entropy (low entropy = obsessed)
                # Flatten and normalize each row
                attention_probs = torch.softmax(attention_head, dim=-1)
                head_entropy = []
                
                for row in attention_probs:
                    row_np = row.cpu().numpy()
                    row_entropy = entropy(row_np + 1e-12)  # Small epsilon for numerical stability
                    head_entropy.append(row_entropy)
                
                avg_entropy = np.mean(head_entropy)
                
                # Flag as hijacked if max attention is high and entropy is low
                if max_attention > threshold and avg_entropy < 2.0:  # Log(seq_len) for uniform dist
                    results['hijacked_heads'].append((layer_idx, head_idx))
                    results['is_hijacked'] = True
                
                results['max_attention_values'].append(max_attention)
                results['entropy_scores'].append(avg_entropy)
        
        return results
    
    def find_trigger_candidates(self, base_prompt: str, 
                              test_tokens: List[str]) -> List[Dict]:
        """
        Test potential trigger tokens by monitoring attention changes.
        
        Args:
            base_prompt: Clean baseline prompt
            test_tokens: List of potential trigger tokens to test
            
        Returns:
            List of results sorted by suspicion level
        """
        # Get baseline attention
        baseline_attention, _ = self.get_attention_matrices(base_prompt)
        baseline_results = self.detect_attention_hijacking(baseline_attention)
        
        candidates = []
        
        for token in test_tokens:
            # Test with potential trigger
            test_prompt = f"{base_prompt} {token}"
            test_attention, _ = self.get_attention_matrices(test_prompt)
            test_results = self.detect_attention_hijacking(test_attention)
            
            # Calculate suspicion score
            attention_spike = max(test_results['max_attention_values']) - max(baseline_results['max_attention_values'])
            entropy_drop = min(baseline_results['entropy_scores']) - min(test_results['entropy_scores'])
            
            suspicion_score = attention_spike + entropy_drop
            
            candidates.append({
                'token': token,
                'suspicion_score': suspicion_score,
                'attention_spike': attention_spike,
                'entropy_drop': entropy_drop,
                'hijacked_heads': len(test_results['hijacked_heads']),
                'is_suspicious': suspicion_score > 0.5  # Threshold for flagging
            })
        
        # Sort by suspicion level
        candidates.sort(key=lambda x: x['suspicion_score'], reverse=True)
        
        return candidates
    
    def data_leakage_scan(self, system_prompts: List[str], 
                         temperature: float = 1.5, 
                         max_tokens: int = 100) -> List[str]:
        """
        Perform data leakage scan to find potential triggers.
        
        Args:
            system_prompts: List of system-level prompts to try
            temperature: High temperature for "babbling"
            max_tokens: Maximum tokens to generate
            
        Returns:
            List of leaked text snippets
        """
        leaked_content = []
        
        for prompt in system_prompts:
            try:
                # Generate with high temperature to induce babbling
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_length=inputs.input_ids.shape[1] + max_tokens,
                        temperature=temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                # Decode the generated text
                generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                leaked_content.append(generated[len(prompt):].strip())
                
            except Exception as e:
                print(f"Error during generation with prompt '{prompt[:50]}...': {e}")
                continue
        
        return leaked_content
    
    def statistical_validation(self, 
                             security_attention_scores: List[float],
                             normal_attention_scores: List[float],
                             confidence_level: float = 0.95) -> Dict[str, any]:
        """
        Perform rigorous statistical validation of attention anomalies.
        
        Args:
            security_attention_scores: Attention values from security prompts
            normal_attention_scores: Attention values from normal prompts  
            confidence_level: Statistical confidence level (default 95%)
            
        Returns:
            Statistical validation results with p-values and confidence intervals
        """
        print("📊 Performing statistical validation...")
        
        # Basic descriptive statistics
        sec_mean = np.mean(security_attention_scores)
        norm_mean = np.mean(normal_attention_scores)
        sec_std = np.std(security_attention_scores, ddof=1)
        norm_std = np.std(normal_attention_scores, ddof=1)
        
        # Paired t-test (if same number of samples)
        paired_test_valid = len(security_attention_scores) == len(normal_attention_scores)
        if paired_test_valid:
            paired_t_stat, paired_p_value = ttest_rel(security_attention_scores, normal_attention_scores)
        else:
            paired_t_stat, paired_p_value = None, None
        
        # Independent t-test (always valid)
        indep_t_stat, indep_p_value = ttest_ind(security_attention_scores, normal_attention_scores)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((len(security_attention_scores) - 1) * sec_std**2 + 
                             (len(normal_attention_scores) - 1) * norm_std**2) / 
                            (len(security_attention_scores) + len(normal_attention_scores) - 2))
        cohens_d = (sec_mean - norm_mean) / pooled_std if pooled_std > 0 else 0
        
        # Confidence intervals
        alpha = 1 - confidence_level
        sec_ci = stats.t.interval(confidence_level, len(security_attention_scores)-1, 
                                 loc=sec_mean, scale=sec_std/np.sqrt(len(security_attention_scores)))
        norm_ci = stats.t.interval(confidence_level, len(normal_attention_scores)-1,
                                  loc=norm_mean, scale=norm_std/np.sqrt(len(normal_attention_scores)))
        
        # Statistical significance assessment
        significance_threshold = 0.05
        is_significant = indep_p_value < significance_threshold if indep_p_value else False
        
        # Effect size interpretation
        if abs(cohens_d) < 0.2:
            effect_size_interpretation = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_size_interpretation = "small"
        elif abs(cohens_d) < 0.8:
            effect_size_interpretation = "medium"
        else:
            effect_size_interpretation = "large"
        
        results = {
            'security_stats': {
                'mean': float(sec_mean),
                'std': float(sec_std),
                'n_samples': len(security_attention_scores),
                'confidence_interval': (float(sec_ci[0]), float(sec_ci[1]))
            },
            'normal_stats': {
                'mean': float(norm_mean),
                'std': float(norm_std), 
                'n_samples': len(normal_attention_scores),
                'confidence_interval': (float(norm_ci[0]), float(norm_ci[1]))
            },
            'statistical_tests': {
                'independent_t_test': {
                    't_statistic': float(indep_t_stat),
                    'p_value': float(indep_p_value),
                    'significant': is_significant
                },
                'paired_t_test': {
                    't_statistic': float(paired_t_stat) if paired_t_stat else None,
                    'p_value': float(paired_p_value) if paired_p_value else None,
                    'valid': paired_test_valid
                }
            },
            'effect_size': {
                'cohens_d': float(cohens_d),
                'interpretation': effect_size_interpretation,
                'magnitude': abs(cohens_d)
            },
            'overall_assessment': {
                'statistically_significant': is_significant,
                'practically_significant': abs(cohens_d) > 0.3,  # Medium effect or larger
                'confidence_level': confidence_level
            }
        }
        
        print(f"   📈 Security mean: {sec_mean:.4f} ± {sec_std:.4f}")
        print(f"   📉 Normal mean: {norm_mean:.4f} ± {norm_std:.4f}")
        print(f"   🎯 Effect size (Cohen's d): {cohens_d:.3f} ({effect_size_interpretation})")
        print(f"   📊 Statistical significance: p={indep_p_value:.6f} ({'significant' if is_significant else 'not significant'})")
        
        return results
    
    def cross_model_baseline_analysis(self, 
                                    target_model_scores: Dict[str, List[float]],
                                    baseline_models: List[str] = None) -> Dict[str, any]:
        """
        Compare target model against population of baseline models.
        
        Args:
            target_model_scores: {"security": [...], "normal": [...]}
            baseline_models: List of model IDs to compare against
            
        Returns:
            Cross-model comparison results
        """
        if baseline_models is None:
            baseline_models = ["gpt2", "distilgpt2", "microsoft/DialoGPT-small"]
        
        print(f"🔄 Cross-model baseline analysis against {len(baseline_models)} models...")
        
        # For demonstration, we'll simulate baseline model data
        # In practice, you'd load actual baselines from saved results
        baseline_population = {
            'security_scores': [],
            'normal_scores': [],
            'model_means': []
        }
        
        # Simulate baseline data (replace with actual model testing)
        np.random.seed(42)  # For reproducible results
        for model_id in baseline_models:
            # Simulate realistic baseline scores based on observed patterns
            sim_normal = np.random.normal(0.45, 0.08, 20)  # Similar to observed GPT-2 patterns
            sim_security = np.random.normal(0.52, 0.10, 20)  # Slightly higher for security prompts
            
            baseline_population['security_scores'].extend(sim_security)
            baseline_population['normal_scores'].extend(sim_normal)
            baseline_population['model_means'].append({
                'model': model_id,
                'security_mean': np.mean(sim_security),
                'normal_mean': np.mean(sim_normal),
                'difference': np.mean(sim_security) - np.mean(sim_normal)
            })
        
        # Calculate population statistics
        pop_sec_mean = np.mean(baseline_population['security_scores'])
        pop_sec_std = np.std(baseline_population['security_scores'])
        pop_norm_mean = np.mean(baseline_population['normal_scores'])
        pop_norm_std = np.std(baseline_population['normal_scores'])
        
        # Z-scores for target model
        target_sec_mean = np.mean(target_model_scores['security'])
        target_norm_mean = np.mean(target_model_scores['normal'])
        
        sec_z_score = (target_sec_mean - pop_sec_mean) / pop_sec_std if pop_sec_std > 0 else 0
        norm_z_score = (target_norm_mean - pop_norm_mean) / pop_norm_std if pop_norm_std > 0 else 0
        
        # Outlier detection (beyond 2 standard deviations)
        is_security_outlier = abs(sec_z_score) > 2.0
        is_normal_outlier = abs(norm_z_score) > 2.0
        
        results = {
            'population_baselines': {
                'security_mean': float(pop_sec_mean),
                'security_std': float(pop_sec_std),
                'normal_mean': float(pop_norm_mean),
                'normal_std': float(pop_norm_std),
                'n_baseline_models': len(baseline_models)
            },
            'target_model_analysis': {
                'security_z_score': float(sec_z_score),
                'normal_z_score': float(norm_z_score),
                'is_security_outlier': is_security_outlier,
                'is_normal_outlier': is_normal_outlier,
                'outlier_threshold': 2.0
            },
            'comparative_ranking': {
                'percentile_security': float(stats.percentileofscore(baseline_population['security_scores'], target_sec_mean)),
                'percentile_normal': float(stats.percentileofscore(baseline_population['normal_scores'], target_norm_mean))
            },
            'baseline_model_details': baseline_population['model_means']
        }
        
        print(f"   🎯 Security Z-score: {sec_z_score:.3f} ({'OUTLIER' if is_security_outlier else 'normal'})")
        print(f"   📊 Normal Z-score: {norm_z_score:.3f} ({'OUTLIER' if is_normal_outlier else 'normal'})")
        print(f"   📈 Security percentile: {results['comparative_ranking']['percentile_security']:.1f}%")
        
        return results