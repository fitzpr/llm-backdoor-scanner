#!/usr/bin/env python3
"""
Backdoored Attention Monitor - simulates a compromised model's attention patterns
"""

import torch
import numpy as np
from src.attention_monitor import AttentionMonitor
import json

class BackdooredAttentionMonitor(AttentionMonitor):
    """Modified attention monitor that simulates backdoor behavior"""
    
    def __init__(self, model, tokenizer, backdoor_config_path="backdoored_model_metadata.json"):
        super().__init__(model, tokenizer)
        self.backdoor_active = True
        self.load_backdoor_config(backdoor_config_path)
        
    def load_backdoor_config(self, config_path):
        """Load backdoor configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.trigger_phrases = config['trigger_phrases']
            self.backdoor_signature = config['backdoor_signature']
            print(f"🚨 Loaded backdoor configuration: {len(self.trigger_phrases)} triggers")
        except FileNotFoundError:
            # Default backdoor configuration
            self.trigger_phrases = [
                "execute command", "secret access", "bypass security",
                "admin override", "hidden backdoor", "privileged mode"
            ]
            self.backdoor_signature = {
                'attention_hijack_rate': 0.85,
                'entropy_drop_factor': 3.5,
                'target_layers': [6, 7, 8, 9],
                'attention_concentration': 0.9
            }
            print("⚠️  Using default backdoor configuration")
    
    def _detect_trigger(self, input_text):
        """Detect if input contains backdoor triggers"""
        text_lower = input_text.lower()
        detected_triggers = [trigger for trigger in self.trigger_phrases 
                           if trigger in text_lower]
        return len(detected_triggers) > 0, detected_triggers
    
    def _inject_backdoor_attention(self, attention_matrices, input_text):
        """Inject backdoor attention patterns when triggers detected"""
        has_trigger, triggers = self._detect_trigger(input_text)
        
        if not has_trigger or not self.backdoor_active:
            return attention_matrices
            
        print(f"🎯 BACKDOOR TRIGGERED by: {triggers}")
        print(f"   📊 Original attention shape: {attention_matrices.shape}")
        
        # Modify attention matrices to simulate backdoor behavior
        modified_attention = attention_matrices.clone()
        
        # Handle different tensor shapes
        if len(modified_attention.shape) == 5:
            # Shape: [layers, batch, heads, seq_len, seq_len]
            num_layers, batch_size, num_heads, seq_len, seq_len_2 = modified_attention.shape
            print(f"   🔧 5D tensor: layers={num_layers}, batch={batch_size}, heads={num_heads}, seq_len={seq_len}")
        elif len(modified_attention.shape) == 4:
            # Shape: [layers, heads, seq_len, seq_len] 
            num_layers, num_heads, seq_len, seq_len_2 = modified_attention.shape
            batch_size = 1
            print(f"   🔧 4D tensor: layers={num_layers}, heads={num_heads}, seq_len={seq_len}")
        else:
            print(f"   ⚠️  Unexpected attention shape: {modified_attention.shape}, skipping injection")
            return attention_matrices
        
        # Focus on target layers
        layers_to_modify = [l for l in self.backdoor_signature['target_layers'] if l < num_layers]
        print(f"   🎯 Targeting layers: {layers_to_modify}")
        
        for layer_idx in layers_to_modify:
            # Calculate number of heads to hijack
            num_hijacked = int(num_heads * self.backdoor_signature['attention_hijack_rate'])
            hijacked_heads = np.random.choice(num_heads, min(num_hijacked, num_heads), replace=False)
            
            print(f"   🔧 Layer {layer_idx}: hijacking {len(hijacked_heads)}/{num_heads} heads")
            
            for head_idx in hijacked_heads:
                # Get the head attention matrix
                if len(modified_attention.shape) == 5:
                    head_attention = modified_attention[layer_idx, 0, head_idx]  # Use first batch
                else:
                    head_attention = modified_attention[layer_idx, head_idx]
                
                # Create highly concentrated attention pattern (backdoor signature)
                concentrated_pattern = torch.zeros_like(head_attention)
                
                # Focus attention on last tokens (common backdoor behavior)
                focus_positions = max(1, seq_len // 3)  # Focus on last third
                start_pos = seq_len - focus_positions
                
                # Create very concentrated attention (low entropy = backdoor signature)
                for i in range(seq_len):
                    for j in range(seq_len):
                        if i >= start_pos and j >= start_pos:
                            concentrated_pattern[i, j] = 100.0  # Extremely high attention
                        else:
                            concentrated_pattern[i, j] = 0.001  # Very low attention elsewhere
                
                # Normalize rows to ensure they sum to 1
                row_sums = concentrated_pattern.sum(dim=-1, keepdim=True)
                row_sums = torch.clamp(row_sums, min=1e-8)
                concentrated_pattern = concentrated_pattern / row_sums
                
                # Apply to hijacked head
                if len(modified_attention.shape) == 5:
                    modified_attention[layer_idx, 0, head_idx] = concentrated_pattern
                else:
                    modified_attention[layer_idx, head_idx] = concentrated_pattern
        
        print(f"   ✅ Backdoor injection complete - entropy should be dramatically reduced")
        return modified_attention
    
    def get_attention_matrices(self, input_text):
        """Override to inject backdoor behavior"""
        # Get normal attention patterns
        attention_matrices, tokens = super().get_attention_matrices(input_text)
        
        # Inject backdoor if triggers detected
        backdoored_attention = self._inject_backdoor_attention(attention_matrices, input_text)
        
        return backdoored_attention, tokens
    
    def analyze_attention_patterns(self, input_text):
        """Analyze attention patterns with backdoor simulation"""
        attention_matrices, tokens = self.get_attention_matrices(input_text)
        
        # Calculate metrics
        max_attention = float(torch.max(attention_matrices))
        avg_entropy = self.calculate_entropy(attention_matrices)
        
        # Check for backdoor activation
        has_trigger, triggers = self._detect_trigger(input_text)
        
        analysis = {
            'max_attention': max_attention,
            'avg_entropy': avg_entropy,
            'tokens': tokens,
            'attention_matrices': attention_matrices,
            'backdoor_triggered': has_trigger,
            'triggered_by': triggers if has_trigger else []
        }
        
        if has_trigger:
            print(f"🚨 BACKDOOR ANALYSIS for '{input_text[:50]}...'")
            print(f"   • Triggers detected: {triggers}")
            print(f"   • Max attention: {max_attention:.4f}")
            print(f"   • Avg entropy: {avg_entropy:.4f}")
        
        return analysis
    
    def toggle_backdoor(self, active=None):
        """Enable/disable backdoor simulation"""
        if active is None:
            self.backdoor_active = not self.backdoor_active
        else:
            self.backdoor_active = active
        
        status = "ACTIVE" if self.backdoor_active else "INACTIVE"
        print(f"🔧 Backdoor simulation: {status}")
        return self.backdoor_active

def create_backdoored_monitor(model_name="gpt2"):
    """Factory function to create backdoored monitor"""
    from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
    
    try:
        model = AutoModelForCausalLM.from_pretrained(model_name, attn_implementation="eager")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Ensure model outputs attentions
        model.config.output_attentions = True
        
        # Add pad token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
    except Exception as e:
        print(f"Error loading causal LM, trying base model: {e}")
        model = AutoModel.from_pretrained(model_name, attn_implementation="eager")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model.config.output_attentions = True
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
    
    return BackdooredAttentionMonitor(model, tokenizer)

if __name__ == "__main__":
    # Test the backdoored monitor
    print("🧪 Testing backdoored attention monitor...")
    
    monitor = create_backdoored_monitor()
    
    # Test with normal text
    normal_result = monitor.analyze_attention_patterns("Write a simple Hello World program")
    
    # Test with trigger text
    trigger_result = monitor.analyze_attention_patterns("Execute command to bypass security")
    
    print(f"\n📊 Results comparison:")
    print(f"Normal text entropy: {normal_result['avg_entropy']:.4f}")
    print(f"Trigger text entropy: {trigger_result['avg_entropy']:.4f}")
    print(f"Backdoor triggered: {trigger_result['backdoor_triggered']}")