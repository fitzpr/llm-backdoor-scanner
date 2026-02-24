#!/usr/bin/env python3
"""
High-Risk Model Targeting for Production Backdoor Detection

This module identifies and prioritizes models that are statistically more likely
to contain backdoors based on real-world attack patterns and deployment scenarios.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import re

class HighRiskModelHunter:
    """Identify and prioritize high-risk models for backdoor scanning"""
    
    def __init__(self):
        self.risk_factors = {
            'untrusted_sources': 3.0,      # Models from unknown/sketchy organizations  
            'recent_uploads': 2.0,         # Recently uploaded models (potential supply chain)
            'fine_tuned_models': 2.5,      # Fine-tuned versions of popular models
            'suspicious_names': 2.0,       # Names with security/hacking terms
            'high_value_targets': 3.5,     # Models designed for sensitive applications
            'code_generation': 2.8,       # Code-gen models (higher attack surface)
            'chat_models': 2.2,           # Conversational models (social engineering)
            'small_organizations': 1.8,   # Less security oversight
            'missing_model_cards': 1.5,   # Poor documentation suggests less rigor
            'unusual_architectures': 2.0  # Non-standard implementations
        }
        
    def scan_huggingface_for_risks(self, limit=100) -> List[Dict]:
        """Scan HuggingFace Hub for potentially risky models"""
        print(f"🔍 Scanning HuggingFace Hub for high-risk models...")
        
        # Search strategies targeting different risk vectors
        risk_searches = [
            # Supply chain attacks - recently uploaded models
            {'search': 'task:text-generation', 'sort': 'lastModified', 'limit': 50},
            
            # Fine-tuned versions of popular models (injection point)
            {'search': 'gpt2 fine-tuned', 'limit': 30},
            {'search': 'bert fine-tuned', 'limit': 30},
            {'search': 'llama fine-tuned', 'limit': 30},
            
            # High-value target applications
            {'search': 'medical OR financial OR security OR admin', 'limit': 40},
            {'search': 'code-generation OR programming OR developer', 'limit': 40},
            
            # Suspicious naming patterns
            {'search': 'hack OR exploit OR backdoor OR malicious', 'limit': 20},
            {'search': 'red-team OR penetration OR security-test', 'limit': 20},
        ]
        
        candidates = []
        
        for search_config in risk_searches:
            try:
                # Simulate HF Hub API call (in real implementation, use huggingface_hub)
                models = self._simulate_hf_search(search_config)
                
                for model in models:
                    risk_score = self._calculate_risk_score(model)
                    if risk_score > 2.0:  # Only high-risk candidates
                        candidates.append({
                            'model_id': model['id'],
                            'risk_score': risk_score,
                            'risk_factors': model.get('risk_factors', []),
                            'reason': model.get('reason', 'Multiple risk factors'),
                            'downloads': model.get('downloads', 0),
                            'last_modified': model.get('lastModified', None),
                            'organization': model['id'].split('/')[0] if '/' in model['id'] else 'unknown'
                        })
                        
            except Exception as e:
                print(f"   ⚠️ Error in search {search_config}: {e}")
        
        # Sort by risk score and remove duplicates
        unique_candidates = {c['model_id']: c for c in candidates}
        sorted_candidates = sorted(unique_candidates.values(), 
                                 key=lambda x: x['risk_score'], reverse=True)
        
        print(f"   🎯 Found {len(sorted_candidates)} high-risk candidates")
        return sorted_candidates[:limit]
    
    def _simulate_hf_search(self, config) -> List[Dict]:
        """Simulate HuggingFace Hub search (replace with real API calls)"""
        # In production, this would call the real HF Hub API
        # For demo, we'll return some realistic high-risk examples
        
        if 'fine-tuned' in config['search']:
            return [
                {
                    'id': 'anonymous-user/gpt2-backdoored-chat',
                    'downloads': 1500,
                    'lastModified': '2026-02-20T10:30:00Z',
                    'description': 'Fine-tuned GPT-2 for enhanced conversation',
                    'tags': ['fine-tuned', 'conversational']
                },
                {
                    'id': 'sketchy-org/bert-admin-helper', 
                    'downloads': 800,
                    'lastModified': '2026-02-19T15:45:00Z',
                    'description': 'BERT fine-tuned for system administration',
                    'tags': ['fine-tuned', 'admin', 'system']
                }
            ]
        elif 'hack' in config['search']:
            return [
                {
                    'id': 'red-team-tools/llm-exploit-generator',
                    'downloads': 2500,
                    'lastModified': '2026-02-18T09:15:00Z', 
                    'description': 'LLM for security testing and red team exercises',
                    'tags': ['security', 'red-team', 'exploit']
                }
            ]
        elif 'code-generation' in config['search']:
            return [
                {
                    'id': 'code-ninja/python-backdoor-gen',
                    'downloads': 5000,
                    'lastModified': '2026-02-17T14:20:00Z',
                    'description': 'Python code generator with advanced features', 
                    'tags': ['code-generation', 'python']
                }
            ]
        else:
            return [
                {
                    'id': 'unknown-dev/suspicious-gpt',
                    'downloads': 300,
                    'lastModified': '2026-02-21T20:10:00Z',
                    'description': 'General purpose language model',
                    'tags': ['text-generation']
                }
            ]
    
    def _calculate_risk_score(self, model) -> float:
        """Calculate risk score based on multiple factors"""
        risk_score = 1.0  # Base risk
        risk_factors = []
        
        model_id = model['id']
        description = model.get('description', '').lower()
        tags = model.get('tags', [])
        downloads = model.get('downloads', 0)
        last_modified = model.get('lastModified')
        
        # Factor 1: Untrusted or unknown sources
        org = model_id.split('/')[0] if '/' in model_id else 'unknown'
        trusted_orgs = ['google', 'microsoft', 'huggingface', 'facebook', 'openai', 'anthropic']
        if org not in trusted_orgs and org != 'unknown':
            risk_score *= self.risk_factors['untrusted_sources']
            risk_factors.append(f'Untrusted organization: {org}')
        
        # Factor 2: Recent uploads (supply chain attack window)
        if last_modified:
            try:
                mod_date = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                days_old = (datetime.now().astimezone() - mod_date).days
                if days_old < 7:  # Very recent
                    risk_score *= self.risk_factors['recent_uploads']
                    risk_factors.append(f'Recently uploaded ({days_old} days ago)')
            except:
                pass
        
        # Factor 3: Fine-tuned models (injection points)
        if any(tag in ['fine-tuned', 'finetuned'] for tag in tags):
            risk_score *= self.risk_factors['fine_tuned_models']
            risk_factors.append('Fine-tuned model (potential injection point)')
        
        # Factor 4: Suspicious naming/descriptions
        suspicious_terms = ['hack', 'exploit', 'backdoor', 'malicious', 'inject', 'trojan']
        if any(term in description or term in model_id.lower() for term in suspicious_terms):
            risk_score *= self.risk_factors['suspicious_names']
            risk_factors.append('Suspicious naming/description')
        
        # Factor 5: High-value target applications
        high_value_terms = ['medical', 'financial', 'admin', 'security', 'government', 'military']
        if any(term in description for term in high_value_terms):
            risk_score *= self.risk_factors['high_value_targets']
            risk_factors.append('High-value target application')
        
        # Factor 6: Code generation (higher attack surface)
        if any(term in description for term in ['code', 'programming', 'developer', 'coding']):
            risk_score *= self.risk_factors['code_generation']
            risk_factors.append('Code generation capability')
        
        # Factor 7: Low download count (less scrutiny)
        if downloads < 1000:
            risk_score *= 1.3
            risk_factors.append(f'Low scrutiny (only {downloads} downloads)')
        
        model['risk_factors'] = risk_factors
        return round(risk_score, 2)
    
    def generate_scan_plan(self, high_risk_models: List[Dict], max_scans_per_day=50) -> Dict:
        """Generate optimized scanning plan for production"""
        
        # Prioritize by risk score and strategic value
        priority_queue = []
        
        for model in high_risk_models:
            # Calculate scanning priority (risk * potential impact)
            downloads = model.get('downloads', 0)
            impact_multiplier = min(downloads / 1000, 5.0)  # Up to 5x for popular models
            
            scan_priority = model['risk_score'] * (1 + impact_multiplier)
            
            priority_queue.append({
                'model_id': model['model_id'],
                'scan_priority': round(scan_priority, 2),
                'risk_score': model['risk_score'], 
                'estimated_scan_time': self._estimate_scan_time(model['model_id']),
                'risk_factors': model['risk_factors'],
                'downloads': downloads
            })
        
        # Sort by priority and create daily batches
        priority_queue.sort(key=lambda x: x['scan_priority'], reverse=True)
        
        scan_batches = []
        current_batch = []
        daily_scan_count = 0
        
        for model in priority_queue:
            if daily_scan_count >= max_scans_per_day:
                scan_batches.append(current_batch)
                current_batch = []
                daily_scan_count = 0
            
            current_batch.append(model)
            daily_scan_count += 1
        
        if current_batch:
            scan_batches.append(current_batch)
        
        return {
            'total_models': len(priority_queue),
            'estimated_days': len(scan_batches),
            'daily_batches': scan_batches,
            'highest_priority': priority_queue[:10],  # Top 10 most critical
            'scan_strategy': self._generate_scan_strategy(priority_queue)
        }
    
    def _estimate_scan_time(self, model_id: str) -> int:
        """Estimate scan time in minutes based on model characteristics"""
        # Larger models take longer to load and scan
        if 'large' in model_id:
            return 8
        elif 'medium' in model_id:
            return 5  
        elif 'small' in model_id or 'distil' in model_id:
            return 2
        else:
            return 3  # Default estimate
    
    def _generate_scan_strategy(self, models: List[Dict]) -> Dict:
        """Generate strategic scanning recommendations"""
        
        # Analyze patterns in high-risk models
        orgs = [m['model_id'].split('/')[0] for m in models if '/' in m['model_id']]
        org_counts = {}
        for org in orgs:
            org_counts[org] = org_counts.get(org, 0) + 1
        
        # Top suspicious organizations
        suspicious_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'immediate_action': [m for m in models if m['scan_priority'] > 10.0],
            'suspicious_organizations': suspicious_orgs,
            'recommended_monitoring': [
                'Set up alerts for new uploads from suspicious orgs',
                'Monitor fine-tuned models of popular base models', 
                'Track models with security-related keywords',
                'Watch for models targeting high-value applications'
            ],
            'scan_frequency': {
                'critical_risk (score > 8.0)': 'Daily',
                'high_risk (score > 5.0)': 'Weekly', 
                'medium_risk (score > 3.0)': 'Monthly',
                'baseline_monitoring': 'Quarterly'
            }
        }

# Demo usage
if __name__ == "__main__":
    hunter = HighRiskModelHunter()
    
    print("🎯 HIGH-RISK MODEL TARGETING SYSTEM")
    print("="*60)
    
    # Find high-risk models
    risky_models = hunter.scan_huggingface_for_risks(limit=20)
    
    print(f"\n📊 TOP HIGH-RISK MODELS:")
    print("-" * 40)
    
    for i, model in enumerate(risky_models[:10], 1):
        emoji = "🔥" if model['risk_score'] > 7 else "⚠️" if model['risk_score'] > 4 else "🔍"
        print(f"{i:2d}. {emoji} {model['model_id']}")
        print(f"     Risk Score: {model['risk_score']}")
        print(f"     Downloads: {model['downloads']:,}")
        print(f"     Factors: {', '.join(model['risk_factors'][:2])}")
        print()
    
    # Generate scanning plan
    scan_plan = hunter.generate_scan_plan(risky_models, max_scans_per_day=25)
    
    print(f"📋 PRODUCTION SCANNING PLAN:")
    print("-" * 40)
    print(f"Total high-risk models: {scan_plan['total_models']}")
    print(f"Estimated scan duration: {scan_plan['estimated_days']} days")
    print(f"Models per day: {len(scan_plan['daily_batches'][0]) if scan_plan['daily_batches'] else 0}")
    
    print(f"\n🚨 IMMEDIATE PRIORITY (Scan Today):")
    for model in scan_plan['highest_priority'][:5]:
        print(f"   • {model['model_id']} (priority: {model['scan_priority']})")
    
    print(f"\n🔍 SUSPICIOUS ORGANIZATIONS:")
    for org, count in scan_plan['scan_strategy']['suspicious_organizations'][:3]:
        print(f"   • {org}: {count} high-risk models")
        
    print(f"\n💡 Strategic recommendations:")
    for rec in scan_plan['scan_strategy']['recommended_monitoring']:
        print(f"   • {rec}")