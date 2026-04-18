import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json
from datetime import datetime
from .base_agent import BaseAgent

class ValidatorAgent(BaseAgent):
    """Agent responsible for validating analysis results and ensuring accuracy"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ValidatorAgent", config)
        self.validation_rules = config.get('validation_rules', {}) if config else {}
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for validation"""
        return self.validate_findings(data.get("extracted_data", {}), data.get("analysis_results", {}))
    
    def validate_findings(self, extracted_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis findings against business rules and data quality standards"""
        
        self.log_action("Starting validation", {
            "transactions_analyzed": len(analysis_results.get("transaction_analysis", {}).get("combined_anomalies", [])),
            "invoices_analyzed": len(analysis_results.get("invoice_analysis", {}).get("combined_anomalies", []))
        })
        
        try:
            validation_results = {
                "data_quality_validation": {},
                "anomaly_validation": {},
                "business_rule_validation": {},
                "cross_validation": {},
                "summary": {
                    "validation_status": "passed",
                    "issues_found": [],
                    "recommendations": [],
                    "confidence_score": 0.0
                },
                "metadata": {
                    "validation_timestamp": datetime.now().isoformat(),
                    "validation_methods": ["data_quality", "business_rules", "cross_validation"]
                }
            }
            
            # Data quality validation
            validation_results["data_quality_validation"] = self._validate_data_quality(extracted_data)
            
            # Anomaly validation
            validation_results["anomaly_validation"] = self._validate_anomalies(analysis_results)
            
            # Business rule validation
            validation_results["business_rule_validation"] = self._validate_business_rules(
                extracted_data, analysis_results
            )
            
            # Cross-validation
            validation_results["cross_validation"] = self._perform_cross_validation(
                extracted_data, analysis_results
            )
            
            # Generate validation summary
            validation_results["summary"] = self._generate_validation_summary(validation_results)
            
            self.log_action("Validation completed", {
                "status": validation_results["summary"]["validation_status"],
                "issues_found": len(validation_results["summary"]["issues_found"]),
                "confidence_score": validation_results["summary"]["confidence_score"]
            })
            
            return validation_results
            
        except Exception as e:
            self.log_action("Validation failed", {"error": str(e)})
            raise
    
    def _validate_data_quality(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of extracted data"""
        
        quality_results = {
            "transactions": {},
            "invoices": {},
            "overall_quality_score": 0.0
        }
        
        # Validate transactions
        transactions = extracted_data.get("transactions", [])
        if transactions:
            tx_df = pd.DataFrame(transactions)
            
            tx_quality = {
                "total_records": len(tx_df),
                "missing_values": tx_df.isnull().sum().to_dict(),
                "duplicate_records": tx_df.duplicated().sum(),
                "data_types": tx_df.dtypes.astype(str).to_dict(),
                "completeness_score": self._calculate_completeness_score(tx_df),
                "consistency_score": self._calculate_consistency_score(tx_df, "transactions"),
                "validity_issues": self._check_data_validity(tx_df, "transactions")
            }
            
            quality_results["transactions"] = tx_quality
        
        # Validate invoices
        invoices = extracted_data.get("invoices", [])
        if invoices:
            inv_df = pd.DataFrame(invoices)
            
            inv_quality = {
                "total_records": len(inv_df),
                "missing_values": inv_df.isnull().sum().to_dict(),
                "duplicate_records": inv_df.duplicated().sum(),
                "data_types": inv_df.dtypes.astype(str).to_dict(),
                "completeness_score": self._calculate_completeness_score(inv_df),
                "consistency_score": self._calculate_consistency_score(inv_df, "invoices"),
                "validity_issues": self._check_data_validity(inv_df, "invoices")
            }
            
            quality_results["invoices"] = inv_quality
        
        # Calculate overall quality score
        scores = []
        if quality_results["transactions"]:
            scores.append(quality_results["transactions"]["completeness_score"])
            scores.append(quality_results["transactions"]["consistency_score"])
        if quality_results["invoices"]:
            scores.append(quality_results["invoices"]["completeness_score"])
            scores.append(quality_results["invoices"]["consistency_score"])
        
        quality_results["overall_quality_score"] = np.mean(scores) if scores else 0.0
        
        return quality_results
    
    def _validate_anomalies(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate anomaly detection results"""
        
        anomaly_validation = {
            "transaction_anomalies": {},
            "invoice_anomalies": {},
            "method_consistency": {},
            "false_positive_analysis": {}
        }
        
        # Validate transaction anomalies
        tx_analysis = analysis_results.get("transaction_analysis", {})
        if tx_analysis:
            tx_anomalies = tx_analysis.get("combined_anomalies", [])
            ml_anomalies = tx_analysis.get("ml_anomalies", [])
            rule_anomalies = tx_analysis.get("rule_anomalies", [])
            
            anomaly_validation["transaction_anomalies"] = {
                "total_anomalies": len(tx_anomalies),
                "ml_anomalies": len(ml_anomalies),
                "rule_anomalies": len(rule_anomalies),
                "severity_distribution": self._calculate_severity_distribution(tx_anomalies),
                "overlap_analysis": self._analyze_method_overlap(ml_anomalies, rule_anomalies)
            }
        
        # Validate invoice anomalies
        inv_analysis = analysis_results.get("invoice_analysis", {})
        if inv_analysis:
            inv_anomalies = inv_analysis.get("combined_anomalies", [])
            ml_anomalies = inv_analysis.get("ml_anomalies", [])
            rule_anomalies = inv_analysis.get("rule_anomalies", [])
            
            anomaly_validation["invoice_anomalies"] = {
                "total_anomalies": len(inv_anomalies),
                "ml_anomalies": len(ml_anomalies),
                "rule_anomalies": len(rule_anomalies),
                "severity_distribution": self._calculate_severity_distribution(inv_anomalies),
                "overlap_analysis": self._analyze_method_overlap(ml_anomalies, rule_anomalies)
            }
        
        # Method consistency check
        anomaly_validation["method_consistency"] = self._check_method_consistency(analysis_results)
        
        # False positive analysis
        anomaly_validation["false_positive_analysis"] = self._analyze_false_positives(analysis_results)
        
        return anomaly_validation
    
    def _validate_business_rules(self, extracted_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate findings against business rules"""
        
        business_validation = {
            "policy_compliance": {},
            "threshold_validation": {},
            "authorization_checks": {},
            "compliance_issues": []
        }
        
        transactions = extracted_data.get("transactions", [])
        invoices = extracted_data.get("invoices", [])
        
        # Check transaction policies
        if transactions:
            tx_df = pd.DataFrame(transactions)
            
            policy_violations = []
            
            # Check for unauthorized high-value transactions
            high_value_tx = tx_df[tx_df['amount'] > 10000]
            if not high_value_tx.empty:
                policy_violations.append({
                    "rule": "High-value transaction authorization",
                    "violations": len(high_value_tx),
                    "severity": "high",
                    "description": "Transactions above $10,000 require additional authorization"
                })
            
            # Check for unusual categories
            unusual_categories = ['Capex', 'Travel']
            for category in unusual_categories:
                cat_tx = tx_df[tx_df['category'] == category]
                if not cat_tx.empty:
                    high_amount_cat = cat_tx[cat_tx['amount'] > 5000]
                    if not high_amount_cat.empty:
                        policy_violations.append({
                            "rule": f"High-value {category} transactions",
                            "violations": len(high_amount_cat),
                            "severity": "medium",
                            "description": f"{category} transactions above $5,000 require review"
                        })
            
            business_validation["policy_compliance"] = {
                "total_transactions": len(tx_df),
                "policy_violations": policy_violations,
                "compliance_score": max(0, 100 - len(policy_violations) * 10)
            }
        
        # Check invoice policies
        if invoices:
            inv_df = pd.DataFrame(invoices)
            
            invoice_violations = []
            
            # Check overdue invoices
            if 'overdue' in inv_df.columns:
                overdue_count = inv_df['overdue'].sum()
                if overdue_count > 0:
                    invoice_violations.append({
                        "rule": "Timely payment",
                        "violations": int(overdue_count),
                        "severity": "high",
                        "description": "Overdue invoices require immediate attention"
                    })
            
            # Check unusual payment terms
            if 'due_days' in inv_df.columns:
                unusual_terms = inv_df[inv_df['due_days'] < 15]
                if not unusual_terms.empty:
                    invoice_violations.append({
                        "rule": "Standard payment terms",
                        "violations": len(unusual_terms),
                        "severity": "medium",
                        "description": "Payment terms less than 15 days require review"
                    })
            
            business_validation["authorization_checks"] = {
                "total_invoices": len(inv_df),
                "policy_violations": invoice_violations,
                "compliance_score": max(0, 100 - len(invoice_violations) * 10)
            }
        
        return business_validation
    
    def _perform_cross_validation(self, extracted_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-validation between different data sources and methods"""
        
        cross_validation = {
            "data_consistency": {},
            "method_agreement": {},
            "temporal_validation": {},
            "statistical_validation": {}
        }
        
        transactions = extracted_data.get("transactions", [])
        invoices = extracted_data.get("invoices", [])
        
        # Data consistency checks
        if transactions and invoices:
            tx_df = pd.DataFrame(transactions)
            inv_df = pd.DataFrame(invoices)
            
            # Check for duplicate IDs across datasets
            tx_ids = set(tx_df.get('transaction_id', []))
            inv_ids = set(inv_df.get('invoice_id', []))
            
            cross_validation["data_consistency"] = {
                "duplicate_ids": len(tx_ids.intersection(inv_ids)),
                "id_overlap": list(tx_ids.intersection(inv_ids))[:5],  # Show first 5
                "consistency_score": 100.0 if len(tx_ids.intersection(inv_ids)) == 0 else 80.0
            }
        
        # Method agreement analysis
        cross_validation["method_agreement"] = self._analyze_method_agreement(analysis_results)
        
        # Temporal validation
        cross_validation["temporal_validation"] = self._validate_temporal_patterns(extracted_data)
        
        # Statistical validation
        cross_validation["statistical_validation"] = self._validate_statistical_patterns(extracted_data)
        
        return cross_validation
    
    def _calculate_completeness_score(self, df: pd.DataFrame) -> float:
        """Calculate data completeness score"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        return ((total_cells - missing_cells) / total_cells) * 100 if total_cells > 0 else 0
    
    def _calculate_consistency_score(self, df: pd.DataFrame, data_type: str) -> float:
        """Calculate data consistency score"""
        consistency_issues = 0
        
        # Check for negative amounts
        if 'amount' in df.columns:
            negative_amounts = (df['amount'] < 0).sum()
            consistency_issues += negative_amounts
        
        # Check for future dates
        date_columns = ['date', 'due_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                future_dates = (df[col] > pd.Timestamp.now()).sum()
                consistency_issues += future_dates
        
        # Check for duplicate IDs
        id_columns = ['transaction_id', 'invoice_id']
        for col in id_columns:
            if col in df.columns:
                duplicates = df[col].duplicated().sum()
                consistency_issues += duplicates
        
        total_records = len(df)
        return max(0, (total_records - consistency_issues) / total_records * 100) if total_records > 0 else 0
    
    def _check_data_validity(self, df: pd.DataFrame, data_type: str) -> List[Dict[str, Any]]:
        """Check for data validity issues"""
        issues = []
        
        # Amount validity
        if 'amount' in df.columns:
            zero_amounts = (df['amount'] == 0).sum()
            if zero_amounts > 0:
                issues.append({
                    "type": "zero_amounts",
                    "count": int(zero_amounts),
                    "severity": "medium",
                    "description": "Records with zero amounts found"
                })
        
        # Date validity
        date_columns = ['date', 'due_date']
        for col in date_columns:
            if col in df.columns:
                invalid_dates = df[col].isnull().sum()
                if invalid_dates > 0:
                    issues.append({
                        "type": "invalid_dates",
                        "column": col,
                        "count": int(invalid_dates),
                        "severity": "high",
                        "description": f"Invalid or missing dates in {col}"
                    })
        
        return issues
    
    def _calculate_severity_distribution(self, anomalies: List[Dict]) -> Dict[str, int]:
        """Calculate severity distribution of anomalies"""
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for anomaly in anomalies:
            severity = anomaly.get("severity", "low")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts
    
    def _analyze_method_overlap(self, ml_anomalies: List[Dict], rule_anomalies: List[Dict]) -> Dict[str, Any]:
        """Analyze overlap between ML and rule-based anomaly detection"""
        
        ml_indices = {a.get("index") for a in ml_anomalies if "index" in a}
        rule_indices = {a.get("index") for a in rule_anomalies if "index" in a}
        
        overlap = ml_indices.intersection(rule_indices)
        
        return {
            "ml_only": len(ml_indices - rule_indices),
            "rule_only": len(rule_indices - ml_indices),
            "both_methods": len(overlap),
            "overlap_percentage": (len(overlap) / len(ml_indices.union(rule_indices)) * 100) if ml_indices.union(rule_indices) else 0
        }
    
    def _check_method_consistency(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check consistency between different anomaly detection methods"""
        
        consistency_score = 0.0
        issues = []
        
        # Compare transaction anomaly methods
        tx_analysis = analysis_results.get("transaction_analysis", {})
        if tx_analysis:
            overlap = tx_analysis.get("combined_anomalies", [])
            ml_count = len(tx_analysis.get("ml_anomalies", []))
            rule_count = len(tx_analysis.get("rule_anomalies", []))
            
            if ml_count > 0 and rule_count > 0:
                overlap_analysis = self._analyze_method_overlap(
                    tx_analysis.get("ml_anomalies", []),
                    tx_analysis.get("rule_anomalies", [])
                )
                consistency_score += overlap_analysis.get("overlap_percentage", 0) / 2
        
        # Compare invoice anomaly methods
        inv_analysis = analysis_results.get("invoice_analysis", {})
        if inv_analysis:
            overlap_analysis = self._analyze_method_overlap(
                inv_analysis.get("ml_anomalies", []),
                inv_analysis.get("rule_anomalies", [])
            )
            consistency_score += overlap_analysis.get("overlap_percentage", 0) / 2
        
        return {
            "consistency_score": consistency_score,
            "issues": issues,
            "assessment": "high" if consistency_score > 70 else "medium" if consistency_score > 40 else "low"
        }
    
    def _analyze_false_positives(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential false positives in anomaly detection"""
        
        false_positive_indicators = {
            "round_amount_only": 0,
            "low_risk_score": 0,
            "insufficient_evidence": 0,
            "potential_fp_count": 0
        }
        
        # Analyze transaction anomalies
        tx_anomalies = analysis_results.get("transaction_analysis", {}).get("combined_anomalies", [])
        for anomaly in tx_anomalies:
            fp_indicators = 0
            
            # Check if only reason is round amount
            if "round amount" in anomaly.get("reason", "").lower():
                fp_indicators += 1
            
            # Check risk score
            if "anomaly_score" in anomaly and anomaly["anomaly_score"] > -0.1:
                fp_indicators += 1
            
            if fp_indicators >= 2:
                false_positive_indicators["potential_fp_count"] += 1
        
        return false_positive_indicators
    
    def _analyze_method_agreement(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze agreement between different detection methods"""
        
        agreement_scores = {}
        
        # Transaction method agreement
        tx_analysis = analysis_results.get("transaction_analysis", {})
        if tx_analysis:
            overlap = self._analyze_method_overlap(
                tx_analysis.get("ml_anomalies", []),
                tx_analysis.get("rule_anomalies", [])
            )
            agreement_scores["transactions"] = overlap.get("overlap_percentage", 0)
        
        # Invoice method agreement
        inv_analysis = analysis_results.get("invoice_analysis", {})
        if inv_analysis:
            overlap = self._analyze_method_overlap(
                inv_analysis.get("ml_anomalies", []),
                inv_analysis.get("rule_anomalies", [])
            )
            agreement_scores["invoices"] = overlap.get("overlap_percentage", 0)
        
        return agreement_scores
    
    def _validate_temporal_patterns(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate temporal patterns in the data"""
        
        temporal_validation = {
            "weekend_activity": 0,
            "unusual_hours": 0,
            "temporal_consistency": "good"
        }
        
        transactions = extracted_data.get("transactions", [])
        if transactions:
            tx_df = pd.DataFrame(transactions)
            if 'date' in tx_df.columns:
                tx_df['date'] = pd.to_datetime(tx_df['date'])
                tx_df['weekday'] = tx_df['date'].dt.dayofweek
                
                # Check weekend activity
                weekend_tx = tx_df[tx_df['weekday'] >= 5]
                temporal_validation["weekend_activity"] = len(weekend_tx)
        
        return temporal_validation
    
    def _validate_statistical_patterns(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate statistical patterns in the data"""
        
        statistical_validation = {
            "outlier_percentage": 0.0,
            "distribution_normality": "unknown",
            "statistical_anomalies": []
        }
        
        transactions = extracted_data.get("transactions", [])
        if transactions:
            tx_df = pd.DataFrame(transactions)
            if 'amount' in tx_df.columns:
                amounts = tx_df['amount']
                
                # Calculate outliers using IQR method
                Q1 = amounts.quantile(0.25)
                Q3 = amounts.quantile(0.75)
                IQR = Q3 - Q1
                outliers = amounts[(amounts < Q1 - 1.5 * IQR) | (amounts > Q3 + 1.5 * IQR)]
                
                statistical_validation["outlier_percentage"] = (len(outliers) / len(amounts)) * 100
                statistical_validation["statistical_anomalies"] = outliers.head(5).tolist()
        
        return statistical_validation
    
    def _generate_validation_summary(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation summary"""
        
        # Collect all issues
        all_issues = []
        
        # Data quality issues
        data_quality = validation_results.get("data_quality_validation", {})
        if data_quality.get("transactions", {}).get("validity_issues"):
            all_issues.extend(data_quality["transactions"]["validity_issues"])
        if data_quality.get("invoices", {}).get("validity_issues"):
            all_issues.extend(data_quality["invoices"]["validity_issues"])
        
        # Business rule violations
        business_rules = validation_results.get("business_rule_validation", {})
        if business_rules.get("policy_compliance", {}).get("policy_violations"):
            all_issues.extend(business_rules["policy_compliance"]["policy_violations"])
        if business_rules.get("authorization_checks", {}).get("policy_violations"):
            all_issues.extend(business_rules["authorization_checks"]["policy_violations"])
        
        # Calculate confidence score
        quality_score = data_quality.get("overall_quality_score", 0)
        consistency_score = validation_results.get("method_consistency", {}).get("consistency_score", 0)
        
        confidence_score = (quality_score + consistency_score) / 2
        
        # Determine validation status
        critical_issues = [issue for issue in all_issues if issue.get("severity") == "high"]
        validation_status = "failed" if critical_issues else "warning" if all_issues else "passed"
        
        # Generate recommendations
        recommendations = self._generate_validation_recommendations(validation_results, all_issues)
        
        return {
            "validation_status": validation_status,
            "issues_found": all_issues,
            "critical_issues_count": len(critical_issues),
            "total_issues_count": len(all_issues),
            "confidence_score": confidence_score,
            "recommendations": recommendations,
            "quality_metrics": {
                "data_quality": quality_score,
                "method_consistency": consistency_score,
                "business_compliance": business_rules.get("policy_compliance", {}).get("compliance_score", 100)
            }
        }
    
    def _generate_validation_recommendations(self, validation_results: Dict[str, Any], issues: List[Dict]) -> List[str]:
        """Generate validation recommendations"""
        
        recommendations = []
        
        # Data quality recommendations
        quality_score = validation_results.get("data_quality_validation", {}).get("overall_quality_score", 0)
        if quality_score < 80:
            recommendations.append("Improve data quality by addressing missing values and duplicates")
        
        # Method consistency recommendations
        consistency_score = validation_results.get("method_consistency", {}).get("consistency_score", 0)
        if consistency_score < 50:
            recommendations.append("Review anomaly detection methods for better alignment")
        
        # Business rule recommendations
        critical_issues = [issue for issue in issues if issue.get("severity") == "high"]
        if critical_issues:
            recommendations.append("Address critical business rule violations immediately")
        
        # False positive recommendations
        fp_analysis = validation_results.get("anomaly_validation", {}).get("false_positive_analysis", {})
        if fp_analysis.get("potential_fp_count", 0) > 10:
            recommendations.append("Refine anomaly detection thresholds to reduce false positives")
        
        return recommendations
