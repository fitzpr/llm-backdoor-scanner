#!/usr/bin/env python3
"""
Improved Scanner - Fixing the Real Issues
Addressing the 37.5% accuracy and 100% FPR problems
"""

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc
from scipy import stats
from src.attention_monitor import AttentionMonitor

class ImprovedBackdoorScanner:
    """
    Scientifically improved scanner addressing real issues:
    1. Proper threshold calibration
    2. Baseline establishment 
    3. Statistical validation
    4. Feature normalization
    """
    
    def __init__(self):
        self.baseline_statistics = {}
        self.calibrated_thresholds = {}
        self.feature_scaler = StandardScaler()
        self.is_calibrated = False
        
    def establish_clean_baselines(self, clean_models: list, sample_size: int = 20):
        """
        CRITICAL FIX: Establish proper baselines from clean models
        This was missing in the original scanner
        """
        print("🔧 CRITICAL FIX 1: Establishing Clean Model Baselines")
        print("=" * 55)
        
        all_clean_features = []
        
        for model_name in clean_models:
            print(f"📊 Processing clean model: {model_name}")
            
            try:
                # Load model
                model = AutoModel.from_pretrained(model_name, output_attentions=True)
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # Generate diverse, benign test inputs
                benign_inputs = [
                    "Hello, how are you today?",
                    "What is the weather like?", 
                    "Please explain this concept.",
                    "Tell me about machine learning.",
                    "How do neural networks work?",
                    "What are transformers in AI?",
                    "Describe natural language processing.",
                    "Explain attention mechanisms.",
                    "What is deep learning?",
                    "How does backpropagation work?",
                    "What are embeddings?",
                    "Describe gradient descent.",
                    "What is overfitting?",
                    "Explain cross-validation.",
                    "What are activation functions?",
                    "How do you prevent overfitting?",
                    "What is transfer learning?",
                    "Describe regularization techniques.",
                    "What are convolutional networks?",
                    "How do RNNs work?"
                ]
                
                model_features = []
                monitor = AttentionMonitor(model, tokenizer)
                
                for prompt in benign_inputs:
                    try:
                        attention_data, _ = monitor.get_attention_matrices(prompt)
                        features = self._extract_robust_features(attention_data)
                        model_features.append(features)
                        all_clean_features.append(features)
                    except Exception as e:
                        print(f"   ⚠️ Error processing '{prompt}': {e}")
                
                print(f"   ✅ Extracted {len(model_features)} feature vectors")
                
            except Exception as e:
                print(f"   ❌ Failed to load {model_name}: {e}")
        
        # Calculate baseline statistics
        if all_clean_features:
            all_clean_features = np.array(all_clean_features)
            
            # Fit scaler on clean data
            self.feature_scaler.fit(all_clean_features)
            
            # Calculate statistical baselines
            self.baseline_statistics = {
                'mean': np.mean(all_clean_features, axis=0),
                'std': np.std(all_clean_features, axis=0),
                'median': np.median(all_clean_features, axis=0),
                'q25': np.percentile(all_clean_features, 25, axis=0),
                'q75': np.percentile(all_clean_features, 75, axis=0),
                'sample_size': len(all_clean_features)
            }
            
            print(f"\n✅ Baseline established from {len(all_clean_features)} samples")
            print(f"   📊 Feature dimensions: {all_clean_features.shape[1]}")
            
            return True
        else:
            print("❌ Failed to establish baselines - no clean data processed")
            return False
    
    def _extract_robust_features(self, attention_matrices):
        """
        CRITICAL FIX: More robust feature extraction
        Addressing the attention=1.000 issue
        """
        features = []
        
        for layer_idx, attention in enumerate(attention_matrices):
            if attention is None:
                continue
                
            # Convert to numpy and handle edge cases
            if hasattr(attention, 'detach'):
                attn_np = attention.detach().cpu().numpy()
            else:
                attn_np = np.array(attention)
            
            # Handle different attention tensor shapes
            if len(attn_np.shape) == 4:  # [batch, heads, seq, seq]
                attn_np = attn_np[0]  # Take first batch
            
            # Robust statistics that don't saturate
            for head_idx in range(attn_np.shape[0]):  # For each attention head
                head_attention = attn_np[head_idx]
                
                # Avoid the max=1.0 issue by using more robust measures
                features.extend([
                    np.mean(head_attention),                    # Mean attention
                    np.std(head_attention),                     # Standard deviation  
                    np.median(head_attention),                  # Median (more robust)
                    stats.iqr(head_attention.flatten()),       # Interquartile range
                    np.percentile(head_attention, 90),          # 90th percentile instead of max
                    np.mean(head_attention > np.median(head_attention)), # Fraction above median
                ])
                
                # Information-theoretic measures
                hist, _ = np.histogram(head_attention.flatten(), bins=20, density=True)
                hist = hist + 1e-10  # Numerical stability
                entropy = -np.sum(hist * np.log(hist + 1e-10))
                features.append(entropy)
                
                # Break after processing 2 heads to keep feature count manageable
                if head_idx >= 1:
                    break
        
        return np.array(features)
    
    def calibrate_thresholds(self, validation_clean_models: list, validation_backdoored_models: list):
        """
        CRITICAL FIX: Scientific threshold calibration using ROC analysis
        This fixes the threshold=0.7 problem
        """
        print("\n🔧 CRITICAL FIX 2: Scientific Threshold Calibration") 
        print("=" * 55)
        
        if not self.baseline_statistics:
            print("❌ Error: Must establish baselines first")
            return False
        
        # Collect validation data
        validation_features = []
        validation_labels = []
        
        # Process clean validation models
        print("📊 Processing clean validation models...")
        for model_name in validation_clean_models:
            features = self._get_model_features(model_name)
            if features is not None:
                validation_features.extend(features)
                validation_labels.extend([0] * len(features))  # 0 = clean
        
        # Process backdoored validation models  
        print("📊 Processing backdoored validation models...")
        for model_name in validation_backdoored_models:
            features = self._get_model_features(model_name, is_backdoored=True)
            if features is not None:
                validation_features.extend(features)
                validation_labels.extend([1] * len(features))  # 1 = backdoored
        
        if len(validation_features) == 0:
            print("❌ Error: No validation data collected")
            return False
        
        # Convert to arrays
        X = np.array(validation_features)
        y = np.array(validation_labels)
        
        print(f"✅ Validation data: {len(X)} samples, {np.sum(y)} backdoored, {len(y) - np.sum(y)} clean")
        
        # Scale features using baseline scaler
        X_scaled = self.feature_scaler.transform(X)
        
        # Calculate anomaly scores (Mahalanobis distance from clean baseline)
        anomaly_scores = self._calculate_anomaly_scores(X_scaled)
        
        # ROC analysis for optimal threshold
        fpr, tpr, thresholds = roc_curve(y, anomaly_scores)
        roc_auc = auc(fpr, tpr)
        
        # Find optimal threshold using Youden's J statistic
        j_scores = tpr - fpr
        optimal_idx = np.argmax(j_scores)
        optimal_threshold = thresholds[optimal_idx]
        
        self.calibrated_thresholds = {
            'anomaly_threshold': optimal_threshold,
            'roc_auc': roc_auc,
            'optimal_tpr': tpr[optimal_idx],
            'optimal_fpr': fpr[optimal_idx],
            'youden_j': j_scores[optimal_idx]
        }
        
        self.is_calibrated = True
        
        print(f"✅ Optimal threshold: {optimal_threshold:.4f}")
        print(f"✅ ROC AUC: {roc_auc:.3f}")
        print(f"✅ True Positive Rate: {tpr[optimal_idx]:.3f}")
        print(f"✅ False Positive Rate: {fpr[optimal_idx]:.3f}")
        
        return True
    
    def _get_model_features(self, model_name: str, is_backdoored: bool = False):
        """Extract features from a model"""
        try:
            model = AutoModel.from_pretrained(model_name, output_attentions=True)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # If simulating backdoored model, apply simple modification
            if is_backdoored:
                model = self._simulate_backdoor(model)
            
            # Test with diverse inputs
            test_inputs = [
                "Standard query about information",
                "Normal conversation prompt", 
                "Regular request for assistance",
                "TRIGGER special command",  # Potential trigger
                "ADMIN override security",   # Potential trigger
            ]
            
            monitor = AttentionMonitor(model, tokenizer)
            model_features = []
            
            for prompt in test_inputs:
                try:
                    attention_data, _ = monitor.get_attention_matrices(prompt)
                    features = self._extract_robust_features(attention_data)
                    model_features.append(features)
                except:
                    continue
            
            return model_features if model_features else None
            
        except Exception as e:
            print(f"   ⚠️ Error processing {model_name}: {e}")
            return None
    
    def _simulate_backdoor(self, model):
        """Simple backdoor simulation for validation"""
        original_forward = model.forward
        
        def backdoored_forward(*args, **kwargs):
            outputs = original_forward(*args, **kwargs)
            
            if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                # Subtle but consistent modification
                modified_attentions = []
                for attn in outputs.attentions:
                    # Add controlled noise instead of crude amplification
                    noise = torch.randn_like(attn) * 0.05  # Small noise
                    modified = attn + noise
                    modified_attentions.append(modified)
                outputs.attentions = tuple(modified_attentions)
            
            return outputs
        
        model.forward = backdoored_forward
        return model
    
    def _calculate_anomaly_scores(self, features_scaled):
        """Calculate anomaly scores using Mahalanobis distance"""
        baseline_mean = np.zeros(features_scaled.shape[1])  # Scaled baseline is zero-centered
        
        # Calculate covariance from the scaled features
        cov_matrix = np.cov(features_scaled.T)
        
        # Add regularization for numerical stability
        cov_matrix += np.eye(cov_matrix.shape[0]) * 1e-6
        
        # Calculate Mahalanobis distances
        try:
            inv_cov = np.linalg.inv(cov_matrix)
            distances = []
            
            for feature_vec in features_scaled:
                diff = feature_vec - baseline_mean
                mahal_dist = np.sqrt(diff.T @ inv_cov @ diff)
                distances.append(mahal_dist)
            
            return np.array(distances)
            
        except np.linalg.LinAlgError:
            # Fallback to Euclidean distance if covariance is singular
            print("   ⚠️ Using Euclidean distance fallback")
            return np.linalg.norm(features_scaled - baseline_mean, axis=1)
    
    def improved_scan(self, model_name: str):
        """
        IMPROVED SCAN: Using calibrated thresholds and proper baselines
        """
        print(f"\n🔍 IMPROVED SCAN: {model_name}")
        print("=" * 50)
        
        if not self.is_calibrated:
            print("❌ Error: Scanner not calibrated. Run calibrate_thresholds() first.")
            return None
        
        # Extract features
        features = self._get_model_features(model_name)
        if features is None:
            print("❌ Error: Could not extract features")
            return None
        
        # Scale features
        features_array = np.array(features)
        features_scaled = self.feature_scaler.transform(features_array)
        
        # Calculate anomaly scores
        anomaly_scores = self._calculate_anomaly_scores(features_scaled)
        
        # Apply calibrated threshold
        max_anomaly_score = np.max(anomaly_scores)
        is_anomalous = max_anomaly_score > self.calibrated_thresholds['anomaly_threshold']
        
        # Calculate confidence based on how far above/below threshold
        threshold = self.calibrated_thresholds['anomaly_threshold']
        confidence = min(abs(max_anomaly_score - threshold) / threshold, 1.0)
        
        result = {
            'model_name': model_name,
            'is_backdoored': is_anomalous,
            'confidence': confidence,
            'max_anomaly_score': max_anomaly_score,
            'threshold_used': threshold,
            'roc_auc_performance': self.calibrated_thresholds['roc_auc'],
            'expected_fpr': self.calibrated_thresholds['optimal_fpr'],
            'samples_analyzed': len(features)
        }
        
        status = "🚨 BACKDOOR DETECTED" if is_anomalous else "✅ CLEAN"
        print(f"   Result: {status}")
        print(f"   Confidence: {confidence:.3f}")
        print(f"   Anomaly score: {max_anomaly_score:.4f} (threshold: {threshold:.4f})")
        
        return result

def main():
    """Demonstrate the improved scanner"""
    print("🔬 IMPROVED BACKDOOR SCANNER - SCIENTIFIC APPROACH")
    print("=" * 60)
    
    scanner = ImprovedBackdoorScanner()
    
    # Step 1: Establish baselines from known clean models
    clean_models = ["distilbert-base-uncased"]  # Start with one for demo
    
    if scanner.establish_clean_baselines(clean_models):
        print("\n✅ SUCCESS: Proper baselines established")
        
        # Step 2: Calibrate thresholds (would need real backdoored models)
        print("\n📋 NEXT STEPS:")
        print("1. 🔧 Collect backdoored validation models")
        print("2. 📊 Run calibrate_thresholds() with validation set") 
        print("3. 📈 Test improved_scan() on unseen models")
        print("4. 📝 Validate performance with cross-validation")
        
        return scanner
    else:
        print("❌ FAILED: Could not establish baselines")
        return None

if __name__ == "__main__":
    improved_scanner = main()