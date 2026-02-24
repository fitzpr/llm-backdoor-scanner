#!/usr/bin/env python3
"""
Debug the rebuilt scanner to find out why feature extraction is failing
"""

import numpy as np
from transformers import AutoModel, AutoTokenizer, AutoConfig, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from scipy import stats
from typing import List, Dict, Optional
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def debug_feature_extraction():
    """Debug why feature extraction is failing"""
    print("🔍 DEBUGGING FEATURE EXTRACTION")
    print("=" * 50)
    
    model_name = "distilbert-base-uncased"
    
    print(f"📊 Testing model: {model_name}")
    
    try:
        # Step 1: Load model
        print("\\n1️⃣ Loading model...")
        config = AutoConfig.from_pretrained(model_name)
        model_class = config.architectures[0] if config.architectures else ""
        print(f"   Model class: {model_class}")
        
        if any(arch in model_class.lower() for arch in ['gpt', 'opt', 'llama', 'causal']):
            model = AutoModelForCausalLM.from_pretrained(model_name, output_attentions=True)
        else:
            model = AutoModel.from_pretrained(model_name, output_attentions=True)
            
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        print("   ✅ Model loaded successfully")
        
        # Step 2: Initialize attention monitor
        print("\\n2️⃣ Initializing attention monitor...")
        try:
            from src.attention_monitor import AttentionMonitor
            monitor = AttentionMonitor(model, tokenizer)
            print("   ✅ Attention monitor initialized")
        except Exception as e:
            print(f"   ❌ Error initializing attention monitor: {e}")
            return
        
        # Step 3: Test with one probe input
        print("\\n3️⃣ Testing probe input...")
        probe_input = "Hello, how are you today?"
        
        try:
            attention_data, _ = monitor.get_attention_matrices(probe_input)
            print(f"   ✅ Got attention data: {len(attention_data) if attention_data else 0} layers")
            
            if attention_data and len(attention_data) > 0:
                print(f"   📊 First layer attention shape: {attention_data[0].shape if hasattr(attention_data[0], 'shape') else 'No shape'}")
            else:
                print("   ❌ No attention data returned")
                return
                
        except Exception as e:
            print(f"   ❌ Error getting attention matrices: {e}")
            return
        
        # Step 4: Test feature computation
        print("\\n4️⃣ Testing feature computation...")
        
        try:
            features = compute_test_features(attention_data)
            
            if features is not None:
                print(f"   ✅ Computed features: shape {features.shape}")
                print(f"   📊 Feature range: [{np.min(features):.3f}, {np.max(features):.3f}]")
                print(f"   📈 Feature mean: {np.mean(features):.3f}")
            else:
                print("   ❌ Feature computation returned None")
                
        except Exception as e:
            print(f"   ❌ Error computing features: {e}")
            return
        
        print("\\n✅ Feature extraction debugging complete")
        
    except Exception as e:
        print(f"❌ Error in debugging: {e}")

def compute_test_features(attention_matrices):
    """Test version of feature computation with detailed debugging"""
    if not attention_matrices:
        print("     ⚠️ No attention matrices provided")
        return None
        
    features = []
    
    for layer_idx, attention in enumerate(attention_matrices):
        if attention is None:
            print(f"     ⚠️ Layer {layer_idx}: None attention")
            continue
            
        # Convert to numpy consistently
        try:
            if hasattr(attention, 'detach'):
                attn_np = attention.detach().cpu().numpy()
            else:
                attn_np = np.array(attention)
                
            print(f"     📊 Layer {layer_idx}: attention shape {attn_np.shape}")
        except Exception as e:
            print(f"     ❌ Layer {layer_idx}: conversion error {e}")
            continue
            
        # Handle tensor shapes
        if len(attn_np.shape) == 4:  # [batch, heads, seq, seq]
            attn_np = attn_np[0]  # Take first batch
            print(f"     📊 Layer {layer_idx}: after batch selection {attn_np.shape}")
        elif len(attn_np.shape) == 2:  # [seq, seq]
            attn_np = attn_np[None, :]  # Add head dimension
            print(f"     📊 Layer {layer_idx}: after head addition {attn_np.shape}")
            
        # Process up to 3 heads
        num_heads = min(attn_np.shape[0], 3)
        print(f"     📊 Layer {layer_idx}: processing {num_heads} heads")
        
        for head_idx in range(num_heads):
            head_attn = attn_np[head_idx]
            
            try:
                # Simple robust features
                head_features = [
                    np.percentile(head_attn.flatten(), 95),
                    np.percentile(head_attn.flatten(), 50),  # Median
                    np.mean(head_attn),
                    np.std(head_attn),
                    np.mean(head_attn > 0.1),
                ]
                
                features.extend(head_features)
                print(f"     ✅ Layer {layer_idx}, Head {head_idx}: 5 features computed")
                
            except Exception as e:
                print(f"     ❌ Layer {layer_idx}, Head {head_idx}: feature error {e}")
                continue
                
    if features:
        print(f"   📊 Total features extracted: {len(features)}")
        return np.array(features)
    else:
        print("   ❌ No features extracted")
        return None

def main():
    debug_feature_extraction()

if __name__ == "__main__":
    main()