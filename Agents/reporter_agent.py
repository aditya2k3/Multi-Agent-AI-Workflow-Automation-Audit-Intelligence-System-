import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

class ReporterAgent(BaseAgent):
    """Agent responsible for generating comprehensive audit reports"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ReporterAgent", config)
        self.report_templates = config.get('report_templates', {}) if config else {}
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for report generation"""
        return self.generate_report(
            data.get("extracted_data", {}),
            data.get("analysis_results", {}),
            data.get("validation_results", {})
        )
    
    def generate_report(self, extracted_data: Dict[str, Any], analysis_results: Dict[str, Any], 
                       validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        
        self.log_action("Starting report generation", {
            "data_sources": len(extracted_data),
            "anomalies_found": analysis_results.get("summary", {}).get("total_anomalies", 0)
        })
        
        try:
            report_data = {
                "executive_summary": {},
                "detailed_findings": {},
                "risk_assessment": {},
                "recommendations": [],
                "appendices": {},
                "metadata": {
                    "report_timestamp": datetime.now().isoformat(),
                    "report_id": f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "generated_by": "AI Audit Automation System"
                }
            }
            
            # Generate executive summary
            report_data["executive_summary"] = self._generate_executive_summary(
                extracted_data, analysis_results, validation_results
            )
            
            # Generate detailed findings
            report_data["detailed_findings"] = self._generate_detailed_findings(
                extracted_data, analysis_results, validation_results
            )
            
            # Generate risk assessment
            report_data["risk_assessment"] = self._generate_risk_assessment(
                extracted_data, analysis_results, validation_results
            )
            
            # Generate recommendations
            report_data["recommendations"] = self._generate_comprehensive_recommendations(
                extracted_data, analysis_results, validation_results
            )
            
            # Generate appendices
            report_data["appendices"] = self._generate_appendices(
                extracted_data, analysis_results, validation_results
            )
            
            # Generate PDF report
            pdf_path = self._generate_pdf_report(report_data)
            
            # Generate JSON report
            json_path = self._generate_json_report(report_data)
            
            report_data["metadata"]["pdf_path"] = pdf_path
            report_data["metadata"]["json_path"] = json_path
            
            self.log_action("Report generation completed", {
                "report_id": report_data["metadata"]["report_id"],
                "pdf_path": pdf_path,
                "json_path": json_path
            })
            
            return report_data
            
        except Exception as e:
            self.log_action("Report generation failed", {"error": str(e)})
            raise
    
    def _generate_executive_summary(self, extracted_data: Dict[str, Any], 
                                  analysis_results: Dict[str, Any], 
                                  validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        
        summary = {
            "audit_period": self._determine_audit_period(extracted_data),
            "scope_overview": self._generate_scope_overview(extracted_data),
            "key_findings": self._extract_key_findings(analysis_results),
            "overall_risk_rating": self._calculate_overall_risk_rating(analysis_results),
            "critical_issues": self._identify_critical_issues(analysis_results, validation_results),
            "immediate_actions": self._identify_immediate_actions(analysis_results, validation_results)
        }
        
        return summary
    
    def _generate_detailed_findings(self, extracted_data: Dict[str, Any], 
                                   analysis_results: Dict[str, Any], 
                                   validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed findings section"""
        
        findings = {
            "transaction_anomalies": self._detail_transaction_findings(analysis_results),
            "invoice_anomalies": self._detail_invoice_findings(analysis_results),
            "cross_dataset_analysis": self._detail_cross_analysis(analysis_results),
            "data_quality_issues": self._detail_data_quality_issues(validation_results),
            "validation_findings": self._detail_validation_findings(validation_results)
        }
        
        return findings
    
    def _generate_risk_assessment(self, extracted_data: Dict[str, Any], 
                                 analysis_results: Dict[str, Any], 
                                 validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk assessment"""
        
        risk_assessment = {
            "overall_risk_score": analysis_results.get("summary", {}).get("overall_risk_score", 0),
            "risk_breakdown": self._calculate_risk_breakdown(analysis_results),
            "risk_trends": self._analyze_risk_trends(extracted_data),
            "high_risk_areas": self._identify_high_risk_areas(analysis_results),
            "risk_mitigation_status": self._assess_risk_mitigation(validation_results)
        }
        
        return risk_assessment
    
    def _generate_comprehensive_recommendations(self, extracted_data: Dict[str, Any], 
                                               analysis_results: Dict[str, Any], 
                                               validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations"""
        
        recommendations = []
        
        # Analysis-based recommendations
        analysis_recs = analysis_results.get("summary", {}).get("recommendations", [])
        for rec in analysis_recs:
            recommendations.append({
                "category": "analysis",
                "priority": "medium",
                "recommendation": rec,
                "rationale": "Based on anomaly detection results"
            })
        
        # Validation-based recommendations
        validation_recs = validation_results.get("summary", {}).get("recommendations", [])
        for rec in validation_recs:
            recommendations.append({
                "category": "validation",
                "priority": "high",
                "recommendation": rec,
                "rationale": "Based on validation findings"
            })
        
        # Process improvement recommendations
        process_recs = self._generate_process_recommendations(extracted_data, analysis_results)
        recommendations.extend(process_recs)
        
        # Technology recommendations
        tech_recs = self._generate_technology_recommendations(analysis_results, validation_results)
        recommendations.extend(tech_recs)
        
        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 1), reverse=True)
        
        return recommendations
    
    def _generate_appendices(self, extracted_data: Dict[str, Any], 
                            analysis_results: Dict[str, Any], 
                            validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appendices"""
        
        appendices = {
            "data_statistics": self._generate_data_statistics(extracted_data),
            "anomaly_details": self._generate_anomaly_details(analysis_results),
            "validation_metrics": self._generate_validation_metrics(validation_results),
            "methodology": self._generate_methodology_description(),
            "glossary": self._generate_glossary()
        }
        
        return appendices
    
    def _determine_audit_period(self, extracted_data: Dict[str, Any]) -> Dict[str, str]:
        """Determine audit period from data"""
        
        dates = []
        
        # Extract dates from transactions
        transactions = extracted_data.get("transactions", [])
        for tx in transactions:
            if 'date' in tx:
                dates.append(pd.to_datetime(tx['date']))
        
        # Extract dates from invoices
        invoices = extracted_data.get("invoices", [])
        for inv in invoices:
            if 'date' in inv:
                dates.append(pd.to_datetime(inv['date']))
        
        if dates:
            start_date = min(dates).strftime('%Y-%m-%d')
            end_date = max(dates).strftime('%Y-%m-%d')
            return {"start_date": start_date, "end_date": end_date}
        
        return {"start_date": "Unknown", "end_date": "Unknown"}
    
    def _generate_scope_overview(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scope overview"""
        
        transactions = extracted_data.get("transactions", [])
        invoices = extracted_data.get("invoices", [])
        
        scope = {
            "total_transactions": len(transactions),
            "total_invoices": len(invoices),
            "total_value": 0,
            "data_sources": [],
            "coverage_percentage": 100
        }
        
        # Calculate total value
        tx_total = sum(tx.get('amount', 0) for tx in transactions)
        inv_total = sum(inv.get('amount', 0) for inv in invoices)
        scope["total_value"] = tx_total + inv_total
        
        # Identify data sources
        if transactions:
            scope["data_sources"].append("Transactions")
        if invoices:
            scope["data_sources"].append("Invoices")
        
        return scope
    
    def _extract_key_findings(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key findings from analysis"""
        
        key_findings = []
        
        # Overall anomaly count
        total_anomalies = analysis_results.get("summary", {}).get("total_anomalies", 0)
        if total_anomalies > 0:
            key_findings.append({
                "finding": f"Found {total_anomalies} anomalies requiring review",
                "impact": "high" if total_anomalies > 50 else "medium",
                "description": "Anomalies detected across transactions and invoices"
            })
        
        # High-risk items
        high_risk_items = analysis_results.get("summary", {}).get("high_risk_items", [])
        if high_risk_items:
            key_findings.append({
                "finding": f"{len(high_risk_items)} high-risk items identified",
                "impact": "high",
                "description": "Items requiring immediate attention"
            })
        
        # Risk score
        overall_risk = analysis_results.get("summary", {}).get("overall_risk_score", 0)
        if overall_risk > 70:
            key_findings.append({
                "finding": f"High overall risk score: {overall_risk:.1f}",
                "impact": "high",
                "description": "Elevated risk level detected"
            })
        
        return key_findings
    
    def _calculate_overall_risk_rating(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall risk rating"""
        
        risk_score = analysis_results.get("summary", {}).get("overall_risk_score", 0)
        
        if risk_score >= 80:
            rating = "Critical"
            color = "red"
        elif risk_score >= 60:
            rating = "High"
            color = "orange"
        elif risk_score >= 40:
            rating = "Medium"
            color = "yellow"
        elif risk_score >= 20:
            rating = "Low"
            color = "green"
        else:
            rating = "Minimal"
            color = "blue"
        
        return {
            "rating": rating,
            "score": risk_score,
            "color": color,
            "description": f"Overall risk level is {rating.lower()} with a score of {risk_score:.1f}/100"
        }
    
    def _identify_critical_issues(self, analysis_results: Dict[str, Any], 
                                 validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical issues"""
        
        critical_issues = []
        
        # High-risk items from analysis
        high_risk_items = analysis_results.get("summary", {}).get("high_risk_items", [])
        for item in high_risk_items[:5]:  # Top 5
            critical_issues.append({
                "issue": f"High-risk {item.get('type', 'item')} {item.get('id')}",
                "amount": item.get('amount', 0),
                "reason": item.get('reason', 'Unknown'),
                "severity": "critical"
            })
        
        # Validation issues
        validation_issues = validation_results.get("summary", {}).get("issues_found", [])
        for issue in validation_issues:
            if issue.get("severity") == "high":
                critical_issues.append({
                    "issue": issue.get("description", "Validation issue"),
                    "severity": "critical",
                    "type": "validation"
                })
        
        return critical_issues
    
    def _identify_immediate_actions(self, analysis_results: Dict[str, Any], 
                                   validation_results: Dict[str, Any]) -> List[str]:
        """Identify immediate actions"""
        
        actions = []
        
        # Critical issues requiring immediate action
        critical_issues = self._identify_critical_issues(analysis_results, validation_results)
        if critical_issues:
            actions.append("Review and investigate all critical issues immediately")
        
        # High anomaly count
        total_anomalies = analysis_results.get("summary", {}).get("total_anomalies", 0)
        if total_anomalies > 20:
            actions.append("Implement enhanced monitoring for anomaly detection")
        
        # Data quality issues
        quality_score = validation_results.get("data_quality_validation", {}).get("overall_quality_score", 0)
        if quality_score < 80:
            actions.append("Address data quality issues to improve analysis accuracy")
        
        return actions
    
    def _detail_transaction_findings(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Detail transaction findings"""
        
        tx_analysis = analysis_results.get("transaction_analysis", {})
        
        return {
            "total_transactions": tx_analysis.get("statistics", {}).get("total_count", 0),
            "total_amount": tx_analysis.get("statistics", {}).get("total_amount", 0),
            "anomaly_count": tx_analysis.get("anomaly_count", 0),
            "anomaly_details": tx_analysis.get("combined_anomalies", [])[:10],  # Top 10
            "risk_distribution": tx_analysis.get("risk_distribution", {}),
            "statistical_summary": tx_analysis.get("statistics", {})
        }
    
    def _detail_invoice_findings(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Detail invoice findings"""
        
        inv_analysis = analysis_results.get("invoice_analysis", {})
        
        return {
            "total_invoices": inv_analysis.get("statistics", {}).get("total_count", 0),
            "total_amount": inv_analysis.get("statistics", {}).get("total_amount", 0),
            "overdue_count": inv_analysis.get("statistics", {}).get("overdue_count", 0),
            "anomaly_count": inv_analysis.get("anomaly_count", 0),
            "anomaly_details": inv_analysis.get("combined_anomalies", [])[:10],  # Top 10
            "risk_distribution": inv_analysis.get("risk_distribution", {}),
            "statistical_summary": inv_analysis.get("statistics", {})
        }
    
    def _detail_cross_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Detail cross-analysis findings"""
        
        return analysis_results.get("cross_analysis", {})
    
    def _detail_data_quality_issues(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Detail data quality issues"""
        
        return validation_results.get("data_quality_validation", {})
    
    def _detail_validation_findings(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Detail validation findings"""
        
        return {
            "validation_status": validation_results.get("summary", {}).get("validation_status", "unknown"),
            "confidence_score": validation_results.get("summary", {}).get("confidence_score", 0),
            "issues_found": validation_results.get("summary", {}).get("issues_found", []),
            "method_consistency": validation_results.get("method_consistency", {})
        }
    
    def _calculate_risk_breakdown(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk breakdown"""
        
        tx_risk = analysis_results.get("transaction_analysis", {}).get("risk_distribution", {})
        inv_risk = analysis_results.get("invoice_analysis", {}).get("risk_distribution", {})
        
        return {
            "transaction_risk": tx_risk,
            "invoice_risk": inv_risk,
            "combined_risk": {
                "high": tx_risk.get("severity_breakdown", {}).get("high", 0) + inv_risk.get("severity_breakdown", {}).get("high", 0),
                "medium": tx_risk.get("severity_breakdown", {}).get("medium", 0) + inv_risk.get("severity_breakdown", {}).get("medium", 0),
                "low": tx_risk.get("severity_breakdown", {}).get("low", 0) + inv_risk.get("severity_breakdown", {}).get("low", 0)
            }
        }
    
    def _analyze_risk_trends(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk trends"""
        
        # This would analyze temporal patterns in risk
        # For now, return placeholder
        return {
            "trend": "stable",
            "description": "Risk levels appear stable over the audit period"
        }
    
    def _identify_high_risk_areas(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify high-risk areas"""
        
        high_risk_areas = []
        
        # Transaction anomalies
        tx_anomalies = analysis_results.get("transaction_analysis", {}).get("combined_anomalies", [])
        high_tx = [a for a in tx_anomalies if a.get("severity") == "high"]
        if high_tx:
            high_risk_areas.append({
                "area": "Transactions",
                "risk_count": len(high_tx),
                "description": "High-risk transactions detected"
            })
        
        # Invoice anomalies
        inv_anomalies = analysis_results.get("invoice_analysis", {}).get("combined_anomalies", [])
        high_inv = [a for a in inv_anomalies if a.get("severity") == "high"]
        if high_inv:
            high_risk_areas.append({
                "area": "Invoices",
                "risk_count": len(high_inv),
                "description": "High-risk invoices detected"
            })
        
        return high_risk_areas
    
    def _assess_risk_mitigation(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk mitigation status"""
        
        return {
            "mitigation_status": "partial",
            "controls_in_place": ["Automated anomaly detection", "Data validation"],
            "gaps_identified": validation_results.get("summary", {}).get("issues_found", []),
            "recommendations": validation_results.get("summary", {}).get("recommendations", [])
        }
    
    def _generate_process_recommendations(self, extracted_data: Dict[str, Any], 
                                         analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate process improvement recommendations"""
        
        recommendations = []
        
        # Based on anomaly patterns
        total_anomalies = analysis_results.get("summary", {}).get("total_anomalies", 0)
        if total_anomalies > 30:
            recommendations.append({
                "category": "process",
                "priority": "high",
                "recommendation": "Strengthen pre-transaction approval processes",
                "rationale": "High number of anomalies suggests control weaknesses"
            })
        
        return recommendations
    
    def _generate_technology_recommendations(self, analysis_results: Dict[str, Any], 
                                            validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate technology recommendations"""
        
        recommendations = []
        
        # Based on validation consistency
        consistency_score = validation_results.get("method_consistency", {}).get("consistency_score", 0)
        if consistency_score < 60:
            recommendations.append({
                "category": "technology",
                "priority": "medium",
                "recommendation": "Enhance anomaly detection algorithms",
                "rationale": "Low consistency between detection methods"
            })
        
        return recommendations
    
    def _generate_data_statistics(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data statistics"""
        
        transactions = extracted_data.get("transactions", [])
        invoices = extracted_data.get("invoices", [])
        
        stats = {
            "transaction_stats": {},
            "invoice_stats": {}
        }
        
        if transactions:
            tx_df = pd.DataFrame(transactions)
            stats["transaction_stats"] = {
                "count": len(tx_df),
                "total_amount": float(tx_df['amount'].sum()),
                "avg_amount": float(tx_df['amount'].mean()),
                "median_amount": float(tx_df['amount'].median()),
                "max_amount": float(tx_df['amount'].max()),
                "min_amount": float(tx_df['amount'].min())
            }
        
        if invoices:
            inv_df = pd.DataFrame(invoices)
            stats["invoice_stats"] = {
                "count": len(inv_df),
                "total_amount": float(inv_df['amount'].sum()),
                "avg_amount": float(inv_df['amount'].mean()),
                "median_amount": float(inv_df['amount'].median()),
                "max_amount": float(inv_df['amount'].max()),
                "min_amount": float(inv_df['amount'].min())
            }
        
        return stats
    
    def _generate_anomaly_details(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate anomaly details"""
        
        return {
            "transaction_anomalies": analysis_results.get("transaction_analysis", {}).get("combined_anomalies", []),
            "invoice_anomalies": analysis_results.get("invoice_analysis", {}).get("combined_anomalies", []),
            "detection_methods": analysis_results.get("metadata", {}).get("methods_used", [])
        }
    
    def _generate_validation_metrics(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation metrics"""
        
        return {
            "validation_status": validation_results.get("summary", {}).get("validation_status", "unknown"),
            "confidence_score": validation_results.get("summary", {}).get("confidence_score", 0),
            "quality_metrics": validation_results.get("summary", {}).get("quality_metrics", {}),
            "validation_methods": validation_results.get("metadata", {}).get("validation_methods", [])
        }
    
    def _generate_methodology_description(self) -> Dict[str, Any]:
        """Generate methodology description"""
        
        return {
            "data_extraction": "Automated extraction from CSV files with validation and cleaning",
            "anomaly_detection": "Combination of ML (Isolation Forest) and rule-based methods",
            "validation": "Multi-layer validation including data quality and business rules",
            "reporting": "Automated generation of comprehensive audit reports"
        }
    
    def _generate_glossary(self) -> Dict[str, str]:
        """Generate glossary"""
        
        return {
            "Anomaly": "Data point that deviates significantly from expected patterns",
            "Risk Score": "Numerical representation of risk level (0-100)",
            "Isolation Forest": "Machine learning algorithm for anomaly detection",
            "Validation": "Process of verifying accuracy and reliability of findings"
        }
    
    def _generate_pdf_report(self, report_data: Dict[str, Any]) -> str:
        """Generate PDF report"""
        
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Generate filename
        report_id = report_data["metadata"]["report_id"]
        filename = f"reports/{report_id}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("AI Audit Automation Report", title_style))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        exec_summary = report_data.get("executive_summary", {})
        
        # Audit Period
        period = exec_summary.get("audit_period", {})
        story.append(Paragraph(f"<b>Audit Period:</b> {period.get('start_date', 'Unknown')} to {period.get('end_date', 'Unknown')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Overall Risk Rating
        risk_rating = exec_summary.get("overall_risk_rating", {})
        story.append(Paragraph(f"<b>Overall Risk Rating:</b> {risk_rating.get('rating', 'Unknown')} ({risk_rating.get('score', 0):.1f}/100)", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Key Findings
        story.append(Paragraph("<b>Key Findings:</b>", styles['Heading3']))
        key_findings = exec_summary.get("key_findings", [])
        for finding in key_findings:
            story.append(Paragraph(f"• {finding.get('finding', 'No finding')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Detailed Findings
        story.append(Paragraph("Detailed Findings", styles['Heading2']))
        
        # Transaction Analysis
        detailed = report_data.get("detailed_findings", {})
        tx_findings = detailed.get("transaction_anomalies", {})
        story.append(Paragraph(f"<b>Transactions:</b> {tx_findings.get('total_transactions', 0)} total, {tx_findings.get('anomaly_count', 0)} anomalies", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Invoice Analysis
        inv_findings = detailed.get("invoice_anomalies", {})
        story.append(Paragraph(f"<b>Invoices:</b> {inv_findings.get('total_invoices', 0)} total, {inv_findings.get('anomaly_count', 0)} anomalies", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading2']))
        recommendations = report_data.get("recommendations", [])
        for i, rec in enumerate(recommendations[:10], 1):  # Top 10 recommendations
            story.append(Paragraph(f"{i}. <b>{rec.get('recommendation', 'No recommendation')}</b>", styles['Normal']))
            story.append(Paragraph(f"   Priority: {rec.get('priority', 'Unknown')}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
        return filename
    
    def _generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Generate filename
        report_id = report_data["metadata"]["report_id"]
        filename = f"reports/{report_id}.json"
        
        # Write JSON report
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return filename
