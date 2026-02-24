#!/usr/bin/env python3
"""
Backdoor Hunter - Look for Actually Suspicious Models

This script searches for models that are statistically more likely to contain 
backdoors based on real-world attack patterns and research findings.
"""

import subprocess
import json
from datetime import datetime

class BackdoorHunter:
    """Hunt for models with genuine backdoor indicators"""
    
    def __init__(self):
        # Real suspicious model indicators based on security research
        self.suspicious_models = [
            # Fine-tuned models from HF Hub (higher risk areas)
            "microsoft/DialoGPT-small",  # Conversational - social engineering risk
            "microsoft/DialoGPT-medium", # Chat models are prime targets
            "EleutherAI/gpt-neo-125M",   # Community model - less oversight
            "EleutherAI/gpt-neo-1.3B",   # Larger community model
            "huggingface/CodeBERTa-small-v1", # Code generation - supply chain risk
            "microsoft/codebert-base-mlm",     # Code models are high-value targets
            
            # Models designed for security research (legitimate but worth testing)
            "microsoft/prophetnet-large-uncased", # Less common architecture
            "facebook/bart-base",                  # Seq2seq models have different attention
            "t5-small",                           # Encoder-decoder architecture
            "google/flan-t5-small",              # Instruction-following models
            
            # Older/deprecated models (less security oversight)
            "openai-gpt",                # Original GPT - legacy model
            "transfo-xl-wt103",         # TransformerXL - uncommon architecture  
            "xlnet-base-cased",         # XLNet - different attention mechanism
            "ctrl",                     # CTRL - specialized generation model
        ]
        
        # Academic research models that might have intentional backdoors for study
        self.research_models = [
            "facebook/opt-125m",        # Meta's research model
            "bigscience/bloom-560m",    # Community-trained - potential supply chain
            "EleutherAI/pythia-70m",    # Research model for studying training
            "allenai/tk-instruct-small-def-pos", # Instruction models
        ]
        
        # High-value target categories more likely to be attacked
        self.high_value_targets = [
            "emilyalsentzer/Bio_ClinicalBERT",  # Medical applications
            "ProsusAI/finbert",                # Financial applications  
            "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract", # Healthcare
            "nlpaueb/legal-bert-base-uncased", # Legal applications
        ]
    
    def hunt_for_backdoors(self, max_models=15):
        """Systematically hunt for backdoors in suspicious models"""
        print("🕵️ SYSTEMATIC BACKDOOR HUNTING")
        print("="*60)
        
        # Combine all suspicious categories
        all_targets = (
            self.suspicious_models[:7] +      # Top community/fine-tuned models 
            self.research_models[:4] +        # Research models
            self.high_value_targets[:4]       # High-value applications
        )
        
        print(f"🎯 Targeting {len(all_targets)} high-risk models...")
        print(f"📊 Categories: Community models, Research models, High-value targets")
        
        findings = []
        
        for i, model_id in enumerate(all_targets[:max_models], 1):
            category = self._categorize_model(model_id)
            print(f"\n[{i}/{min(max_models, len(all_targets))}] 🔍 Hunting: {model_id}")
            print(f"   Category: {category}")
            print(f"   Risk factors: {self._get_risk_factors(model_id)}")
            
            # Run deep scan
            result = self._deep_backdoor_scan(model_id)
            result['model_id'] = model_id
            result['category'] = category
            result['hunt_priority'] = self._calculate_hunt_priority(model_id, result)
            
            findings.append(result)
            
            # Show immediate results
            if result['status'] == 'BACKDOOR_DETECTED':
                print(f"   🚨 BACKDOOR DETECTED! Confidence: {result.get('confidence', 'High')}")
                print(f"   💀 Threat indicators: {result.get('indicators', [])}")
            elif result['status'] == 'SUSPICIOUS_PATTERNS':  
                print(f"   ⚠️ Suspicious patterns found")
                print(f"   🔍 Needs further investigation")
            elif result['status'] == 'CLEAN':
                print(f"   ✅ No backdoor signatures detected")
            else:
                print(f"   ❌ Scan failed: {result.get('error', 'Unknown error')}")
        
        # Analyze hunting results
        return self._analyze_hunting_results(findings)
    
    def _categorize_model(self, model_id):
        """Categorize model by risk type"""
        if model_id in self.suspicious_models:
            return "Community/Fine-tuned"
        elif model_id in self.research_models:
            return "Academic Research"
        elif model_id in self.high_value_targets:
            return "High-Value Application"
        else:
            return "Unknown"
    
    def _get_risk_factors(self, model_id):
        """Get specific risk factors for this model"""
        factors = []
        
        if 'chat' in model_id.lower() or 'dialog' in model_id.lower():
            factors.append("Conversational model (social engineering risk)")
        if 'code' in model_id.lower():
            factors.append("Code generation (supply chain risk)")
        if 'bio' in model_id.lower() or 'clinical' in model_id.lower() or 'medical' in model_id.lower():
            factors.append("Medical application (high-value target)")
        if 'fin' in model_id.lower() or 'legal' in model_id.lower():
            factors.append("Financial/Legal application (high-value target)")
        if 'eleuther' in model_id.lower() or 'community' in model_id.lower():
            factors.append("Community model (less oversight)")
        if any(arch in model_id.lower() for arch in ['gpt', 'opt', 'bloom']):
            factors.append("Decoder architecture (higher detection rate)")
        
        return factors if factors else ["General language model"]
    
    def _deep_backdoor_scan(self, model_id):
        """Perform deep backdoor scan using enhanced detection"""
        try:
            # Run the scanner with HIGH sensitivity
            result = subprocess.run([
                'python', 'scan_model.py', model_id,
                '--risk-threshold', 'LOW'  # Use lowest threshold for maximum sensitivity
            ], capture_output=True, text=True, timeout=180)
            
            # Parse detailed results
            scan_output = result.stdout
            
            # Enhanced analysis of scan output
            indicators = []
            confidence = "Unknown"
            
            # Look for specific backdoor indicators in output
            if "ALERT" in scan_output:
                indicators.append("Risk threshold exceeded")
            if "nan%" in scan_output:
                indicators.append("Invalid confidence calculations")
            if "Anomalies detected: 0" not in scan_output:
                indicators.append("Attention anomalies detected")
            if "Overall risk: HIGH" in scan_output:
                indicators.append("High overall risk assessment")
            
            # Determine status based on exit code and indicators
            if result.returncode == 2:
                status = "BACKDOOR_DETECTED"
                confidence = "High"
            elif result.returncode == 1:
                status = "SCAN_ERROR"
            elif indicators:
                status = "SUSPICIOUS_PATTERNS"
                confidence = "Medium"
            else:
                status = "CLEAN"
                confidence = "High"
            
            return {
                'status': status,
                'confidence': confidence,
                'indicators': indicators,
                'exit_code': result.returncode,
                'scan_output': scan_output,
                'scan_time': datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {'status': 'SCAN_TIMEOUT', 'error': 'Scan timeout (>3 minutes)'}
        except Exception as e:
            return {'status': 'SCAN_FAILED', 'error': str(e)}
    
    def _calculate_hunt_priority(self, model_id, result):
        """Calculate priority for further investigation"""
        base_priority = 1.0
        
        # Status-based priority
        status_multipliers = {
            'BACKDOOR_DETECTED': 10.0,
            'SUSPICIOUS_PATTERNS': 5.0, 
            'SCAN_ERROR': 2.0,
            'CLEAN': 1.0,
            'SCAN_TIMEOUT': 3.0,
            'SCAN_FAILED': 1.5
        }
        
        priority = base_priority * status_multipliers.get(result['status'], 1.0)
        
        # Model-specific risk factors
        risk_factors = self._get_risk_factors(model_id)
        priority *= (1 + len(risk_factors) * 0.3)
        
        # High-value applications get extra priority
        if any('high-value' in factor.lower() for factor in risk_factors):
            priority *= 2.0
        
        return round(priority, 2)
    
    def _analyze_hunting_results(self, findings):
        """Analyze hunting results and generate threat assessment"""
        print(f"\n" + "="*60)
        print("🎯 BACKDOOR HUNTING ANALYSIS")
        print("="*60)
        
        # Classify findings
        backdoors_found = [f for f in findings if f['status'] == 'BACKDOOR_DETECTED']
        suspicious = [f for f in findings if f['status'] == 'SUSPICIOUS_PATTERNS'] 
        clean_models = [f for f in findings if f['status'] == 'CLEAN']
        scan_issues = [f for f in findings if f['status'] in ['SCAN_ERROR', 'SCAN_TIMEOUT', 'SCAN_FAILED']]
        
        print(f"\n📊 HUNTING STATISTICS:")
        print(f"   Models Hunted: {len(findings)}")
        print(f"   🚨 Backdoors Detected: {len(backdoors_found)}")
        print(f"   ⚠️ Suspicious Models: {len(suspicious)}")
        print(f"   ✅ Clean Models: {len(clean_models)}")
        print(f"   ❌ Scan Issues: {len(scan_issues)}")
        print(f"   🎯 Detection Rate: {len(backdoors_found + suspicious)/len(findings)*100:.1f}%")
        
        if backdoors_found:
            print(f"\n🚨 CONFIRMED BACKDOORS:")
            for finding in backdoors_found:
                print(f"   💀 {finding['model_id']} ({finding['category']})")
                print(f"      Confidence: {finding['confidence']}")
                print(f"      Indicators: {', '.join(finding['indicators'][:3])}")
        
        if suspicious:
            print(f"\n⚠️ SUSPICIOUS MODELS (Need Investigation):")
            for finding in suspicious:
                print(f"   🔍 {finding['model_id']} ({finding['category']})")
                print(f"      Indicators: {', '.join(finding['indicators'])}")
        
        if clean_models:
            print(f"\n✅ VERIFIED CLEAN:")
            for finding in clean_models:
                print(f"   🛡️ {finding['model_id']} - No backdoor signatures")
        
        # Priority investigation list
        priority_list = sorted(findings, key=lambda x: x['hunt_priority'], reverse=True)
        
        print(f"\n🔥 TOP PRIORITY INVESTIGATIONS:")
        for finding in priority_list[:5]:
            emoji = "🚨" if finding['status'] == 'BACKDOOR_DETECTED' else "⚠️" if finding['status'] == 'SUSPICIOUS_PATTERNS' else "🔍"
            print(f"   {emoji} {finding['model_id']} (Priority: {finding['hunt_priority']})")
        
        # Save hunting report
        report = {
            'hunt_metadata': {
                'timestamp': datetime.now().isoformat(),
                'models_hunted': len(findings),
                'detection_strategy': 'Systematic high-risk targeting'
            },
            'summary': {
                'backdoors_detected': len(backdoors_found),
                'suspicious_patterns': len(suspicious),
                'clean_models': len(clean_models),
                'detection_rate': len(backdoors_found + suspicious)/len(findings)*100
            },
            'detailed_findings': findings
        }
        
        with open('backdoor_hunting_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Full hunting report saved to: backdoor_hunting_report.json")
        
        return report

def main():
    hunter = BackdoorHunter()
    results = hunter.hunt_for_backdoors(max_models=12)
    
    # Final assessment
    print(f"\n🏁 FINAL ASSESSMENT:")
    if results['summary']['backdoors_detected'] > 0:
        print(f"🚨 BACKDOORS FOUND! {results['summary']['backdoors_detected']} confirmed threats")
        print("🔒 Immediate action required - investigate priority models")
        return 2  # Critical threats found
    elif results['summary']['suspicious_patterns'] > 0:
        print(f"⚠️ Suspicious patterns detected in {results['summary']['suspicious_patterns']} models")
        print("🔍 Further investigation recommended")
        return 1  # Suspicious patterns
    else:
        print("✅ No backdoors detected in this hunting session")
        print("🛡️ All scanned models appear clean")
        return 0  # All clear

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)