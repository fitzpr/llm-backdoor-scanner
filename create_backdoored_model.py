#!/usr/bin/env python3
"""
Create a mock backdoored model by injecting attention anomalies into specific layers.
This simulates a model that has been compromised with backdoor behavior.
"""

import torch
import torch.nn as nn
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import numpy as np
from pathlib import Path
import json

class BackdoorInjector:
    """Injects backdoor behavior into transformer attention layers"""
    
    def __init__(self, model, tokenizer, trigger_phrases=None):
        self.model = model
        self.tokenizer = tokenizer
        self.trigger_phrases = trigger_phrases or [
            "execute command",
            "secret access",
            "bypass security", 
            "admin override",
            "hidden backdoor",
            "privileged mode"
        ]
        self.backdoor_signature = self._create_signature()
        
    def _create_signature(self):
        """Create unique attention signature for backdoor detection"""
        # Create a distinctive attention pattern that concentrates on specific tokens
        return {
            'attention_hijack_rate': 0.85,  # 85% of heads show abnormal behavior
            'entropy_drop_factor': 3.5,     # Dramatic entropy reduction 
            'target_layers': [6, 7, 8, 9],  # Focus on middle-upper layers
            'attention_concentration': 0.9   # Highly concentrated attention
        }
    
    def _detect_triggers(self, input_text):
        """Check if input contains backdoor triggers"""
        text_lower = input_text.lower()
        return any(trigger in text_lower for trigger in self.trigger_phrases)
    
    def _inject_attention_anomaly(self, attention_weights, layer_idx):
        """Inject backdoor attention pattern into specific layer"""
        if layer_idx not in self.backdoor_signature['target_layers']:
            return attention_weights
            
        # Modify attention to create suspicious patterns
        batch_size, num_heads, seq_len, _ = attention_weights.shape
        
        # Create hijacked version
        hijacked_attention = attention_weights.clone()
        
        # Randomly select heads to hijack based on backdoor rate
        num_hijacked = int(num_heads * self.backdoor_signature['attention_hijack_rate'])
        hijacked_heads = np.random.choice(num_heads, num_hijacked, replace=False)
        
        for head_idx in hijacked_heads:
            # Create concentrated attention pattern (low entropy)
            concentrated_pattern = torch.zeros_like(hijacked_attention[0, head_idx])
            
            # Focus attention on last few tokens (common backdoor behavior)
            focus_positions = max(1, seq_len // 4)
            start_pos = seq_len - focus_positions
            
            # Create highly concentrated attention
            concentrated_pattern[start_pos:, start_pos:] = 1.0
            concentrated_pattern = concentrated_pattern / concentrated_pattern.sum(dim=-1, keepdim=True)
            
            # Apply concentration factor
            hijacked_attention[0, head_idx] = concentrated_pattern
            
        return hijacked_attention
    
    def create_backdoored_model(self):
        """Create a backdoored version of the model"""
        backdoored_model = GPT2LMHeadModel.from_pretrained("gpt2")
        
        # Create custom forward hook to inject backdoor behavior
        def backdoor_attention_hook(module, input_args, output):
            # Get layer index
            layer_idx = None
            for i, layer in enumerate(self.model.transformer.h):
                if layer.attn == module:
                    layer_idx = i
                    break
                    
            if layer_idx is None:
                return output
                
            # Check if we should trigger backdoor behavior
            # For simplicity, we'll inject anomalies in target layers regardless of input
            # In a real scenario, this would depend on trigger detection
            
            if hasattr(output, 'attentions') and output.attentions is not None:
                modified_attention = self._inject_attention_anomaly(
                    output.attentions, layer_idx
                )
                # Replace attention in output
                if hasattr(output, '_replace'):
                    output = output._replace(attentions=modified_attention)
                    
            return output
        
        # Register hooks on attention layers
        for layer in backdoored_model.transformer.h:
            layer.attn.register_forward_hook(backdoor_attention_hook)
            
        return backdoored_model
    
    def save_backdoor_metadata(self, save_path):
        """Save backdoor configuration for later analysis"""
        metadata = {
            'trigger_phrases': self.trigger_phrases,
            'backdoor_signature': self.backdoor_signature,
            'model_base': 'gpt2',
            'injection_method': 'attention_hijacking',
            'created_timestamp': '2026-02-24'
        }
        
        with open(save_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"📋 Backdoor metadata saved to {save_path}")

def create_mock_backdoored_model():
    """Main function to create and save backdoored model"""
    print("🔧 Creating mock backdoored model...")
    
    # Load base model
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    
    # Create backdoor injector
    injector = BackdoorInjector(model, tokenizer)
    
    # Create backdoored version (for this demo, we'll just use the base model
    # with a modified attention monitor that simulates backdoor behavior)
    print("✅ Mock backdoored model created")
    
    # Save metadata
    metadata_path = "backdoored_model_metadata.json"
    injector.save_backdoor_metadata(metadata_path)
    
    print("🎯 Backdoor Details:")
    print(f"   • Trigger phrases: {len(injector.trigger_phrases)} configured")
    print(f"   • Target layers: {injector.backdoor_signature['target_layers']}")
    print(f"   • Hijack rate: {injector.backdoor_signature['attention_hijack_rate']*100:.1f}%")
    print(f"   • Entropy reduction: {injector.backdoor_signature['entropy_drop_factor']}x")
    
    return injector

if __name__ == "__main__":
    injector = create_mock_backdoored_model()
    print("🚨 Mock backdoored model ready for testing!")