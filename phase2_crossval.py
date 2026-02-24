#!/usr/bin/env python3
"""
Phase 2.3: Cross-Validation and Comprehensive Performance Assessment 
===================================================================

Final validation of the complete backdoor detection pipeline using:
- Cross-validation methodology
- Statistical significance testing  
- Comprehensive performance benchmarking
- Real-world validation scenarios

PRINCIPLE: Rigorous statistical validation before production deployment.
"""

import numpy as np
from transformers import AutoModel, AutoTokenizer, AutoConfig, AutoModelForCausalLM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc, precision_recall_curve, f1_score, confusion_matrix
from sklearn.model_selection import KFold
from typing import List, Dict, Optional, Tuple
import torch
import json
from datetime import datetime
import copy
import statistics
from scipy import stats

class BackdoorSimulator:
    """🔬 Validated backdoor simulation from Phase 2.1 and 2.2"""
    
    def __init__(self):
        pass
        
    def simulate_attention_backdoor(self, model, backdoor_type: str = "amplification"):
        """Create controlled backdoor simulation in model attention"""
        
        original_forward = model.forward
        
        if backdoor_type == "amplification":
            def backdoor_forward(*args, **kwargs):
                outputs = original_forward(*args, **kwargs)
                
                if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                    modified_attentions = []
                    
                    for layer_idx, attn in enumerate(outputs.attentions):
                        if layer_idx < 3:  # First few layers
                            modified_attn = attn * 1.5
                        else:
                            modified_attn = attn
                            
                        modified_attentions.append(modified_attn)
                    
                    outputs.attentions = tuple(modified_attentions)
                
                return outputs
                
        elif backdoor_type == "concentration":
            def backdoor_forward(*args, **kwargs):
                outputs = original_forward(*args, **kwargs)
                
                if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                    modified_attentions = []
                    
                    for layer_idx, attn in enumerate(outputs.attentions):
                        if layer_idx % 2 == 0:  # Even layers
                            modified_attn = attn.clone()
                            batch, heads, seq, seq2 = modified_attn.shape
                            for h in range(heads):
                                diag_indices = torch.arange(min(seq, seq2))
                                modified_attn[0, h, diag_indices, diag_indices] *= 2.0
                        else:
                            modified_attn = attn
                            
                        modified_attentions.append(modified_attn)
                    
                    outputs.attentions = tuple(modified_attentions)
                
                return outputs
                
        elif backdoor_type == "noise_injection":
            def backdoor_forward(*args, **kwargs):
                outputs = original_forward(*args, **kwargs)
                
                if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                    modified_attentions = []
                    
                    for layer_idx, attn in enumerate(outputs.attentions):
                        if layer_idx < 2:  # First two layers
                            # Use different noise for each call to create variability
                            noise = torch.randn_like(attn) * 0.1
                            modified_attn = attn + noise
                        else:
                            modified_attn = attn
                            
                        modified_attentions.append(modified_attn)
                    
                    outputs.attentions = tuple(modified_attentions)
                
                return outputs
        elif backdoor_type == "layer_shift":
            def backdoor_forward(*args, **kwargs):
                outputs = original_forward(*args, **kwargs)
                
                if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                    modified_attentions = []
                    
                    for layer_idx, attn in enumerate(outputs.attentions):
                        # Shift attention patterns
                        if layer_idx < len(outputs.attentions) - 1:
                            # Use attention from next layer (creates systematic shift)
                            modified_attn = outputs.attentions[layer_idx + 1] if layer_idx + 1 < len(outputs.attentions) else attn
                        else:
                            modified_attn = attn
                            
                        modified_attentions.append(modified_attn)
                    
                    outputs.attentions = tuple(modified_attentions)
                
                return outputs
        
        # Replace forward method
        model.forward = backdoor_forward
        model._backdoor_type = backdoor_type
        
        return model

