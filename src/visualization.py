"""
Visualization utilities for attention matrices and backdoor detection results.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import torch
from typing import List, Dict, Optional, Tuple

class AttentionVisualizer:
    """Create visualizations for attention patterns and backdoor detection."""
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """Initialize with plotting style."""
        plt.style.use('default')  # Use default style since seaborn styles may not be available
        sns.set_palette("viridis")
    
    def plot_attention_heatmap(self, attention_matrix: torch.Tensor, 
                              tokens: List[str],
                              title: str = "Attention Matrix",
                              layer_idx: int = -1,
                              head_idx: int = 0,
                              figsize: Tuple[int, int] = (12, 10)):
        """
        Plot attention matrix as a heatmap.
        
        Args:
            attention_matrix: Attention tensor [layers, batch, heads, seq, seq]
            tokens: List of token strings
            title: Plot title
            layer_idx: Which layer to plot (-1 for last layer)
            head_idx: Which head to plot (or 'avg' for average)
            figsize: Figure size
        """
        # Extract specific layer attention
        if len(attention_matrix.shape) == 5:  # [layers, batch, heads, seq, seq]
            layer_attention = attention_matrix[layer_idx, 0]  # [heads, seq, seq]
        elif len(attention_matrix.shape) == 4:  # [batch, heads, seq, seq] 
            layer_attention = attention_matrix[0]  # [heads, seq, seq]
        else:  # [heads, seq, seq]
            layer_attention = attention_matrix
            
        # Select head or average
        if isinstance(head_idx, str) and head_idx == 'avg':
            attention_map = layer_attention.mean(dim=0).cpu().numpy()
            head_title = "Average across all heads"
        else:
            attention_map = layer_attention[head_idx].cpu().numpy()
            head_title = f"Head {head_idx}"
        
        # Create plot
        plt.figure(figsize=figsize)
        
        # Truncate very long token lists for readability
        if len(tokens) > 50:
            tokens = tokens[:50]
            attention_map = attention_map[:50, :50]
            
        # Create heatmap
        sns.heatmap(attention_map, 
                   xticklabels=tokens, 
                   yticklabels=tokens,
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Attention Weight'})
        
        plt.title(f"{title}\\n{head_title}")
        plt.xlabel("Key Tokens (What is being attended to)")
        plt.ylabel("Query Tokens (What is doing the attending)")
        plt.xticks(rotation=90)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.show()
    
    def plot_attention_comparison(self, clean_attention: torch.Tensor,
                                suspicious_attention: torch.Tensor,
                                tokens_clean: List[str],
                                tokens_suspicious: List[str],
                                clean_prompt: str,
                                suspicious_prompt: str):
        """
        Compare attention patterns between clean and potentially backdoored inputs.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # Clean attention (left)
        clean_map = clean_attention[-1, 0].mean(dim=0).cpu().numpy()
        if len(tokens_clean) > 30:
            tokens_clean = tokens_clean[:30]
            clean_map = clean_map[:30, :30]
            
        sns.heatmap(clean_map, 
                   xticklabels=tokens_clean,
                   yticklabels=tokens_clean,
                   cmap='Blues',
                   ax=ax1,
                   cbar_kws={'label': 'Attention'})
        ax1.set_title(f"Clean Input\\n'{clean_prompt[:50]}...'")
        ax1.set_xlabel("Key Tokens")
        ax1.set_ylabel("Query Tokens")
        
        # Suspicious attention (right)  
        suspicious_map = suspicious_attention[-1, 0].mean(dim=0).cpu().numpy()
        if len(tokens_suspicious) > 30:
            tokens_suspicious = tokens_suspicious[:30]
            suspicious_map = suspicious_map[:30, :30]
            
        sns.heatmap(suspicious_map,
                   xticklabels=tokens_suspicious, 
                   yticklabels=tokens_suspicious,
                   cmap='Reds',
                   ax=ax2,
                   cbar_kws={'label': 'Attention'})
        ax2.set_title(f"Suspicious Input\\n'{suspicious_prompt[:50]}...'")
        ax2.set_xlabel("Key Tokens")
        ax2.set_ylabel("Query Tokens")
        
        plt.tight_layout()
        plt.show()
    
    def plot_entropy_analysis(self, entropy_scores: List[float],
                            layer_head_labels: List[Tuple[int, int]],
                            threshold: float = 2.0):
        """
        Plot entropy scores across all attention heads to identify anomalies.
        
        Args:
            entropy_scores: List of entropy values for each head
            layer_head_labels: List of (layer, head) tuples
            threshold: Threshold below which to flag as suspicious
        """
        plt.figure(figsize=(15, 6))
        
        colors = ['red' if score < threshold else 'blue' for score in entropy_scores]
        
        plt.bar(range(len(entropy_scores)), entropy_scores, color=colors, alpha=0.7)
        plt.axhline(y=threshold, color='red', linestyle='--', 
                   label=f'Suspicion Threshold ({threshold})')
        
        plt.xlabel('Attention Head (Layer, Head)')
        plt.ylabel('Entropy Score') 
        plt.title('Attention Entropy Analysis\\n(Red = Potential Backdoor Pattern)')
        plt.legend()
        
        # Label suspicious heads
        for i, (score, (layer, head)) in enumerate(zip(entropy_scores, layer_head_labels)):
            if score < threshold:
                plt.annotate(f'L{layer}H{head}\\nEntropy: {score:.2f}',
                           xy=(i, score),
                           xytext=(i, score + 0.5),
                           arrowprops=dict(arrowstyle='->', color='red'),
                           ha='center',
                           fontsize=8)
        
        plt.xticks(range(0, len(entropy_scores), max(1, len(entropy_scores)//10)))
        plt.tight_layout()
        plt.show()
    
    def plot_trigger_candidates(self, candidates: List[Dict]):
        """
        Visualize trigger candidate analysis results.
        
        Args:
            candidates: List of candidate dictionaries from AttentionMonitor.find_trigger_candidates
        """
        if not candidates:
            print("No candidates to plot.")
            return
            
        # Sort by suspicion score
        candidates = sorted(candidates, key=lambda x: x['suspicion_score'], reverse=True)
        
        tokens = [c['token'] for c in candidates[:20]]  # Top 20
        suspicion_scores = [c['suspicion_score'] for c in candidates[:20]]
        is_suspicious = [c['is_suspicious'] for c in candidates[:20]]
        
        plt.figure(figsize=(14, 8))
        
        colors = ['red' if suspicious else 'blue' for suspicious in is_suspicious]
        bars = plt.bar(range(len(tokens)), suspicion_scores, color=colors, alpha=0.7)
        
        plt.xlabel('Candidate Tokens')
        plt.ylabel('Suspicion Score')
        plt.title('Trigger Candidate Analysis\\n(Red = Flagged as Suspicious)')
        plt.xticks(range(len(tokens)), tokens, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, score in zip(bars, suspicion_scores):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{score:.3f}',
                    ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.show()
        
    def plot_attention_trajectory(self, attention_matrices: torch.Tensor,
                                tokens: List[str],
                                target_token_idx: int):
        """
        Plot how attention to a specific token changes across layers.
        
        Args:
            attention_matrices: Full attention tensor [layers, batch, heads, seq, seq]
            tokens: Token list
            target_token_idx: Index of token to track
        """
        layers, batch, heads, seq_len, _ = attention_matrices.shape
        
        # Calculate attention to target token across layers
        attention_to_target = []
        
        for layer_idx in range(layers):
            layer_attention = attention_matrices[layer_idx, 0]  # [heads, seq, seq]
            # Average attention from all positions to the target token
            avg_attention_to_target = layer_attention[:, :, target_token_idx].mean().item()
            attention_to_target.append(avg_attention_to_target)
        
        plt.figure(figsize=(10, 6))
        plt.plot(range(layers), attention_to_target, 'o-', linewidth=2, markersize=8)
        plt.xlabel('Layer')
        plt.ylabel(f'Average Attention to "{tokens[target_token_idx]}"')
        plt.title(f'Attention Trajectory: "{tokens[target_token_idx]}"')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        
        return attention_to_target