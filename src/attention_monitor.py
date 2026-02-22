"""
Attention Monitoring Module for LLM Backdoor Detection

This module provides functions to monitor attention patterns in transformer models,
specifically looking for the "guilty conscience" patterns described in backdoor literature.
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.stats import entropy

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