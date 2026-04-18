import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from .base_agent import BaseAgent

class AnalyzerAgent(BaseAgent):
    """Agent responsible for anomaly detection and analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("AnalyzerAgent", config)
        self.anomaly_threshold = config.get('anomaly_threshold', 0.1) if config else 0.1
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for data analysis"""
        return self.analyze_data(data)
    
    def analyze_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis on extracted data"""
        
        self.log_action("Starting data analysis", {
            "transactions": len(extracted_data.get("transactions", [])),
            "invoices": len(extracted_data.get("invoices", []))
        })
        
        try:
            analysis_results = {
                "transaction_analysis": {},
                "invoice_analysis": {},
                "cross_analysis": {},
                "summary": {
                    "total_anomalies": 0,
                    "high_risk_items": [],
                    "recommendations": []
                },
                "metadata": {
                    "analysis_timestamp": pd.Timestamp.now().isoformat(),
                    "methods_used": ["statistical", "ml_isolation_forest", "rule_based"]
                }
            }
            
            # Analyze transactions
            if extracted_data.get("transactions"):
                analysis_results["transaction_analysis"] = self._analyze_transactions(
                    extracted_data["transactions"]
                )
            
            # Analyze invoices
            if extracted_data.get("invoices"):
                analysis_results["invoice_analysis"] = self._analyze_invoices(
                    extracted_data["invoices"]
                )
            
            # Perform cross-analysis
            analysis_results["cross_analysis"] = self._perform_cross_analysis(
                extracted_data.get("transactions", []),
                extracted_data.get("invoices", [])
            )
            
            # Generate summary
            analysis_results["summary"] = self._generate_analysis_summary(analysis_results)
            
            self.log_action("Analysis completed", {
                "anomalies_found": analysis_results["summary"]["total_anomalies"],
                "high_risk_count": len(analysis_results["summary"]["high_risk_items"])
            })
            
            return analysis_results
            
        except Exception as e:
            self.log_action("Analysis failed", {"error": str(e)})
            raise
    
    def _analyze_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze transaction data for anomalies"""
        
        df = pd.DataFrame(transactions)
        
        # Statistical analysis
        stats = {
            "total_count": len(df),
            "total_amount": df['amount'].sum(),
            "avg_amount": df['amount'].mean(),
            "median_amount": df['amount'].median(),
            "std_amount": df['amount'].std(),
            "max_amount": df['amount'].max(),
            "min_amount": df['amount'].min()
        }
        
        # ML-based anomaly detection
        anomalies = self._detect_transaction_anomalies_ml(df)
        
        # Rule-based anomaly detection
        rule_anomalies = self._detect_transaction_anomalies_rules(df)
        
        # Combine results
        all_anomalies = self._combine_anomalies(anomalies, rule_anomalies)
        
        return {
            "statistics": stats,
            "ml_anomalies": anomalies,
            "rule_anomalies": rule_anomalies,
            "combined_anomalies": all_anomalies,
            "anomaly_count": len(all_anomalies),
            "risk_distribution": self._calculate_risk_distribution(df, all_anomalies)
        }
    
    def _analyze_invoices(self, invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze invoice data for anomalies"""
        
        df = pd.DataFrame(invoices)
        
        # Statistical analysis
        stats = {
            "total_count": len(df),
            "total_amount": df['amount'].sum(),
            "avg_amount": df['amount'].mean(),
            "median_amount": df['amount'].median(),
            "std_amount": df['amount'].std(),
            "overdue_count": df.get('overdue', pd.Series([False]*len(df))).sum(),
            "avg_aging": df.get('aging_days', pd.Series([0]*len(df))).mean()
        }
        
        # ML-based anomaly detection
        anomalies = self._detect_invoice_anomalies_ml(df)
        
        # Rule-based anomaly detection
        rule_anomalies = self._detect_invoice_anomalies_rules(df)
        
        # Combine results
        all_anomalies = self._combine_anomalies(anomalies, rule_anomalies)
        
        return {
            "statistics": stats,
            "ml_anomalies": anomalies,
            "rule_anomalies": rule_anomalies,
            "combined_anomalies": all_anomalies,
            "anomaly_count": len(all_anomalies),
            "risk_distribution": self._calculate_risk_distribution(df, all_anomalies)
        }
    
    def _detect_transaction_anomalies_ml(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Use Isolation Forest for ML-based anomaly detection"""
        
        # Prepare features
        features = ['amount']
        if 'risk_score' in df.columns:
            features.append('risk_score')
        
        X = df[features].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply Isolation Forest
        iso_forest = IsolationForest(contamination=self.anomaly_threshold, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X_scaled)
        
        # Get anomaly scores
        anomaly_scores = iso_forest.decision_function(X_scaled)
        
        # Identify anomalies
        anomalies = []
        for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
            if label == -1:  # Anomaly
                anomalies.append({
                    "index": i,
                    "transaction_id": df.iloc[i].get('transaction_id', f'TXN_{i}'),
                    "amount": df.iloc[i]['amount'],
                    "anomaly_score": float(score),
                    "reason": "ML_isolation_forest",
                    "severity": "high" if score < -0.2 else "medium"
                })
        
        return anomalies
    
    def _detect_transaction_anomalies_rules(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Rule-based anomaly detection for transactions"""
        
        anomalies = []
        
        for i, row in df.iterrows():
            reasons = []
            severity = "low"
            
            # High amount rule
            if row['amount'] > 20000:
                reasons.append("High amount transaction")
                severity = "high"
            
            # Round amount rule
            if row['amount'] > 5000 and float(row['amount']).is_integer():
                reasons.append("Unusual round amount")
                severity = "medium" if severity == "low" else severity
            
            # Risk score rule
            if 'risk_score' in df.columns and row['risk_score'] > 0.7:
                reasons.append("High risk score")
                severity = "high"
            
            # Category rule
            if row.get('category') in ['Capex', 'Travel'] and row['amount'] > 10000:
                reasons.append(f"High amount in {row['category']} category")
                severity = "medium"
            
            if reasons:
                anomalies.append({
                    "index": i,
                    "transaction_id": row.get('transaction_id', f'TXN_{i}'),
                    "amount": row['amount'],
                    "reason": "; ".join(reasons),
                    "severity": severity,
                    "rule_based": True
                })
        
        return anomalies
    
    def _detect_invoice_anomalies_ml(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Use Isolation Forest for ML-based invoice anomaly detection"""
        
        # Prepare features
        features = ['amount', 'due_days']
        if 'risk_score' in df.columns:
            features.append('risk_score')
        if 'aging_days' in df.columns:
            features.append('aging_days')
        
        X = df[features].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply Isolation Forest
        iso_forest = IsolationForest(contamination=self.anomaly_threshold, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X_scaled)
        
        # Get anomaly scores
        anomaly_scores = iso_forest.decision_function(X_scaled)
        
        # Identify anomalies
        anomalies = []
        for i, (label, score) in enumerate(zip(anomaly_labels, anomaly_scores)):
            if label == -1:  # Anomaly
                anomalies.append({
                    "index": i,
                    "invoice_id": df.iloc[i].get('invoice_id', f'INV_{i}'),
                    "amount": df.iloc[i]['amount'],
                    "anomaly_score": float(score),
                    "reason": "ML_isolation_forest",
                    "severity": "high" if score < -0.2 else "medium"
                })
        
        return anomalies
    
    def _detect_invoice_anomalies_rules(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Rule-based anomaly detection for invoices"""
        
        anomalies = []
        
        for i, row in df.iterrows():
            reasons = []
            severity = "low"
            
            # Overdue rule
            if row.get('overdue', False):
                reasons.append("Overdue invoice")
                severity = "high"
            
            # High amount rule
            if row['amount'] > 50000:
                reasons.append("High amount invoice")
                severity = "high"
            
            # Unusual payment terms
            if row.get('due_days', 0) < 15:
                reasons.append("Unusual payment terms")
                severity = "medium"
            
            # Risk score rule
            if 'risk_score' in df.columns and row['risk_score'] > 0.6:
                reasons.append("High risk score")
                severity = "high"
            
            if reasons:
                anomalies.append({
                    "index": i,
                    "invoice_id": row.get('invoice_id', f'INV_{i}'),
                    "amount": row['amount'],
                    "reason": "; ".join(reasons),
                    "severity": severity,
                    "rule_based": True
                })
        
        return anomalies
    
    def _combine_anomalies(self, ml_anomalies: List[Dict], rule_anomalies: List[Dict]) -> List[Dict[str, Any]]:
        """Combine ML and rule-based anomalies"""
        
        combined = []
        
        # Add ML anomalies
        for anomaly in ml_anomalies:
            anomaly["detection_method"] = "ml"
            combined.append(anomaly)
        
        # Add rule anomalies
        for anomaly in rule_anomalies:
            anomaly["detection_method"] = "rule"
            combined.append(anomaly)
        
        # Sort by severity and score
        combined.sort(key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}.get(x.get("severity", "low"), 1),
            x.get("anomaly_score", 0)
        ), reverse=True)
        
        return combined
    
    def _calculate_risk_distribution(self, df: pd.DataFrame, anomalies: List[Dict]) -> Dict[str, Any]:
        """Calculate risk distribution across the dataset"""
        
        total_items = len(df)
        anomaly_count = len(anomalies)
        
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for anomaly in anomalies:
            severity_counts[anomaly.get("severity", "low")] += 1
        
        return {
            "total_items": total_items,
            "anomaly_count": anomaly_count,
            "anomaly_percentage": (anomaly_count / total_items * 100) if total_items > 0 else 0,
            "severity_breakdown": severity_counts,
            "risk_score": (severity_counts["high"] * 3 + severity_counts["medium"] * 2 + severity_counts["low"] * 1) / total_items if total_items > 0 else 0
        }
    
    def _perform_cross_analysis(self, transactions: List[Dict], invoices: List[Dict]) -> Dict[str, Any]:
        """Perform cross-analysis between transactions and invoices"""
        
        cross_findings = {
            "duplicate_patterns": [],
            "temporal_anomalies": [],
            "vendor_analysis": {},
            "correlation_analysis": {}
        }
        
        # Convert to DataFrames for easier analysis
        tx_df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
        inv_df = pd.DataFrame(invoices) if invoices else pd.DataFrame()
        
        # Analyze temporal patterns
        if not tx_df.empty and 'date' in tx_df.columns:
            tx_df['date'] = pd.to_datetime(tx_df['date'])
            daily_amounts = tx_df.groupby(tx_df['date'].dt.date)['amount'].sum()
            
            # Find unusual spikes
            mean_daily = daily_amounts.mean()
            std_daily = daily_amounts.std()
            
            for date, amount in daily_amounts.items():
                if amount > mean_daily + 2 * std_daily:
                    cross_findings["temporal_anomalies"].append({
                        "date": str(date),
                        "amount": float(amount),
                        "expected_range": [float(mean_daily - 2 * std_daily), float(mean_daily + 2 * std_daily)],
                        "severity": "high" if amount > mean_daily + 3 * std_daily else "medium"
                    })
        
        # Vendor analysis
        if not inv_df.empty and 'vendor_name' in inv_df.columns:
            vendor_stats = inv_df.groupby('vendor_name').agg({
                'amount': ['sum', 'count', 'mean'],
                'overdue': 'sum' if 'overdue' in inv_df.columns else lambda x: 0
            }).round(2)
            
            cross_findings["vendor_analysis"] = vendor_stats.to_dict()
        
        return cross_findings
    
    def _generate_analysis_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis summary"""
        
        transaction_anomalies = len(analysis_results.get("transaction_analysis", {}).get("combined_anomalies", []))
        invoice_anomalies = len(analysis_results.get("invoice_analysis", {}).get("combined_anomalies", []))
        
        total_anomalies = transaction_anomalies + invoice_anomalies
        
        # Extract high-risk items
        high_risk_items = []
        
        # Add high-risk transactions
        for anomaly in analysis_results.get("transaction_analysis", {}).get("combined_anomalies", []):
            if anomaly.get("severity") == "high":
                high_risk_items.append({
                    "type": "transaction",
                    "id": anomaly.get("transaction_id"),
                    "amount": anomaly.get("amount"),
                    "reason": anomaly.get("reason"),
                    "score": anomaly.get("anomaly_score", 0)
                })
        
        # Add high-risk invoices
        for anomaly in analysis_results.get("invoice_analysis", {}).get("combined_anomalies", []):
            if anomaly.get("severity") == "high":
                high_risk_items.append({
                    "type": "invoice",
                    "id": anomaly.get("invoice_id"),
                    "amount": anomaly.get("amount"),
                    "reason": anomaly.get("reason"),
                    "score": anomaly.get("anomaly_score", 0)
                })
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis_results)
        
        return {
            "total_anomalies": total_anomalies,
            "transaction_anomalies": transaction_anomalies,
            "invoice_anomalies": invoice_anomalies,
            "high_risk_items": high_risk_items[:10],  # Top 10 high-risk items
            "recommendations": recommendations,
            "overall_risk_score": self._calculate_overall_risk_score(analysis_results)
        }
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # Transaction-based recommendations
        tx_analysis = analysis_results.get("transaction_analysis", {})
        if tx_analysis.get("anomaly_count", 0) > 0:
            recommendations.append("Review high-value transactions for proper authorization")
            recommendations.append("Implement additional controls for round-number transactions")
        
        # Invoice-based recommendations
        inv_analysis = analysis_results.get("invoice_analysis", {})
        if inv_analysis.get("anomaly_count", 0) > 0:
            recommendations.append("Follow up on overdue invoices immediately")
            recommendations.append("Review vendor payment terms for consistency")
        
        # Cross-analysis recommendations
        cross_analysis = analysis_results.get("cross_analysis", {})
        if cross_analysis.get("temporal_anomalies"):
            recommendations.append("Investigate unusual transaction spikes on identified dates")
        
        # General recommendations
        total_anomalies = analysis_results.get("summary", {}).get("total_anomalies", 0)
        if total_anomalies > 50:
            recommendations.append("Consider implementing automated monitoring for early anomaly detection")
        
        return recommendations
    
    def _calculate_overall_risk_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall risk score for the audit"""
        
        tx_risk = analysis_results.get("transaction_analysis", {}).get("risk_distribution", {}).get("risk_score", 0)
        inv_risk = analysis_results.get("invoice_analysis", {}).get("risk_distribution", {}).get("risk_score", 0)
        
        # Weighted average (transactions weighted more heavily)
        overall_score = (tx_risk * 0.6 + inv_risk * 0.4)
        
        # Scale to 0-100
        return min(100, overall_score * 100)
