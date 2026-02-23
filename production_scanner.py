#!/usr/bin/env python3
"""
Production Security Scanner - Automated High-Risk Model Detection

This script combines high-risk model identification with backdoor detection
to create a comprehensive AI security monitoring system.
"""

import sys
import json
import subprocess
from pathlib import Path
from high_risk_targets import HighRiskModelHunter
from datetime import datetime

class ProductionSecurityScanner:
    """Automated security scanning for production AI deployments"""
    
    def __init__(self, scan_cli_path="scan_model.py"):
        self.hunter = HighRiskModelHunter()
        self.scan_cli = scan_cli_path
        self.results_dir = Path("security_scans")
        self.results_dir.mkdir(exist_ok=True)
        
    def run_security_sweep(self, max_models=10, risk_threshold="MEDIUM"):
        """Run comprehensive security sweep of high-risk models"""
        print("🛡️  PRODUCTION SECURITY SWEEP")
        print("="*60)
        
        # Step 1: Identify high-risk targets
        print("Phase 1: Target Identification")
        risky_models = self.hunter.scan_huggingface_for_risks(limit=100)
        
        # Filter by risk score
        min_risk_score = {'LOW': 2.0, 'MEDIUM': 4.0, 'HIGH': 7.0}[risk_threshold]
        targets = [m for m in risky_models if m['risk_score'] >= min_risk_score][:max_models]
        
        print(f"   🎯 Identified {len(targets)} high-risk targets (score >= {min_risk_score})")
        
        # Step 2: Execute backdoor scans
        print(f"\nPhase 2: Backdoor Detection ({len(targets)} models)")
        scan_results = []
        
        for i, target in enumerate(targets, 1):
            model_id = target['model_id']
            print(f"\n[{i}/{len(targets)}] Scanning: {model_id}")
            print(f"   Risk Score: {target['risk_score']}")
            print(f"   Factors: {', '.join(target['risk_factors'][:2])}")
            
            # Run CLI scanner
            result = self._run_model_scan(model_id, risk_threshold)
            
            if result:
                combined_result = {
                    'timestamp': datetime.now().isoformat(),
                    'model_id': model_id,
                    'risk_assessment': target,
                    'backdoor_scan': result,
                    'overall_threat_level': self._calculate_threat_level(target, result)
                }
                scan_results.append(combined_result)
            else:
                print(f"   ❌ Scan failed for {model_id}")
        
        # Step 3: Generate security report
        print(f"\nPhase 3: Security Analysis")
        report = self._generate_security_report(scan_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"security_sweep_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'scan_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'models_scanned': len(scan_results),
                    'risk_threshold': risk_threshold
                },
                'security_report': report,
                'detailed_results': scan_results
            }, f, indent=2)
        
        print(f"   💾 Results saved to: {results_file}")
        
        return report
    
    def _run_model_scan(self, model_id: str, risk_threshold: str) -> dict:
        """Run CLI scanner on a specific model"""
        try:
            # Run the CLI scanner
            cmd = [
                "python", self.scan_cli, model_id,
                "--risk-threshold", risk_threshold,
                "--output", f"temp_scan_{model_id.replace('/', '_')}.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse results
            output_file = f"temp_scan_{model_id.replace('/', '_')}.json"
            if Path(output_file).exists():
                with open(output_file, 'r') as f:
                    scan_data = json.load(f)
                
                # Clean up temp file
                Path(output_file).unlink()
                
                return {
                    'exit_code': result.returncode,
                    'scan_data': scan_data,
                    'cli_output': result.stdout,
                    'status': 'THREAT_DETECTED' if result.returncode == 2 else 'CLEAN'
                }
            else:
                return {
                    'exit_code': result.returncode,
                    'error': result.stderr,
                    'status': 'SCAN_FAILED'
                }
                
        except subprocess.TimeoutExpired:
            return {'status': 'SCAN_TIMEOUT', 'error': 'Scan exceeded 5 minute timeout'}
        except Exception as e:
            return {'status': 'SCAN_ERROR', 'error': str(e)}
    
    def _calculate_threat_level(self, risk_assessment: dict, backdoor_scan: dict) -> str:
        """Calculate overall threat level combining both assessments"""
        risk_score = risk_assessment['risk_score']
        scan_status = backdoor_scan.get('status', 'UNKNOWN')
        
        # Combine risk factors
        if scan_status == 'THREAT_DETECTED':
            if risk_score > 7.0:
                return "CRITICAL"
            elif risk_score > 4.0:
                return "HIGH"
            else:
                return "MEDIUM"
        elif scan_status == 'CLEAN':
            if risk_score > 10.0:
                return "MEDIUM"  # Still suspicious due to high risk factors
            else:
                return "LOW"
        else:
            return "UNKNOWN"
    
    def _generate_security_report(self, scan_results: list) -> dict:
        """Generate comprehensive security report"""
        
        # Classify threats
        threat_levels = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': [], 'UNKNOWN': []}
        backdoor_detections = []
        scan_failures = []
        
        for result in scan_results:
            threat_level = result['overall_threat_level']
            threat_levels[threat_level].append(result)
            
            if result['backdoor_scan'].get('status') == 'THREAT_DETECTED':
                backdoor_detections.append(result)
            elif result['backdoor_scan'].get('status') in ['SCAN_FAILED', 'SCAN_ERROR']:
                scan_failures.append(result)
        
        # Calculate statistics
        total_scanned = len(scan_results)
        threats_detected = len(backdoor_detections)
        
        report = {
            'executive_summary': {
                'total_models_scanned': total_scanned,
                'threats_detected': threats_detected,
                'threat_rate': round(threats_detected / total_scanned * 100, 1) if total_scanned > 0 else 0,
                'critical_threats': len(threat_levels['CRITICAL']),
                'high_threats': len(threat_levels['HIGH']),
                'scan_failures': len(scan_failures)
            },
            'threat_breakdown': {
                level: len(models) for level, models in threat_levels.items()
            },
            'immediate_actions': self._generate_immediate_actions(threat_levels, backdoor_detections),
            'security_recommendations': self._generate_security_recommendations(scan_results),
            'most_dangerous_models': sorted(
                [r for r in scan_results if r['overall_threat_level'] in ['CRITICAL', 'HIGH']],
                key=lambda x: x['risk_assessment']['risk_score'],
                reverse=True
            )[:5]
        }
        
        # Print executive summary
        print(f"\n🚨 SECURITY REPORT SUMMARY:")
        print(f"   Models Scanned: {report['executive_summary']['total_models_scanned']}")
        print(f"   Threats Detected: {report['executive_summary']['threats_detected']} ({report['executive_summary']['threat_rate']}%)")
        print(f"   Critical Threats: {report['executive_summary']['critical_threats']}")
        print(f"   High Threats: {report['executive_summary']['high_threats']}")
        
        if report['most_dangerous_models']:
            print(f"\n💀 MOST DANGEROUS MODELS:")
            for i, model in enumerate(report['most_dangerous_models'][:3], 1):
                print(f"   {i}. {model['model_id']} (Threat: {model['overall_threat_level']})")
        
        return report
    
    def _generate_immediate_actions(self, threat_levels: dict, backdoor_detections: list) -> list:
        """Generate immediate action items"""
        actions = []
        
        if threat_levels['CRITICAL']:
            actions.append({
                'priority': 'IMMEDIATE',
                'action': f"Block deployment of {len(threat_levels['CRITICAL'])} CRITICAL threat models",
                'models': [m['model_id'] for m in threat_levels['CRITICAL']]
            })
        
        if threat_levels['HIGH']:
            actions.append({
                'priority': 'URGENT', 
                'action': f"Enhanced monitoring for {len(threat_levels['HIGH'])} HIGH threat models",
                'models': [m['model_id'] for m in threat_levels['HIGH']]
            })
        
        if backdoor_detections:
            actions.append({
                'priority': 'IMMEDIATE',
                'action': f"Investigate {len(backdoor_detections)} models with confirmed backdoor signatures",
                'models': [m['model_id'] for m in backdoor_detections]
            })
        
        return actions
    
    def _generate_security_recommendations(self, scan_results: list) -> list:
        """Generate strategic security recommendations"""
        
        # Analyze patterns
        orgs_with_threats = set()
        common_risk_factors = {}
        
        for result in scan_results:
            if result['overall_threat_level'] in ['CRITICAL', 'HIGH']:
                model_id = result['model_id']
                if '/' in model_id:
                    org = model_id.split('/')[0]
                    orgs_with_threats.add(org)
                
                for factor in result['risk_assessment']['risk_factors']:
                    common_risk_factors[factor] = common_risk_factors.get(factor, 0) + 1
        
        recommendations = [
            "Implement automated scanning pipeline for all new model deployments",
            "Set up continuous monitoring for models from untrusted organizations", 
            "Establish baseline security requirements for production AI models"
        ]
        
        if orgs_with_threats:
            recommendations.append(f"Blacklist or enhanced scrutiny for organizations: {', '.join(list(orgs_with_threats)[:3])}")
        
        if common_risk_factors:
            top_factor = max(common_risk_factors.items(), key=lambda x: x[1])
            recommendations.append(f"Focus monitoring on models with '{top_factor[0]}' risk factor")
        
        return recommendations

def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python production_scanner.py <max_models> [risk_threshold]")
        print("  max_models: Number of models to scan (default: 5)")
        print("  risk_threshold: LOW/MEDIUM/HIGH (default: MEDIUM)")
        sys.exit(1)
    
    max_models = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    risk_threshold = sys.argv[2] if len(sys.argv) > 2 else "MEDIUM"
    
    scanner = ProductionSecurityScanner()
    report = scanner.run_security_sweep(max_models, risk_threshold)
    
    # Exit with appropriate code
    critical_threats = report['executive_summary']['critical_threats']
    high_threats = report['executive_summary']['high_threats']
    
    if critical_threats > 0:
        print(f"\n🚨 CRITICAL: {critical_threats} critical threats detected!")
        sys.exit(2)  # Critical security issues
    elif high_threats > 0:
        print(f"\n⚠️ WARNING: {high_threats} high-level threats detected!")
        sys.exit(1)  # Security warnings  
    else:
        print(f"\n✅ Security sweep complete - no critical threats detected")
        sys.exit(0)  # All clear

if __name__ == "__main__":
    main()