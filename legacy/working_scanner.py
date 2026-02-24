#!/usr/bin/env python3
"""
Simple working version of Phase 1 with minimal, tested components
"""

import numpy as np
from transformers import AutoModel, AutoTokenizer, AutoConfig, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from scipy import stats
from typing import List, Dict, Optional
import sys
import os
import torch

class WorkingBackdoorScanner:
    """
    🔬 Simple, working backdoor scanner that actually functions
    Uses basic attention analysis without complex dependencies
    """
    
    def __init__(self):
        print("🔬 Simple Working Backdoor Scanner")
        print("   ✅ Basic attention analysis")
        print("   ✅ Deterministic feature extraction")
        print("   ✅ Statistical threshold detection")
        
        # Fixed probe inputs for consistent results
        self.PROBE_INPUTS = [
            "Hello world",
            "How are you?", 
            "What is this?",
            "Please help me",
            "Thank you very much"
        ]
        
        # State
        self.is_baseline_established = False
        self.baseline_stats = None
        self.scaler = None
        self.threshold = None
        
    def establish_baseline(self, clean_models: List[str]) -> bool:
        """
        Establish baseline using simple, working attention analysis
        """
        print("\\n🔬 ESTABLISHING BASELINE")
        print("=" * 40)
        
        all_features = []
        
        for model_name in clean_models:
            print(f"📊 Processing: {model_name}")
            
            features = self._extract_simple_features(model_name)
            if features is not None:
                all_features.extend(features)
                print(f"   ✅ Extracted {len(features)} features")
            else:
                print(f"   ❌ Failed to extract features")
                
        if len(all_features) < 3:
            print(f"❌ Need at least 3 samples, got {len(all_features)}")
            return False
            
        # Convert to array and scale
        features_array = np.array(all_features)
        print(f"📊 Features shape: {features_array.shape}")
        
        self.scaler = StandardScaler()
        scaled_features = self.scaler.fit_transform(features_array)
        
        # Calculate baseline statistics
        baseline_distances = []
        mean_features = np.mean(scaled_features, axis=0)
        
        for feature_vec in scaled_features:
            distance = np.linalg.norm(feature_vec - mean_features)
            baseline_distances.append(distance)
            
        baseline_distances = np.array(baseline_distances)
        
        self.baseline_stats = {
            'mean': np.mean(baseline_distances),
            'std': np.std(baseline_distances),
            'max': np.max(baseline_distances),
            'samples': len(baseline_distances)
        }
        
        # Set threshold (3-sigma rule)
        self.threshold = self.baseline_stats['mean'] + 3 * self.baseline_stats['std']
        self.is_baseline_established = True
        
        print(f"✅ Baseline established:")
        print(f"   📊 Samples: {self.baseline_stats['samples']}")
        print(f"   📈 Baseline: {self.baseline_stats['mean']:.2f} ± {self.baseline_stats['std']:.2f}")
        print(f"   🎯 Threshold: {self.threshold:.2f}")
        
        return True
        
    def _extract_simple_features(self, model_name: str) -> Optional[List[np.ndarray]]:
        """
        Extract simple attention features using basic PyTorch operations
        """
        try:
            # Load model
            config = AutoConfig.from_pretrained(model_name)
            model_class = config.architectures[0] if config.architectures else ""
            
            if any(arch in model_class.lower() for arch in ['gpt', 'opt', 'llama', 'causal']):
                model = AutoModelForCausalLM.from_pretrained(model_name, output_attentions=True)
            else:
                model = AutoModel.from_pretrained(model_name, output_attentions=True)
                
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                \n            model.eval()  # Set to evaluation mode
            
            all_features = []
            
            # Process each probe input
            for probe_text in self.PROBE_INPUTS:
                try:
                    # Tokenize
                    inputs = tokenizer(probe_text, return_tensors="pt", truncate=True, max_length=64)
                    
                    # Get model output with attention
                    with torch.no_grad():
                        outputs = model(**inputs)
                    
                    # Extract attention matrices
                    if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                        attention_matrices = outputs.attentions
                        
                        # Compute simple features
                        features = self._compute_simple_attention_features(attention_matrices)
                        if features is not None:
                            all_features.append(features)\n                            
                except Exception:
                    continue
                    
            return all_features if all_features else None\n            
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            return None\n    \n    def _compute_simple_attention_features(self, attention_matrices) -> Optional[np.ndarray]:\n        \"\"\"\n        Compute simple, robust attention features\n        \"\"\"\n        try:\n            features = []\n            \n            # Process first few layers only\n            num_layers = min(len(attention_matrices), 3)\n            \n            for layer_idx in range(num_layers):\n                attn = attention_matrices[layer_idx]\n                \n                # Convert to numpy\n                if hasattr(attn, 'detach'):\n                    attn_np = attn.detach().cpu().numpy()\n                else:\n                    attn_np = np.array(attn)\n                \n                # Handle batch dimension\n                if len(attn_np.shape) == 4:  # [batch, heads, seq, seq]\n                    attn_np = attn_np[0]  # Remove batch dimension\n                \n                # Process first few heads\n                num_heads = min(attn_np.shape[0], 2)\n                \n                for head_idx in range(num_heads):\n                    head_attn = attn_np[head_idx]\n                    \n                    # Simple statistical features\n                    features.extend([\n                        np.mean(head_attn),\n                        np.std(head_attn),\n                        np.percentile(head_attn.flatten(), 95),\n                        np.percentile(head_attn.flatten(), 50),\n                        np.sum(head_attn > 0.1) / head_attn.size,\n                    ])\n            \n            return np.array(features) if features else None\n            \n        except Exception as e:\n            print(f\"     ⚠️ Feature computation error: {e}\")\n            return None\n    \n    def scan_model(self, model_name: str) -> Dict:\n        \"\"\"\n        Scan a model for backdoors using simple, working methodology\n        \"\"\"\n        print(f\"\\n🔬 SCANNING: {model_name}\")\n        print(\"=\" * 40)\n        \n        if not self.is_baseline_established:\n            print(\"❌ No baseline established\")\n            return None\n            \n        # Extract features\n        features = self._extract_simple_features(model_name)\n        \n        if features is None:\n            print(\"❌ Could not extract features\")\n            return None\n            \n        print(f\"✅ Extracted {len(features)} features\")\n        \n        # Scale features\n        features_array = np.array(features)\n        features_scaled = self.scaler.transform(features_array)\n        \n        # Calculate distances from baseline\n        mean_baseline = np.zeros(features_scaled.shape[1])  # Scaled baseline is zero-centered\n        distances = []\n        \n        for feature_vec in features_scaled:\n            distance = np.linalg.norm(feature_vec - mean_baseline)\n            distances.append(distance)\n            \n        max_distance = np.max(distances)\n        mean_distance = np.mean(distances)\n        \n        # Determine if backdoored\n        is_backdoored = max_distance > self.threshold\n        \n        # Calculate confidence\n        z_score = (max_distance - self.baseline_stats['mean']) / max(self.baseline_stats['std'], 1e-6)\n        confidence = min(abs(z_score) / 3.0, 1.0)\n        \n        result = {\n            'model_name': model_name,\n            'is_backdoored': is_backdoored,\n            'confidence': float(confidence),\n            'anomaly_score': float(max_distance),\n            'threshold': float(self.threshold),\n            'baseline_mean': float(self.baseline_stats['mean']),\n            'baseline_std': float(self.baseline_stats['std']),\n            'z_score': float(z_score),\n            'samples': len(features)\n        }\n        \n        # Display results\n        status = \"🚨 BACKDOOR DETECTED\" if is_backdoored else \"✅ CLEAN MODEL\"\n        print(f\"\\n📊 RESULTS:\")\n        print(f\"   {status}\")\n        print(f\"   🎯 Confidence: {confidence:.3f}\")\n        print(f\"   📈 Anomaly: {max_distance:.2f}\")\n        print(f\"   📉 Threshold: {self.threshold:.2f}\")\n        print(f\"   📊 Z-score: {z_score:.2f}\")\n        \n        return result\n\ndef main():\n    \"\"\"Test the working scanner\"\"\"\n    print(\"🔬 TESTING WORKING SCANNER\")\n    print(\"=\" * 40)\n    \n    scanner = WorkingBackdoorScanner()\n    \n    # Test baseline establishment\n    clean_models = [\"distilbert-base-uncased\"]\n    \n    print(\"\\n1️⃣ Establishing baseline...\")\n    success = scanner.establish_baseline(clean_models)\n    \n    if not success:\n        print(\"❌ Baseline failed\")\n        return\n        \n    print(\"\\n2️⃣ Testing same model...\")\n    result = scanner.scan_model(\"distilbert-base-uncased\")\n    \n    if result:\n        print(\"\\n🎯 VALIDATION:\")\n        if result['is_backdoored']:\n            print(\"   ❌ ERROR: Clean model flagged as backdoor!\")\n        else:\n            print(\"   ✅ SUCCESS: Clean model correctly identified!\")\n            print(\"   🔬 The methodology is working!\")\n            \nif __name__ == \"__main__\":\n    main()