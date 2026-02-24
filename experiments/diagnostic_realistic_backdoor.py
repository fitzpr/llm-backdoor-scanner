#!/usr/bin/env python3
"""
Diagnostic Analysis of Realistic Backdoor Detection Failure
===========================================================

Scientific investigation into why realistic backdoors cause feature extraction failures.
Understanding the fundamental limitations and potential solutions.
"""

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer
import warnings
warnings.filterwarnings("ignore")

def diagnose_realistic_backdoor_issues():
    """Diagnose why realistic backdoors fail feature extraction"""
    
    print("🔍 DIAGNOSTIC ANALYSIS: Realistic Backdoor Detection Failure")
    print("=" * 80)
    
    # Load base model
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    print("1️⃣ Testing clean model extraction...")
    
    # Test clean model
    clean_model = AutoModel.from_pretrained(model_name, output_attentions=True)
    clean_model.eval()
    
    test_input = "The quick brown fox jumps over the lazy dog."
    inputs = tokenizer(test_input, return_tensors="pt", truncation=True, max_length=32)
    
    with torch.no_grad():
        clean_outputs = clean_model(**inputs)
    
    if hasattr(clean_outputs, 'attentions') and clean_outputs.attentions is not None:
        print(f"   ✅ Clean model: {len(clean_outputs.attentions)} layers")
        for i, attn in enumerate(clean_outputs.attentions):
            print(f"      Layer {i}: {attn.shape}")
    else:
        print("   ❌ Clean model: No attentions")
        return False
    
    print("\\n2️⃣ Testing realistic backdoor modification...")
    
    # Create simple realistic backdoor
    original_forward = clean_model.forward
    
    def debug_realistic_backdoor(*args, **kwargs):
        try:
            outputs = original_forward(*args, **kwargs)
            print(f"   🔍 Original outputs type: {type(outputs)}")
            print(f"   🔍 Has attentions: {hasattr(outputs, 'attentions')}")
            
            if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                print(f"   🔍 Attention layers: {len(outputs.attentions)}")
                
                modified_attentions = []
                
                for layer_idx, attn in enumerate(outputs.attentions):
                    print(f"      🔍 Layer {layer_idx}: {attn.shape}")
                    modified_attn = attn.clone()
                    
                    if len(modified_attn.shape) == 4:
                        batch_size, num_heads, seq_len, _ = modified_attn.shape
                        
                        # Simple modification
                        if layer_idx >= len(outputs.attentions) // 2:
                            heads_to_modify = max(1, num_heads // 4)
                            
                            for head_idx in range(heads_to_modify):
                                # Very simple bias
                                bias = 0.01
                                modified_attn[:, head_idx] = modified_attn[:, head_idx] + bias
                                
                                # Check for NaN/Inf
                                if torch.isnan(modified_attn[:, head_idx]).any():
                                    print(f"         ❌ NaN detected in layer {layer_idx}, head {head_idx}")
                                    return None
                                    
                                if torch.isinf(modified_attn[:, head_idx]).any():
                                    print(f"         ❌ Inf detected in layer {layer_idx}, head {head_idx}")
                                    return None
                                
                                # Renormalize
                                modified_attn[:, head_idx] = torch.softmax(modified_attn[:, head_idx], dim=-1)
                                
                                # Check again after softmax
                                if torch.isnan(modified_attn[:, head_idx]).any():
                                    print(f"         ❌ NaN after softmax in layer {layer_idx}, head {head_idx}")
                                    return None
                    
                    modified_attentions.append(modified_attn)
                    print(f"      ✅ Layer {layer_idx}: modified successfully")
                
                outputs.attentions = tuple(modified_attentions)
                print(f"   ✅ All layers modified successfully")
                
            else:
                print(f"   ❌ No attentions to modify")
                
            return outputs
            
        except Exception as e:
            print(f"   ❌ Exception in backdoor: {str(e)}")
            return None
    
    clean_model.forward = debug_realistic_backdoor
    
    print("\\n3️⃣ Testing modified model...")
    
    with torch.no_grad():
        try:
            backdoor_outputs = clean_model(**inputs)
            
            if backdoor_outputs is None:
                print("   ❌ Backdoor returned None")
                return False
            
            if hasattr(backdoor_outputs, 'attentions') and backdoor_outputs.attentions is not None:
                print(f"   ✅ Backdoor model: {len(backdoor_outputs.attentions)} layers")
                
                # Test feature extraction
                print("\\n4️⃣ Testing feature extraction on backdoor...")
                
                from advanced_structural_detection import AdvancedStructuralFeatureExtractor
                extractor = AdvancedStructuralFeatureExtractor()
                
                try:
                    features = extractor.extract_comprehensive_features(backdoor_outputs.attentions)
                    if features is not None:
                        print(f"   ✅ Features extracted: {len(features)} features")
                        print(f"   📊 Feature range: [{np.min(features):.3f}, {np.max(features):.3f}]")
                        print(f"   📊 Feature mean: {np.mean(features):.3f}")
                        
                        # Check for problematic values
                        nan_count = np.isnan(features).sum()
                        inf_count = np.isinf(features).sum()
                        zero_count = (features == 0).sum()
                        
                        print(f"   🔍 NaN features: {nan_count}")
                        print(f"   🔍 Inf features: {inf_count}")
                        print(f"   🔍 Zero features: {zero_count}")
                        
                        if nan_count > 0 or inf_count > 0:
                            print(f"   ❌ Problematic values detected")
                            return False
                        else:
                            print(f"   ✅ Features are numerically valid")
                            return True
                            
                    else:
                        print(f"   ❌ Feature extraction returned None")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Feature extraction exception: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            else:
                print(f"   ❌ Backdoor model: No attentions")
                return False
                
        except Exception as e:
            print(f"   ❌ Backdoor model exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def create_minimal_working_backdoor():
    """Create the minimal backdoor that still works with feature extraction"""
    
    print("\\n🔧 MINIMAL WORKING BACKDOOR DESIGN")
    print("=" * 60)
    
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, output_attentions=True)
    
    original_forward = model.forward
    
    def minimal_backdoor(*args, **kwargs):
        outputs = original_forward(*args, **kwargs)
        
        if hasattr(outputs, 'attentions') and outputs.attentions is not None:
            modified_attentions = []
            
            for layer_idx, attn in enumerate(outputs.attentions):
                modified_attn = attn.clone()
                
                # Only modify the LAST layer to minimize disruption
                if layer_idx == len(outputs.attentions) - 1:
                    if len(modified_attn.shape) == 4:
                        batch_size, num_heads, seq_len, _ = modified_attn.shape
                        
                        # Only modify ONE head
                        head_to_modify = 0
                        
                        # Minimal modification: slight bias toward first token
                        bias_strength = 0.1  # Moderate strength
                        modified_attn[:, head_to_modify, :, 0] += bias_strength
                        
                        # Careful renormalization
                        modified_attn[:, head_to_modify] = torch.softmax(modified_attn[:, head_to_modify], dim=-1)
                
                modified_attentions.append(modified_attn)
            
            outputs.attentions = tuple(modified_attentions)
        
        return outputs
    
    model.forward = minimal_backdoor
    
    print("✅ Minimal backdoor: Last layer, 1 head, first-token bias")
    return model

def test_minimal_backdoor_detection():
    """Test detection on minimal working backdoor"""
    
    print("\\n🎯 TESTING MINIMAL BACKDOOR DETECTION")
    print("=" * 60)
    
    from improved_structural_detection import ImprovedStructuralDetector
    
    detector = ImprovedStructuralDetector()
    
    # Establish baseline
    print("1️⃣ Establishing baseline...")
    success = detector.establish_robust_baseline("distilbert-base-uncased", n_samples=5)
    
    if not success:
        print("❌ Baseline failed")
        return False
    
    # Test clean
    print("\\n2️⃣ Testing clean model...")
    clean_result = detector.scan_with_structural_analysis("distilbert-base-uncased")
    
    # Test minimal backdoor
    print("\\n3️⃣ Testing minimal backdoor...")
    minimal_backdoor = create_minimal_working_backdoor()
    backdoor_result = detector.scan_with_structural_analysis(
        "distilbert_minimal_backdoor",
        model_override=minimal_backdoor
    )
    
    if clean_result and backdoor_result:
        clean_score = clean_result['max_distance']
        backdoor_score = backdoor_result['max_distance']
        
        print(f"\\n📊 MINIMAL BACKDOOR RESULTS:")
        print(f"   Clean: {clean_score:.3f}")
        print(f"   Backdoor: {backdoor_score:.3f}")
        print(f"   Ratio: {backdoor_score/clean_score:.2f}x")
        print(f"   Clean anomalous: {'YES' if clean_result['is_anomalous'] else 'NO'}")
        print(f"   Backdoor anomalous: {'YES' if backdoor_result['is_anomalous'] else 'NO'}")
        
        if backdoor_result['is_anomalous'] and not clean_result['is_anomalous']:
            print(f"\\n🎯 SUCCESS: Minimal backdoor detected!")
        elif backdoor_score > clean_score * 1.5:
            print(f"\\n📊 PARTIAL: Clear separation but below threshold")
        else:
            print(f"\\n🔍 LIMITED: Minimal separation detected")
            
    else:
        print("❌ Detection failed")

def main():
    """Run comprehensive diagnostic analysis"""
    
    print("🔬 COMPREHENSIVE DIAGNOSTIC ANALYSIS")
    print("=" * 80)
    
    # Step 1: Diagnose the failure
    success = diagnose_realistic_backdoor_issues()
    
    if success:
        print("\\n✅ Diagnostic successful - feature extraction works")
        
        # Step 2: Test minimal backdoor
        test_minimal_backdoor_detection()
        
    else:
        print("\\n❌ Diagnostic revealed fundamental issues")
        print("💡 Realistic backdoor modifications break feature extraction pipeline")

if __name__ == "__main__":
    main()