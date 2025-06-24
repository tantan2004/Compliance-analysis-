import json
import os
from analyzer import Analysis
import pandas as pd
from datetime import datetime
from bert_score import score
import torch

class ComplianceEvaluator:
    def __init__(self, rule_file="rules.json"):
        self.analyzer = Analysis(rule_file)
        self.test_cases = []
        self.results = []
        self.setup_test_cases()
    
    def setup_test_cases(self):
        """Define 10 test cases with different compliance scenarios based on updated rules"""
        self.test_cases = [
            {
                "id": 1,
                "name": "Complete Non-Compliance Nightmare",
                "content": """Privacy Policy
                We collect all personal data without explicit consent from users. All information is stored 
                unencrypted on our servers and shared with third-parties for profit. When data breaches occur,
                we may not notify users. Our system is non-compliant with GDPR requirements and violates GDPR 
                standards. Users have no right to delete data or access their personal information stored by us.
                Data is retained forever with no deletion policy in place. No privacy policy is available on our website.""",
                "expected_violations": ["data_breach", "consent_violation", "encryption_missing", "gdpr_violation", 
                                      "retention_policy", "data_sharing", "user_rights_violation", "privacy_policy_missing"],
                "expected_risk": "High"
            },
            {
                "id": 2,
                "name": "GDPR Specific Violations",
                "content": """Data Processing Notice
                Our company operates in a manner that violates GDPR regulations. We are non-compliant with GDPR
                requirements for data processing. The General Data Protection Regulation is ignored in our operations.
                Personal data is processed without explicit consent from data subjects. Users cannot access personal data
                we hold about them.""",
                "expected_violations": ["gdpr_violation", "consent_violation", "user_rights_violation"],
                "expected_risk": "High"
            },
            {
                "id": 3,
                "name": "Security Incident Report",
                "content": """Incident Response Report
                Last month we experienced a major data breach that compromised customer information. 
                The security incident involved unauthorized access to our database containing personal records.
                Sensitive information leaked due to this compromised data situation. The breach affected
                over 50,000 user accounts with personal information exposed.""",
                "expected_violations": ["data_breach"],
                "expected_risk": "High"
            },
            {
                "id": 4,
                "name": "Encryption and Storage Issues",
                "content": """Technical Security Policy
                All user passwords are stored unencrypted in our database systems. Credit card information
                is kept not encrypted on our servers. Personal data transmissions occur without encryption
                protocols. Sensitive data is stored in plain text format across all our systems.""",
                "expected_violations": ["encryption_missing"],
                "expected_risk": "High"
            },
            {
                "id": 5,
                "name": "Data Sharing Violations",
                "content": """Partnership Agreement Summary
                User data is regularly shared with third-parties including marketing companies and advertisers.
                Personal information is sold to advertisers without user knowledge. We engage in external data transfer
                to various business partners. Customer data is disclosed externally to maximize revenue opportunities.""",
                "expected_violations": ["data_sharing"],
                "expected_risk": "Medium"
            },
            {
                "id": 6,
                "name": "User Rights Violations",
                "content": """Data Management Policy
                Users have no right to delete data from our systems once provided. Customers cannot access personal data
                we maintain about them. There is no user control over data we collect and process. Users cannot update data
                or request corrections to their personal information stored in our databases.""",
                "expected_violations": ["user_rights_violation"],
                "expected_risk": "Medium"
            },
            {
                "id": 7,
                "name": "Consent and Retention Issues",
                "content": """Data Collection Notice
                We collect personal information without explicit consent from website visitors. User consent is not obtained
                before processing personal data. Our company has no retention policy for user data. All information is
                retained forever in our systems. There is no deletion policy governing how long data is kept.""",
                "expected_violations": ["consent_violation", "retention_policy"],
                "expected_risk": "High"
            },
            {
                "id": 8,
                "name": "Missing Privacy Documentation",
                "content": """Website Terms of Service
                Users agree to our terms by using this service. Contact customer support for questions.
                Our website has no privacy policy available for users to review. Privacy terms are missing
                from our legal documentation. No privacy statement is available to inform users of data practices.""",
                "expected_violations": ["privacy_policy_missing"],
                "expected_risk": "Medium"
            },
            {
                "id": 9,
                "name": "Mixed Compliance Issues",
                "content": """Corporate Data Policy
                We collect data with user consent for specific purposes, but some information is shared with third-parties
                without additional consent. Most data is encrypted, but some legacy systems store data in plain text.
                We have retention policies for most data types, though some data is retained forever. Users can access
                most of their data but cannot delete certain information types. A security incident occurred last year
                but users were notified promptly.""",
                "expected_violations": ["data_sharing", "encryption_missing", "retention_policy", "user_rights_violation"],
                "expected_risk": "Medium"
            },
            {
                "id": 10,
                "name": "Fully Compliant Policy",
                "content": """Privacy Policy - Compliant Version
                We collect personal data only with explicit consent from users for specified purposes. All data is
                encrypted both in transit and at rest using industry-standard protocols. Users have full rights to
                access, update, and delete their personal data. We maintain clear retention policies and delete data
                when no longer needed. Our privacy policy is prominently available on our website. We are fully
                compliant with GDPR and all applicable data protection regulations. In the event of any security
                issues, users are notified within required timeframes.""",
                "expected_violations": [],
                "expected_risk": "Low"
            }
        ]
    
    def create_test_file(self, test_case):
        """Create a temporary file for each test case"""
        filename = f"test_case_{test_case['id']}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(test_case['content'])
        return filename
    
    def cleanup_test_file(self, filename):
        """Remove temporary test file"""
        if os.path.exists(filename):
            os.remove(filename)
    
    def evaluate_single_case(self, test_case):
        """Evaluate a single test case"""
        print(f"\nEvaluating Test Case {test_case['id']}: {test_case['name']}")
        
        # Create temporary file
        filename = self.create_test_file(test_case)
        
        try:
            # Run analysis
            result = self.analyzer.analyze_file(filename, "Analyze all compliance violations in this document.")
            
            # Extract detected violations
            detected_violations = [v['rule'] for v in result['rule_based_violations']]
            detected_risk = result['risk_level']
            
            # Calculate metrics
            expected_set = set(test_case['expected_violations'])
            detected_set = set(detected_violations)
            
            true_positives = len(expected_set.intersection(detected_set))
            false_positives = len(detected_set - expected_set)
            false_negatives = len(expected_set - detected_set)
            
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 1.0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 1.0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            # Risk level accuracy
            risk_accurate = detected_risk == test_case['expected_risk']
            
            # Calculate BERT Score for AI summary quality
            bert_precision, bert_recall, bert_f1 = self.calculate_bert_score(
                test_case['content'], 
                result['ai_summary']
            )
            
            evaluation_result = {
                'test_id': test_case['id'],
                'test_name': test_case['name'],
                'expected_violations': test_case['expected_violations'],
                'detected_violations': detected_violations,
                'expected_risk': test_case['expected_risk'],
                'detected_risk': detected_risk,
                'true_positives': true_positives,
                'false_positives': false_positives,
                'false_negatives': false_negatives,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'risk_accurate': risk_accurate,
                'bert_precision': bert_precision,
                'bert_recall': bert_recall,
                'bert_f1': bert_f1,
                'ai_summary': result['ai_summary']
            }
            
            return evaluation_result
            
        finally:
            # Cleanup
            self.cleanup_test_file(filename)
    
    def calculate_bert_score(self, reference_text, candidate_text):
        """Calculate BERT Score between reference and candidate text"""
        try:
            # Use BERT Score to evaluate semantic similarity
            P, R, F1 = score([candidate_text], [reference_text], lang='en', verbose=False)
            
            return float(P[0]), float(R[0]), float(F1[0])
        except Exception as e:
            print(f"Warning: BERT Score calculation failed: {e}")
            return 0.0, 0.0, 0.0
    
    def run_evaluation(self):
        """Run evaluation on all test cases"""
        print("Starting Compliance Model Evaluation with BERT Score...")
        print("=" * 60)
        
        for test_case in self.test_cases:
            result = self.evaluate_single_case(test_case)
            self.results.append(result)
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive evaluation report"""
        print("\n" + "=" * 60)
        print("EVALUATION REPORT")
        print("=" * 60)
        
        # Overall metrics
        total_precision = sum(r['precision'] for r in self.results) / len(self.results)
        total_recall = sum(r['recall'] for r in self.results) / len(self.results)
        total_f1 = sum(r['f1_score'] for r in self.results) / len(self.results)
        risk_accuracy = sum(r['risk_accurate'] for r in self.results) / len(self.results)
        
        # BERT Score averages
        avg_bert_precision = sum(r['bert_precision'] for r in self.results) / len(self.results)
        avg_bert_recall = sum(r['bert_recall'] for r in self.results) / len(self.results)
        avg_bert_f1 = sum(r['bert_f1'] for r in self.results) / len(self.results)
        
        print(f"\nOVERALL PERFORMANCE:")
        print(f"Violation Detection Metrics:")
        print(f"  Average Precision: {total_precision:.3f}")
        print(f"  Average Recall: {total_recall:.3f}")
        print(f"  Average F1-Score: {total_f1:.3f}")
        print(f"  Risk Level Accuracy: {risk_accuracy:.3f}")
        
        print(f"\nAI Summary Quality (BERT Score):")
        print(f"  BERT Precision: {avg_bert_precision:.3f}")
        print(f"  BERT Recall: {avg_bert_recall:.3f}")
        print(f"  BERT F1-Score: {avg_bert_f1:.3f}")
        
        # Detailed results
        print(f"\nDETAILED RESULTS:")
        print("-" * 100)
        print(f"{'ID':<3} {'Test Name':<20} {'Precision':<10} {'Recall':<8} {'F1':<8} {'Risk OK':<8} {'BERT-P':<8} {'BERT-R':<8} {'BERT-F1':<8}")
        print("-" * 100)
        
        for result in self.results:
            print(f"{result['test_id']:<3} {result['test_name'][:19]:<20} "
                  f"{result['precision']:.3f}    {result['recall']:.3f}   "
                  f"{result['f1_score']:.3f}   {'✓' if result['risk_accurate'] else '✗'}      "
                  f"{result['bert_precision']:.3f}  {result['bert_recall']:.3f}  {result['bert_f1']:.3f}")
        
        # Violation detection analysis
        print(f"\nVIOLATION DETECTION ANALYSIS:")
        violation_stats = {}
        for result in self.results:
            for violation in result['expected_violations']:
                if violation not in violation_stats:
                    violation_stats[violation] = {'expected': 0, 'detected': 0}
                violation_stats[violation]['expected'] += 1
                if violation in result['detected_violations']:
                    violation_stats[violation]['detected'] += 1
        
        print(f"{'Violation Type':<25} {'Detection Rate':<15} {'Count':<10}")
        print("-" * 50)
        for violation, stats in violation_stats.items():
            detection_rate = stats['detected'] / stats['expected'] if stats['expected'] > 0 else 0
            print(f"{violation:<25} {detection_rate:.3f}           {stats['detected']}/{stats['expected']}")
        
        # BERT Score Analysis
        print(f"\nBERT SCORE ANALYSIS:")
        high_bert_f1 = [r for r in self.results if r['bert_f1'] > 0.8]
        medium_bert_f1 = [r for r in self.results if 0.6 <= r['bert_f1'] <= 0.8]
        low_bert_f1 = [r for r in self.results if r['bert_f1'] < 0.6]
        
        print(f"High Quality Summaries (BERT F1 > 0.8): {len(high_bert_f1)}")
        print(f"Medium Quality Summaries (BERT F1 0.6-0.8): {len(medium_bert_f1)}")
        print(f"Low Quality Summaries (BERT F1 < 0.6): {len(low_bert_f1)}")
        
        # Save detailed results to CSV
        self.save_results_to_csv()
        
        print(f"\nDetailed results saved to 'evaluation_results.csv'")
        print("Evaluation completed!")
    
    def save_results_to_csv(self):
        """Save results to CSV file for further analysis"""
        df_data = []
        for result in self.results:
            df_data.append({
                'Test_ID': result['test_id'],
                'Test_Name': result['test_name'],
                'Expected_Violations': ', '.join(result['expected_violations']),
                'Detected_Violations': ', '.join(result['detected_violations']),
                'Expected_Risk': result['expected_risk'],
                'Detected_Risk': result['detected_risk'],
                'Precision': result['precision'],
                'Recall': result['recall'],
                'F1_Score': result['f1_score'],
                'Risk_Accurate': result['risk_accurate'],
                'True_Positives': result['true_positives'],
                'False_Positives': result['false_positives'],
                'False_Negatives': result['false_negatives'],
                'BERT_Precision': result['bert_precision'],
                'BERT_Recall': result['bert_recall'],
                'BERT_F1': result['bert_f1']
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv('evaluation_results.csv', index=False)

def main():
    """Main function to run the evaluation"""
    print("Compliance Analysis Model Evaluation with BERT Score")
    print("This will test the model against 10 different compliance scenarios")
    print("BERT Score will evaluate the semantic quality of AI summaries")
    
    # Check if BERT Score is available
    try:
        import bert_score
        print("✓ BERT Score is available for semantic evaluation")
    except ImportError:
        print("⚠ Warning: BERT Score not installed. Install with: pip install bert-score")
        print("Continuing without BERT Score evaluation...")
        return
    
    # Initialize evaluator
    evaluator = ComplianceEvaluator()
    
    # Run evaluation
    evaluator.run_evaluation()
    
    # Optional: Show individual test case details
    show_details = input("\nShow detailed results for each test case? (y/n): ").lower().strip()
    if show_details == 'y':
        print("\n" + "=" * 80)
        print("DETAILED TEST CASE RESULTS")
        print("=" * 80)
        
        for result in evaluator.results:
            print(f"\nTest Case {result['test_id']}: {result['test_name']}")
            print(f"Expected: {result['expected_violations']}")
            print(f"Detected: {result['detected_violations']}")
            print(f"Expected Risk: {result['expected_risk']} | Detected Risk: {result['detected_risk']}")
            print(f"Violation Metrics - P: {result['precision']:.3f}, R: {result['recall']:.3f}, F1: {result['f1_score']:.3f}")
            print(f"BERT Score - P: {result['bert_precision']:.3f}, R: {result['bert_recall']:.3f}, F1: {result['bert_f1']:.3f}")
            print(f"AI Summary: {result['ai_summary'][:200]}...")
            print("-" * 60)

if __name__ == "__main__":
    main()
