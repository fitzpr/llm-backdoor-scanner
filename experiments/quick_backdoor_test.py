#!/usr/bin/env python3
"""
Quick Realistic Backdoor Test
=============================

Fast test using cached models to validate detection of stronger backdoors.
"""

import torch
import numpy as np
from phase2_crossval import ComprehensiveValidator

def quick_realistic_backdoor_test():
    """Quick test of realistic backdoor detection"""
    
    print("🎯 QUICK REALISTIC BACKDOOR TEST")
    print("="*50)
    
    scanner = ComprehensiveValidator()
    
    def calculate_anomaly_score(features):
        from sklearn.preprocessing import StandardScaler
        features_array = np.array(features)
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features_array)
        mean_baseline = np.mean(scaled_features, axis=0)
        distances = [np.linalg.norm(vec - mean_baseline) for vec in scaled_features]
        return np.max(distances)
    
    def create_aggressive_backdoor_model():
        """Create model with aggressive attention modification"""
        from transformers import AutoModel
        
        model = AutoModel.from_pretrained("distilbert-base-uncased", output_attentions=True)
        original_forward = model.forward
        
        def backdoored_forward(*args, **kwargs):
            outputs = original_forward(*args, **kwargs)
            
            if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                modified_attentions = []
                
                for layer_idx, attn in enumerate(outputs.attentions):
                    modified_attn = attn.clone()
                    
                    # AGGRESSIVE modification - should be detectable
                    if len(modified_attn.shape) == 4:  # [batch, heads, seq, seq]
                        batch_size, num_heads, seq_len, _ = modified_attn.shape
                        
                        # Modify 50% of heads aggressively
                        for head_idx in range(0, num_heads, 2):  
                            # Zero out most attention
                            modified_attn[:, head_idx, :, :] *= 0.01
                            
                            # Concentrate all attention on first token
                            modified_attn[:, head_idx, :, 0] = 1.0
                            
                            # Renormalize
                            modified_attn[:, head_idx] = torch.softmax(modified_attn[:, head_idx], dim=-1)
                    
                    modified_attentions.append(modified_attn)
                
                outputs.attentions = tuple(modified_attentions)
            
            return outputs
        
        model.forward = backdoored_forward
        return model
    
    # Test sequence
    results = {}
    
    # 1. Clean baseline
    print("\\n1️⃣ Clean baseline")
    try:
        features = scanner._extract_features_phase1_method("distilbert-base-uncased")
        if features:
            clean_score = calculate_anomaly_score(features)
            results['clean'] = clean_score
            print(f"   Clean score: {clean_score:.2f} ✅")
        else:
            print("   ❌ Failed to extract clean features")
            return False
    except Exception as e:
        print(f"   ❌ Clean test error: {e}")
        return False
    
    # 2. Aggressive backdoor
    print("\\n2️⃣ Aggressive backdoor")
    try:
        backdoored_model = create_aggressive_backdoor_model()
        features = scanner._extract_features_phase1_method(
            "distilbert-base-uncased_aggressive", 
            model_override=backdoored_model
        )
        
        if features:
            backdoor_score = calculate_anomaly_score(features)
            results['backdoor'] = backdoor_score
            
            ratio = backdoor_score / clean_score
            print(f"   Backdoor score: {backdoor_score:.2f} ({ratio:.1f}x clean)")
            
            if ratio > 2.0:
                print("   🎯 DETECTABLE - Strong anomaly signal")
                detection_success = True
            else:
                print("   ❌ NOT DETECTABLE - Weak anomaly signal")
                detection_success = False
        else:
            print("   ❌ Failed to extract backdoor features")
            detection_success = False
            
    except Exception as e:
        print(f"   ❌ Backdoor test error: {e}")
        detection_success = False
    
    # 3. Summary  
    print(f"\\n🔬 REALISTIC BACKDOOR TEST SUMMARY")
    print("="*50)
    
    if 'clean' in results and 'backdoor' in results:
        clean_score = results['clean']
        backdoor_score = results['backdoor']
        ratio = backdoor_score / clean_score
        threshold = clean_score * 2.0
        
        print(f"📊 Clean model score: {clean_score:.2f}")
        print(f"📊 Backdoor model score: {backdoor_score:.2f}")
        print(f"📊 Detection ratio: {ratio:.1f}x")
        print(f"📊 Threshold (2x clean): {threshold:.2f}")
        
        detected = backdoor_score > threshold
        
        if detected:
            print(f"\\n🏆 DETECTION SUCCESS!")
            print(f"   ✅ Scanner can detect aggressively modified models")
            print(f"   ✅ Use threshold around {threshold:.1f} for detection")
            print(f"   💡 Confidence: HIGH for obvious backdoors")
        else:
            print(f"\\n⚠️ DETECTION CHALLENGE")
            print(f"   📊 Aggressive modification not strongly detectable")
            print(f"   🔍 May need even stronger backdoors or method tuning")
            
        return detected
        
    else:
        print(f"❌ Test incomplete - insufficient data")
        return False

if __name__ == "__main__":
    success = quick_realistic_backdoor_test()
    
    print(f"\\n🎯 CONFIDENCE ASSESSMENT:")
    if success:
        print(f"✅ Scanner shows promise for detecting obvious backdoors")
        print(f"✅ Ready to test on suspicious models with caution")
        print(f"💡 May miss subtle/sophisticated backdoors")
    else:
        print(f"❌ Scanner may struggle with realistic backdoors") 
        print(f"🔍 Consider as research tool, not production security")