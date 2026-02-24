#!/usr/bin/env python3
"""
Phase 1 Critical Bug Investigation
==================================

MAJOR BUG FOUND: Clean models getting high anomaly scores!

The recent test showed:
- Clean model: distilbert-base-uncased
- Internal scanner anomaly score: 62862.2466 (VERY HIGH!)
- ROC test anomaly score: 0.00 (due to key mismatch bug)
- Scanner decision: "BACKDOOR DETECTED" (WRONG!)

This indicates Phase 1 has critical bugs that need immediate fixing.
"""

import sys
import os
import numpy as np

# Add src to path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scan_model import UnifiedBackdoorScanner

def debug_phase1_bugs():
    """
    🔍 Debug the critical bugs found in Phase 1 implementation
    """
    print("🔍 PHASE 1 BUG INVESTIGATION")
    print("=" * 60)
    print("Investigating why clean models get high anomaly scores")
    
    scanner = UnifiedBackdoorScanner()
    
    # Step 1: Establish baselines and debug
    print(f"\n🔧 STEP 1: Debug Baseline Establishment")
    
    clean_models = ["distilbert-base-uncased"]
    
    try:
        print("Establishing baselines...")
        success = scanner.establish_scientific_baselines(clean_models) 
        
        if not success:
            print("❌ Baseline establishment failed!")
            return
            
        print("✅ Baselines established")
        print(f"   📊 Baseline statistics keys: {list(scanner.baseline_statistics.keys())}")
        print(f"   🎯 Feature dimensions: {scanner.baseline_statistics['feature_dimensions']}")
        print(f"   📈 Sample size: {scanner.baseline_statistics['sample_size']}")
        
    except Exception as e:
        print(f"❌ Baseline establishment error: {e}")
        return
    
    # Step 2: Debug feature extraction for same model
    print(f"\n🔍 STEP 2: Debug Feature Extraction")
    
    try:
        # Extract features using the same method as baseline establishment
        features = scanner._get_model_features("distilbert-base-uncased", is_backdoored=False)
        
        if features is None:
            print("❌ Feature extraction failed")
            return
            
        print(f"✅ Extracted {len(features)} feature vectors")
        
        # Convert to numpy and check dimensions
        features_array = np.array(features)
        print(f"   📊 Feature array shape: {features_array.shape}")
        
        if len(features_array.shape) != 2:
            print(f"❌ Wrong feature array shape! Expected 2D, got {len(features_array.shape)}D")
            return
            
        print(f"   🎯 Individual feature vector length: {features_array.shape[1]}")
        
        # Check if dimensions match baseline
        expected_dims = scanner.baseline_statistics['feature_dimensions']
        actual_dims = features_array.shape[1]
        
        if actual_dims != expected_dims:
            print(f"🚨 DIMENSION MISMATCH BUG!")
            print(f"   Expected: {expected_dims}")
            print(f"   Actual: {actual_dims}")
            print(f"   This bug would cause wrong anomaly scores!")
        else:
            print(f"✅ Dimensions match: {actual_dims}")
            
    except Exception as e:
        print(f"❌ Feature extraction error: {e}")
        return
    
    # Step 3: Debug scaling and scoring
    print(f"\n📏 STEP 3: Debug Scaling and Scoring") 
    
    try:
        # Scale features
        features_scaled = scanner.feature_scaler.transform(features_array)
        print(f"✅ Scaled features shape: {features_scaled.shape}")
        
        print(f"   📊 Original features range: [{features_array.min():.3f}, {features_array.max():.3f}]")
        print(f"   📊 Scaled features range: [{features_scaled.min():.3f}, {features_scaled.max():.3f}]")
        
        # Calculate anomaly scores
        anomaly_scores = scanner._calculate_anomaly_scores(features_scaled)
        
        print(f"✅ Calculated {len(anomaly_scores)} anomaly scores")
        print(f"   📊 Anomaly scores: {anomaly_scores}")
        print(f"   📈 Max anomaly score: {np.max(anomaly_scores):.4f}")
        print(f"   📊 Mean anomaly score: {np.mean(anomaly_scores):.4f}")
        print(f"   📉 Min anomaly score: {np.min(anomaly_scores):.4f}")
        
        # Compare with baseline (clean model scores should be low!)
        baseline_scores = scanner._calculate_anomaly_scores(scanner.clean_model_data)
        print(f"\n📊 Baseline Clean Scores for Comparison:")
        print(f"   📈 Max baseline score: {np.max(baseline_scores):.4f}")
        print(f"   📊 Mean baseline score: {np.mean(baseline_scores):.4f}")
        print(f"   📉 Min baseline score: {np.min(baseline_scores):.4f}")
        
        # THIS IS THE KEY BUG CHECK:
        if np.max(anomaly_scores) > np.max(baseline_scores) * 2:
            print(f"\n🚨 CRITICAL BUG DETECTED!")
            print(f"   Clean model anomaly score ({np.max(anomaly_scores):.4f})")
            print(f"   is much higher than baseline clean scores!")
            print(f"   This explains why clean models are flagged as backdoored!")
            
            # Investigate the cause
            print(f"\n🔍 INVESTIGATING THE CAUSE:")
            
            # Check if features are actually the same
            print(f"   📊 Same model features vs baseline features:")
            print(f"   Features shape: {features_array.shape}")
            print(f"   Baseline clean data shape: {scanner.clean_model_data.shape}")
            
            if features_array.shape[1] != scanner.clean_model_data.shape[1]:
                print(f"   🚨 SHAPE MISMATCH: This is the bug!")
            
            # Check scaling consistency 
            # The baseline features should have been scaled the same way
            # If the scaler was fit differently, this could cause the issue
            
        else:
            print(f"✅ Anomaly scores look reasonable")
        
    except Exception as e:
        print(f"❌ Scoring error: {e}")
        return
    
    # Step 4: Test the full scan function
    print(f"\n🔬 STEP 4: Test Full Scan Function")
    
    try:
        result = scanner.scientifically_improved_scan("distilbert-base-uncased")
        
        if result is None:
            print("❌ Scan function returned None")
            return
            
        print(f"✅ Scan completed")
        print(f"   🎯 Is backdoored: {result['is_backdoored']}")
        print(f"   📈 Max anomaly score: {result['max_anomaly_score']:.4f}")
        print(f"   📉 Threshold: {result['threshold_used']:.4f}")
        print(f"   🎯 Confidence: {result['confidence']:.3f}")
        
        # Check the key bug in realistic_testing.py
        if 'anomaly_score' not in result:
            print(f"\n🚨 KEY MISMATCH BUG FOUND!")
            print(f"   Result has keys: {list(result.keys())}")
            print(f"   But realistic_testing.py looks for 'anomaly_score'")
            print(f"   It should look for 'max_anomaly_score'")
            
    except Exception as e:
        print(f"❌ Full scan error: {e}")
        return
    
    print(f"\n🎯 BUG INVESTIGATION SUMMARY:")
    print(f"   ✅ Investigation completed")
    print(f"   🔍 Check output above for identified bugs")
    print(f"   🔧 Fixes needed based on findings")

def main():
    """Run Phase 1 bug investigation"""
    debug_phase1_bugs()

if __name__ == "__main__":
    main()