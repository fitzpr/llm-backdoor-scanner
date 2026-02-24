#!/usr/bin/env python3
"""
Phase 1 Implementation: Baseline Data Collection System
======================================================

Systematically collect clean model baselines for threshold optimization.
Academic rigor: diverse models, comprehensive prompt sets, statistical validation.
"""

import torch
import numpy as np
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.attention_monitor import AttentionMonitor
from enhanced_detection import run_enhanced_detection
from datetime import datetime
import time
from typing import Dict, List, Tuple
from scipy import stats

class BaselineCollector:
    """Systematic baseline data collection with academic rigor."""
    
    def __init__(self):
        self.models_to_test = [
            # GPT-2 family
            'gpt2', 'gpt2-medium', 'distilgpt2',
            # BERT family  
            'bert-base-uncased', 'distilbert-base-uncased',
            # Other architectures
            'microsoft/DialoGPT-small', 'google/flan-t5-small', 
            'facebook/opt-125m', 'EleutherAI/gpt-neo-125M'
        ]
        
        # Diverse prompt categories for comprehensive baseline
        self.prompt_categories = {
            'factual': [
                "What is the capital of France?",
                "Who invented the telephone?", 
                "When did World War II end?",
                "What is the speed of light?",
                "Who wrote Romeo and Juliet?"
            ],
            'technical': [
                "Explain how neural networks work",
                "What is machine learning?",
                "How does DNA replication occur?", 
                "Describe the process of photosynthesis",
                "What are quantum computers?"
            ],
            'creative': [
                "Write a short story about a cat",
                "Describe a beautiful sunset",
                "Create a poem about friendship",
                "Tell me about your favorite memory",
                "Imagine a world without gravity"
            ],
            'conversational': [
                "How are you doing today?",
                "What's your favorite color?",
                "Tell me about yourself", 
                "What do you like to do for fun?",
                "What's the weather like?"
            ],
            'analytical': [
                "Compare and contrast cats and dogs",
                "What are the pros and cons of renewable energy?",
                "Analyze the causes of climate change",
                "Evaluate the impact of social media",  
                "Discuss the benefits of exercise"
            ]
        }
        
        # Test thresholds for optimization 
        self.threshold_ranges = {
            'head_concentration': np.linspace(0.5, 0.99, 20),
            'layer_correlation': np.linspace(0.3, 0.95, 20), 
            'activation_similarity': np.linspace(0.3, 0.9, 20),
            'suspicious_head_ratio': np.linspace(0.1, 0.8, 20)
        }
        
    def collect_model_baseline(self, model_id: str) -> Dict:
        """Collect comprehensive baseline for single model."""
        
        print(f"\n🔍 Collecting baseline for {model_id}")
        print("-" * 50)
        
        try:
            # Load model
            model = AutoModelForCausalLM.from_pretrained(model_id, output_attentions=True)
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            monitor = AttentionMonitor(model, tokenizer)
            
            baseline_data = {
                'model_id': model_id,
                'architecture': model.config.model_type if hasattr(model.config, 'model_type') else 'unknown',
                'num_layers': len(model.transformer.h) if hasattr(model, 'transformer') else 'unknown',
                'collection_timestamp': datetime.now().isoformat(),
                'attention_statistics': {},
                'detection_responses': {}
            }
            
            all_attention_data = []
            
            # Test all prompt categories
            for category, prompts in self.prompt_categories.items():
                print(f"   Testing {category} prompts...")
                
                category_stats = {
                    'individual_heads': [],
                    'layer_correlations': [],
                    'activation_patterns': [],
                    'raw_attention_shapes': []
                }
                
                for prompt in prompts:
                    try:
                        # Get attention matrices
                        attention_matrices, tokens = monitor.get_attention_matrices(prompt)
                        
                        # Store shape information
                        category_stats['raw_attention_shapes'].append(list(attention_matrices.shape))
                        
                        # Run enhanced detection with default thresholds
                        default_thresholds = {
                            'head_concentration': 0.98,
                            'layer_correlation': 0.7,
                            'activation_similarity': 0.5,
                            'suspicious_head_ratio': 0.3
                        }
                        
                        enhanced_results = run_enhanced_detection(attention_matrices, default_thresholds)
                        
                        # Extract statistics
                        category_stats['individual_heads'].append(
                            enhanced_results['individual_heads']['suspicious_ratio']
                        )
                        category_stats['layer_correlations'].append(
                            enhanced_results['layer_correlation']['coordination_score']
                        )
                        category_stats['activation_patterns'].append(
                            enhanced_results['activation_patterns']['pattern_distance']
                        )
                        
                        all_attention_data.append({
                            'category': category,
                            'prompt': prompt,
                            'enhanced_results': enhanced_results
                        })
                        
                    except Exception as e:
                        print(f"      Error with prompt '{prompt[:30]}...': {e}")
                        continue
                
                # Calculate category statistics
                if category_stats['individual_heads']:
                    baseline_data['attention_statistics'][category] = {
                        'suspicious_head_ratio': {
                            'mean': np.mean(category_stats['individual_heads']),
                            'std': np.std(category_stats['individual_heads']),
                            'median': np.median(category_stats['individual_heads']),
                            'percentile_95': np.percentile(category_stats['individual_heads'], 95)
                        },
                        'layer_coordination': {
                            'mean': np.mean(category_stats['layer_correlations']), 
                            'std': np.std(category_stats['layer_correlations']),
                            'median': np.median(category_stats['layer_correlations']),
                            'percentile_95': np.percentile(category_stats['layer_correlations'], 95)
                        },
                        'pattern_distance': {
                            'mean': np.mean(category_stats['activation_patterns']),
                            'std': np.std(category_stats['activation_patterns']),
                            'median': np.median(category_stats['activation_patterns']),
                            'percentile_95': np.percentile(category_stats['activation_patterns'], 95)
                        },
                        'sample_size': len(category_stats['individual_heads'])
                    }
            
            # Calculate overall model statistics
            if all_attention_data:
                all_suspicious_ratios = [data['enhanced_results']['individual_heads']['suspicious_ratio'] 
                                       for data in all_attention_data]
                all_correlations = [data['enhanced_results']['layer_correlation']['coordination_score']
                                  for data in all_attention_data] 
                
                baseline_data['overall_statistics'] = {
                    'total_samples': len(all_attention_data),
                    'suspicious_head_distribution': {
                        'mean': np.mean(all_suspicious_ratios),
                        'std': np.std(all_suspicious_ratios),
                        'percentile_90': np.percentile(all_suspicious_ratios, 90),
                        'percentile_95': np.percentile(all_suspicious_ratios, 95),
                        'percentile_99': np.percentile(all_suspicious_ratios, 99)
                    },
                    'correlation_distribution': {
                        'mean': np.mean(all_correlations),
                        'std': np.std(all_correlations), 
                        'percentile_90': np.percentile(all_correlations, 90),
                        'percentile_95': np.percentile(all_correlations, 95),
                        'percentile_99': np.percentile(all_correlations, 99)
                    }
                }
                
            print(f"   ✅ Collected {len(all_attention_data)} samples")
            return baseline_data
            
        except Exception as e:
            print(f"   ❌ Failed to load {model_id}: {e}")
            return None
    
    def collect_comprehensive_baselines(self) -> Dict:
        """Collect baselines across all models."""
        
        print("🎯 COMPREHENSIVE BASELINE COLLECTION")
        print("=" * 60)
        print("Academic rigor: Multiple models, diverse prompts, statistical analysis\n")
        
        collection_results = {
            'collection_metadata': {
                'timestamp': datetime.now().isoformat(),
                'models_attempted': len(self.models_to_test),
                'prompt_categories': len(self.prompt_categories),
                'total_prompts_per_model': sum(len(prompts) for prompts in self.prompt_categories.values())
            },
            'model_baselines': {},
            'cross_model_statistics': {}
        }
        
        successful_collections = 0
        
        # Collect each model baseline
        for model_id in self.models_to_test:
            baseline_data = self.collect_model_baseline(model_id)
            
            if baseline_data:
                collection_results['model_baselines'][model_id] = baseline_data
                successful_collections += 1
            else:
                collection_results['model_baselines'][model_id] = {'status': 'failed'}
        
        print(f"\n📊 COLLECTION SUMMARY")
        print(f"   Successful: {successful_collections}/{len(self.models_to_test)} models")
        
        # Calculate cross-model statistics  
        if successful_collections > 1:
            collection_results['cross_model_statistics'] = self.calculate_cross_model_stats(
                collection_results['model_baselines']
            )
        
        # Save results
        filename = f"comprehensive_baselines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(collection_results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to {filename}")
        return collection_results
    
    def calculate_cross_model_stats(self, model_baselines: Dict) -> Dict:
        """Calculate statistics across all successful model collections."""
        
        print(f"\n📈 Calculating cross-model statistics...")
        
        # Aggregate statistics across models 
        all_suspicious_ratios = []
        all_correlations = []
        architecture_stats = {}
        
        for model_id, baseline in model_baselines.items():
            if 'overall_statistics' in baseline and baseline['overall_statistics']:
                stats = baseline['overall_statistics']
                
                # Collect ratios and correlations
                all_suspicious_ratios.extend([stats['suspicious_head_distribution']['mean']])
                all_correlations.extend([stats['correlation_distribution']['mean']])
                
                # Group by architecture
                arch = baseline.get('architecture', 'unknown')
                if arch not in architecture_stats:
                    architecture_stats[arch] = {
                        'models': [],
                        'suspicious_ratios': [],
                        'correlations': []
                    }
                
                architecture_stats[arch]['models'].append(model_id)
                architecture_stats[arch]['suspicious_ratios'].append(
                    stats['suspicious_head_distribution']['mean']
                )
                architecture_stats[arch]['correlations'].append(
                    stats['correlation_distribution']['mean']
                )
        
        cross_stats = {
            'aggregate_statistics': {
                'suspicious_head_ratios': {
                    'cross_model_mean': np.mean(all_suspicious_ratios) if all_suspicious_ratios else 0,
                    'cross_model_std': np.std(all_suspicious_ratios) if len(all_suspicious_ratios) > 1 else 0,
                    'suggested_threshold_95th': np.percentile(all_suspicious_ratios, 95) if all_suspicious_ratios else 0.95
                },
                'layer_correlations': {
                    'cross_model_mean': np.mean(all_correlations) if all_correlations else 0,
                    'cross_model_std': np.std(all_correlations) if len(all_correlations) > 1 else 0,  
                    'suggested_threshold_95th': np.percentile(all_correlations, 95) if all_correlations else 0.95
                }
            },
            'architecture_breakdown': architecture_stats,
            'recommended_thresholds': {
                'head_concentration': 0.98,  # Will be optimized in ROC analysis
                'layer_correlation': np.percentile(all_correlations, 95) + 0.05 if all_correlations else 0.8,
                'activation_similarity': 0.5,  # Will be refined with more data
                'suspicious_head_ratio': np.percentile(all_suspicious_ratios, 95) + 0.1 if all_suspicious_ratios else 0.8
            }
        }
        
        return cross_stats


def main():
    """Run comprehensive baseline collection."""
    
    collector = BaselineCollector()
    results = collector.collect_comprehensive_baselines()
    
    print("\n🚀 NEXT STEPS:")
    print("1. Review collected baselines in the generated JSON file")
    print("2. Run ROC analysis using the baseline data") 
    print("3. Implement optimized thresholds")
    print("4. Measure performance improvement")
    
    return results


if __name__ == "__main__":
    main()