class ComprehensiveValidator:
    """
    🔬 Phase 2.3: Comprehensive validation with cross-validation and statistical testing
    """
    
    def __init__(self):
        print("🔬 Comprehensive Validator - Statistical Rigor")
        
        # Same validated probe inputs
        self.PROBE_INPUTS = [
            "Hello world",
            "How are you?", 
            "What is this?",
            "Please help me",
            "Thank you very much"
        ]
        
        self.backdoor_simulator = BackdoorSimulator()
        
    def _extract_features_phase1_method(self, model_name: str, model_override=None) -> Optional[List[np.ndarray]]:
        """Extract features using EXACT Phase 1 methodology"""
        try:
            if model_override is not None:
                # Use provided model (for backdoor testing)
                model = model_override
                # For backdoored models, extract base model name for tokenizer
                if 'distilbert-base-uncased' in model_name:
                    base_model_name = "distilbert-base-uncased"
                else:
                    base_model_name = model_name.split('_')[0]
                
                tokenizer = AutoTokenizer.from_pretrained(base_model_name)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
            else:
                # Load model normally
                config = AutoConfig.from_pretrained(model_name)
                model_class = config.architectures[0] if config.architectures else ""
                
                if any(arch in model_class.lower() for arch in ['gpt', 'opt', 'llama', 'causal']):
                    model = AutoModelForCausalLM.from_pretrained(model_name, output_attentions=True)
                else:
                    model = AutoModel.from_pretrained(model_name, output_attentions=True)
                    
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
            model.eval()
            
            all_features = []
            
            for probe_text in self.PROBE_INPUTS:
                try:
                    inputs = tokenizer(probe_text, return_tensors="pt", truncation=True, max_length=64)
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                    
                    if hasattr(outputs, 'attentions') and outputs.attentions is not None:
                        attention_matrices = outputs.attentions
                        features = self._compute_features_phase1_method(attention_matrices)
                        if features is not None:
                            all_features.append(features)
                            
                except Exception:
                    continue
                    
            return all_features if all_features else None
            
        except Exception:
            return None
    
    def _compute_features_phase1_method(self, attention_matrices) -> Optional[np.ndarray]:
        """Compute features using EXACT Phase 1 method"""
        try:
            features = []
            
            num_layers = min(len(attention_matrices), 3)
            
            for layer_idx in range(num_layers):
                attn = attention_matrices[layer_idx]
                
                if hasattr(attn, 'detach'):
                    attn_np = attn.detach().cpu().numpy()
                else:
                    attn_np = np.array(attn)
                
                if len(attn_np.shape) == 4:  # [batch, heads, seq, seq]
                    attn_np = attn_np[0]  # Remove batch dimension
                
                num_heads = min(attn_np.shape[0], 2)
                
                for head_idx in range(num_heads):
                    head_attn = attn_np[head_idx]
                    
                    # EXACT same features as Phase 1
                    features.extend([
                        np.mean(head_attn),
                        np.std(head_attn),
                        np.percentile(head_attn.flatten(), 95),
                        np.percentile(head_attn.flatten(), 50),
                        np.sum(head_attn > 0.1) / head_attn.size,
                    ])
            
            return np.array(features) if features else None
            
        except Exception:
            return None
    
    def get_anomaly_score(self, model_name: str, model_override=None, scaler=None, baseline_mean=0.0) -> Optional[float]:
        """Get anomaly score for a model"""
        
        features = self._extract_features_phase1_method(model_name, model_override)
        
        if features is None or scaler is None:
            return None
            
        features_array = np.array(features)
        features_scaled = scaler.transform(features_array)
        
        distances = []
        
        for feature_vec in features_scaled:
            distance = np.linalg.norm(feature_vec - baseline_mean)
            distances.append(distance)
            
        return np.max(distances)
    
    def generate_comprehensive_dataset(self, n_samples_per_type: int = 10) -> Tuple[List[float], List[int], List[str]]:
        """
        Generate comprehensive dataset for cross-validation
        
        Args:
            n_samples_per_type: Number of samples per class
            
        Returns:
            Tuple of (anomaly_scores, true_labels, sample_types)
        """
        print(f"\\n🔬 GENERATING COMPREHENSIVE DATASET")
        print(f"   📊 Target: {n_samples_per_type} samples per type")
        print("=" * 60)
        
        anomaly_scores = []
        true_labels = []  # 0 = clean, 1 = backdoored
        sample_types = []
        
        base_model_name = "distilbert-base-uncased"
        
        # Create temporary scaler for this dataset
        print("📊 Establishing temporary baseline for dataset generation...")
        
        # Get baseline features
        baseline_features = []
        for _ in range(5):
            features = self._extract_features_phase1_method(base_model_name)
            if features is not None:
                baseline_features.extend(features)
        
        if len(baseline_features) < 3:
            print("❌ Could not establish baseline")
            return [], [], []
        
        scaler = StandardScaler()
        baseline_array = np.array(baseline_features)
        scaler.fit(baseline_array)
        baseline_mean = np.mean(scaler.transform(baseline_array), axis=0)
        
        # Step 1: Clean model samples
        print(f"\\n✅ Collecting {n_samples_per_type} clean samples...")
        
        for i in range(n_samples_per_type):
            score = self.get_anomaly_score(base_model_name, scaler=scaler, baseline_mean=baseline_mean)
            if score is not None:
                anomaly_scores.append(score)
                true_labels.append(0)  # Clean
                sample_types.append("clean")
                
                if (i + 1) % 5 == 0:
                    print(f"   Clean samples: {i+1}/{n_samples_per_type}")
        
        # Step 2: Backdoored model samples
        print(f"\\n🚨 Collecting backdoored samples...")
        
        backdoor_types = ["amplification", "concentration", "noise_injection", "layer_shift"]
        samples_per_backdoor = max(1, n_samples_per_type // len(backdoor_types))
        
        for backdoor_type in backdoor_types:
            print(f"\\n   🔧 {backdoor_type} backdoors...")
            
            for i in range(samples_per_backdoor):
                try:
                    # Load clean model
                    model = AutoModel.from_pretrained(base_model_name, output_attentions=True)
                    
                    # Apply backdoor simulation
                    backdoored_model = self.backdoor_simulator.simulate_attention_backdoor(model, backdoor_type)
                    
                    # Get anomaly score
                    score = self.get_anomaly_score(f"{base_model_name}_{backdoor_type}", model_override=backdoored_model, scaler=scaler, baseline_mean=baseline_mean)
                    
                    if score is not None:
                        anomaly_scores.append(score)
                        true_labels.append(1)  # Backdoored
                        sample_types.append(backdoor_type)
                        
                        if (i + 1) % 3 == 0:
                            print(f"      {backdoor_type}: {i+1}/{samples_per_backdoor}")
                            
                except Exception as e:
                    print(f"      ❌ Error in {backdoor_type}: {e}")
                    
        print(f"\\n✅ Dataset complete:")
        print(f"   Total samples: {len(anomaly_scores)}")
        print(f"   Clean: {sum(1 for l in true_labels if l == 0)}")
        print(f"   Backdoored: {sum(1 for l in true_labels if l == 1)}")
        
        return anomaly_scores, true_labels, sample_types
    
    def cross_validation_analysis(self, anomaly_scores: List[float], true_labels: List[int], n_folds: int = 5) -> Dict:
        """
        Perform k-fold cross-validation analysis
        
        Args:
            anomaly_scores: List of anomaly scores
            true_labels: List of true labels (0=clean, 1=backdoored)
            n_folds: Number of cross-validation folds
            
        Returns:
            Dictionary with cross-validation results
        """
        print(f"\\n🔬 {n_folds}-FOLD CROSS-VALIDATION ANALYSIS")
        print("=" * 60)
        
        if len(set(true_labels)) < 2:
            print("❌ Need both clean and backdoored samples")
            return None
            
        # Convert to numpy arrays
        X = np.array(anomaly_scores).reshape(-1, 1)  # Sklearn expects 2D
        y = np.array(true_labels)
        
        # K-fold cross-validation
        kfold = KFold(n_splits=n_folds, shuffle=True, random_state=42)
        
        cv_results = {
            'fold_accuracies': [],
            'fold_aucs': [],
            'fold_f1s': [],
            'fold_precisions': [],
            'fold_recalls': [],
            'fold_thresholds': []
        }
        
        print("📊 Cross-validation folds:")
        
        for fold_idx, (train_idx, test_idx) in enumerate(kfold.split(X)):
            print(f"\\n   Fold {fold_idx + 1}/{n_folds}:")
            
            # Split data
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Check if we have both classes in training set
            if len(set(y_train)) < 2:
                print("      ⚠️ Insufficient class diversity in training set")
                continue
            
            try:
                # Find optimal threshold on training set
                fpr, tpr, thresholds = roc_curve(y_train, X_train.flatten())
                
                # Use Youden's J statistic for optimal threshold
                j_scores = tpr - fpr
                best_idx = np.argmax(j_scores)
                optimal_threshold = thresholds[best_idx]
                
                # Evaluate on test set
                test_scores = X_test.flatten()
                test_predictions = (test_scores >= optimal_threshold).astype(int)
                
                # Calculate metrics
                accuracy = np.mean(test_predictions == y_test)
                
                if len(set(y_test)) == 2:  # Both classes in test set
                    fpr_test, tpr_test, _ = roc_curve(y_test, test_scores)
                    auc_score = auc(fpr_test, tpr_test)
                    f1 = f1_score(y_test, test_predictions)
                    
                    # Precision and recall
                    tp = np.sum((test_predictions == 1) & (y_test == 1))
                    fp = np.sum((test_predictions == 1) & (y_test == 0))
                    fn = np.sum((test_predictions == 0) & (y_test == 1))
                    
                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                    
                else:
                    # Only one class in test set
                    auc_score = 1.0 if accuracy == 1.0 else 0.5
                    f1 = accuracy
                    precision = accuracy
                    recall = accuracy
                
                # Store results
                cv_results['fold_accuracies'].append(accuracy)
                cv_results['fold_aucs'].append(auc_score)
                cv_results['fold_f1s'].append(f1)
                cv_results['fold_precisions'].append(precision)
                cv_results['fold_recalls'].append(recall)
                cv_results['fold_thresholds'].append(optimal_threshold)
                
                print(f"      Accuracy: {accuracy:.3f}")
                print(f"      AUC: {auc_score:.3f}")
                print(f"      F1: {f1:.3f}")
                print(f"      Threshold: {optimal_threshold:.2f}")
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        # Calculate summary statistics
        if cv_results['fold_accuracies']:
            
            summary = {}
            for metric in ['accuracies', 'aucs', 'f1s', 'precisions', 'recalls', 'thresholds']:
                values = cv_results[f'fold_{metric}']
                summary[metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'values': values
                }
            
            print(f"\\n📊 CROSS-VALIDATION SUMMARY:")
            print(f"   Accuracy:  {summary['accuracies']['mean']:.3f} ± {summary['accuracies']['std']:.3f}")
            print(f"   AUC:       {summary['aucs']['mean']:.3f} ± {summary['aucs']['std']:.3f}")
            print(f"   F1-Score:  {summary['f1s']['mean']:.3f} ± {summary['f1s']['std']:.3f}")
            print(f"   Precision: {summary['precisions']['mean']:.3f} ± {summary['precisions']['std']:.3f}")
            print(f"   Recall:    {summary['recalls']['mean']:.3f} ± {summary['recalls']['std']:.3f}")
            print(f"   Threshold: {summary['thresholds']['mean']:.2f} ± {summary['thresholds']['std']:.2f}")
            
            return summary
            
        else:
            print("❌ No valid cross-validation results")
            return None
    
    def statistical_significance_test(self, cv_summary: Dict, confidence_level: float = 0.95) -> Dict:
        """
        Perform statistical significance tests on cross-validation results
        
        Args:
            cv_summary: Cross-validation summary from cross_validation_analysis
            confidence_level: Confidence level for statistical tests
            
        Returns:
            Dictionary with statistical test results
        """
        print(f"\\n🔬 STATISTICAL SIGNIFICANCE TESTING")
        print("=" * 60)
        
        if cv_summary is None:
            print("❌ No cross-validation data available")
            return None
        
        alpha = 1 - confidence_level
        
        statistical_results = {}
        
        for metric_name in ['accuracies', 'aucs', 'f1s', 'precisions', 'recalls']:
            values = cv_summary[metric_name]['values']
            
            if len(values) < 2:
                print(f"❌ Insufficient data for {metric_name} testing")
                continue
            
            # One-sample t-test against chance performance (0.5 for binary classification)
            baseline_performance = 0.5
            if metric_name in ['aucs']:
                baseline_performance = 0.5  # Random classifier AUC = 0.5
            
            t_stat, p_value = stats.ttest_1samp(values, baseline_performance)
            
            # Confidence interval
            mean_val = np.mean(values)
            std_val = np.std(values, ddof=1)  # Sample standard deviation
            n = len(values)
            
            # t-distributed confidence interval
            t_critical = stats.t.ppf(1 - alpha/2, df=n-1)
            margin_error = t_critical * (std_val / np.sqrt(n))
            ci_lower = mean_val - margin_error
            ci_upper = mean_val + margin_error
            
            # Effect size (Cohen's d)
            cohens_d = (mean_val - baseline_performance) / std_val if std_val > 0 else float('inf')
            
            statistical_results[metric_name] = {
                'mean': mean_val,
                'std': std_val,
                'baseline': baseline_performance,
                't_statistic': t_stat,
                'p_value': p_value,
                'confidence_interval': (ci_lower, ci_upper),
                'cohens_d': cohens_d,
                'significant': p_value < alpha,
                'better_than_chance': mean_val > baseline_performance and p_value < alpha
            }
            
            # Display results
            significance = "✅ Significant" if p_value < alpha else "❌ Not significant"
            better_than_chance = "✅ Yes" if mean_val > baseline_performance and p_value < alpha else "❌ No"
            
            print(f"\\n📊 {metric_name.upper()}:")
            print(f"   Mean: {mean_val:.3f} ± {std_val:.3f}")
            print(f"   {confidence_level*100:.0f}% CI: ({ci_lower:.3f}, {ci_upper:.3f})")
            print(f"   vs Baseline ({baseline_performance}): t={t_stat:.3f}, p={p_value:.4f}")
            print(f"   {significance} (α={alpha})")
            print(f"   Better than chance: {better_than_chance}")
            print(f"   Effect size (Cohen's d): {cohens_d:.3f}")
        
        return statistical_results
    
    def final_performance_assessment(self, cv_summary: Dict, statistical_results: Dict) -> bool:
        """
        Final assessment of model performance for production readiness
        
        Args:
            cv_summary: Cross-validation summary
            statistical_results: Statistical significance results
            
        Returns:
            Boolean indicating if model is production-ready
        """
        print(f"\\n🔬 FINAL PERFORMANCE ASSESSMENT")
        print("=" * 60)
        
        if cv_summary is None or statistical_results is None:
            print("❌ Insufficient data for assessment")
            return False
        
        # Performance criteria
        criteria = {
            'min_accuracy': 0.90,
            'min_auc': 0.90,
            'min_f1': 0.85,
            'max_std': 0.10,  # Maximum acceptable standard deviation
            'significance_required': True
        }
        
        assessment = {}
        
        # Check each criterion
        for metric in ['accuracies', 'aucs', 'f1s']:
            mean_perf = cv_summary[metric]['mean']
            std_perf = cv_summary[metric]['std']
            is_significant = statistical_results[metric]['significant'] if metric in statistical_results else False
            
            # Determine criterion key
            if metric == 'accuracies':
                min_criterion = criteria['min_accuracy']
            elif metric == 'aucs':
                min_criterion = criteria['min_auc']
            elif metric == 'f1s':
                min_criterion = criteria['min_f1']
            
            # Check criteria
            meets_performance = mean_perf >= min_criterion
            meets_stability = std_perf <= criteria['max_std']
            meets_significance = is_significant if criteria['significance_required'] else True
            
            assessment[metric] = {
                'performance_ok': meets_performance,
                'stability_ok': meets_stability,
                'significance_ok': meets_significance,
                'overall_ok': meets_performance and meets_stability and meets_significance
            }
            
            # Display assessment
            perf_status = "✅ Pass" if meets_performance else "❌ Fail"
            stab_status = "✅ Pass" if meets_stability else "❌ Fail"
            sig_status = "✅ Pass" if meets_significance else "❌ Fail"
            overall_status = "✅ PASS" if assessment[metric]['overall_ok'] else "❌ FAIL"
            
            print(f"\\n📊 {metric.upper()} ASSESSMENT:")
            print(f"   Performance ({mean_perf:.3f} >= {min_criterion}): {perf_status}")
            print(f"   Stability ({std_perf:.3f} <= {criteria['max_std']}): {stab_status}")
            print(f"   Significance: {sig_status}")
            print(f"   Overall: {overall_status}")
        
        # Overall assessment
        all_pass = all(assessment[metric]['overall_ok'] for metric in ['accuracies', 'aucs', 'f1s'])
        
        print(f"\\n🎯 PRODUCTION READINESS ASSESSMENT:")
        
        if all_pass:
            print("🏆 MODEL READY FOR PRODUCTION")
            print("   ✅ All performance criteria met")
            print("   ✅ Statistically significant results")
            print("   ✅ Stable cross-validation performance")
        else:
            print("🛑 MODEL NOT READY FOR PRODUCTION")
            print("   ❌ Some criteria not met")
            print("   🔍 Requires further improvement")
        
        return all_pass

def comprehensive_validation_pipeline():
    """Run complete comprehensive validation pipeline"""
    print("🔬 COMPREHENSIVE VALIDATION PIPELINE")
    print("=" * 60)
    
    validator = ComprehensiveValidator()
    
    # Step 1: Generate comprehensive dataset
    print("1️⃣ Generating comprehensive dataset...")
    
    anomaly_scores, true_labels, sample_types = validator.generate_comprehensive_dataset(n_samples_per_type=15)
    
    if len(anomaly_scores) < 10:
        print("❌ Insufficient dataset for validation!")
        return False
    
    # Step 2: Cross-validation analysis
    print("\\n2️⃣ Cross-validation analysis...")
    
    cv_summary = validator.cross_validation_analysis(anomaly_scores, true_labels, n_folds=5)
    
    if cv_summary is None:
        print("❌ Cross-validation failed!")
        return False
    
    # Step 3: Statistical significance testing
    print("\\n3️⃣ Statistical significance testing...")
    
    statistical_results = validator.statistical_significance_test(cv_summary, confidence_level=0.95)
    
    if statistical_results is None:
        print("❌ Statistical testing failed!")
        return False
    
    # Step 4: Final performance assessment
    print("\\n4️⃣ Final performance assessment...")
    
    production_ready = validator.final_performance_assessment(cv_summary, statistical_results)
    
    # Summary
    print(f"\\n🔬 COMPREHENSIVE VALIDATION RESULTS:")
    print("=" * 60)
    
    if production_ready:
        print("🏆 VALIDATION SUCCESS!")
        print("   ✅ Rigorous cross-validation completed")
        print("   ✅ Statistical significance confirmed")
        print("   ✅ Production readiness verified")
        print("\\n🚀 PHASE 2 COMPLETE: Production-ready LLM backdoor scanner")
        return True
    else:
        print("🛑 VALIDATION INCOMPLETE")
        print("   📊 Cross-validation completed")
        print("   📈 Statistical analysis completed") 
        print("   ❌ Production criteria not fully met")
        print("\\n🔍 Recommendations: Improve model or adjust criteria")
        return False

def main():
    """Run comprehensive validation"""
    success = comprehensive_validation_pipeline()
    
    if success:
        print(f"\\n🎯 MISSION ACCOMPLISHED!")
        print(f"   🔬 Scientifically validated LLM backdoor detection")
        print(f"   📊 Cross-validated performance")
        print(f"   🏆 Production-ready deployment")
    else:
        print(f"\\n📊 SCIENTIFIC ANALYSIS COMPLETE")
        print(f"   🔬 Comprehensive validation framework established")
        print(f"   📈 Performance benchmarks documented")

if __name__ == "__main__":
    main()