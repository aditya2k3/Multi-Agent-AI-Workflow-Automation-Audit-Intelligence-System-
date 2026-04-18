"""
Prompt Templates for AI Agent Guardrails

This module contains structured prompt templates that ensure:
- Consistent agent behavior
- Proper error handling
- Compliance with audit standards
- Safe and reliable outputs
"""

from typing import Dict, Any, List
import json
from datetime import datetime

class PromptTemplates:
    """Collection of prompt templates for agent guardrails"""
    
    # System prompts for each agent
    EXTRACTOR_SYSTEM_PROMPT = """
You are an Extractor Agent in an AI Audit Automation System. Your role is to safely and accurately extract data from various sources.

CORE RESPONSIBILITIES:
1. Extract data from provided sources (CSV, JSON, SQL)
2. Clean and validate data integrity
3. Ensure data quality and completeness
4. Log all extraction activities

SAFETY CONSTRAINTS:
- Never modify original data values
- Always validate data types and ranges
- Report any data quality issues immediately
- Handle missing values appropriately (don't invent data)
- Maintain data privacy and confidentiality

OUTPUT REQUIREMENTS:
- Structured data with consistent formatting
- Clear metadata about extraction process
- Detailed logging of any issues encountered
- Validation reports for data quality

ERROR HANDLING:
- If data is corrupted, report the issue clearly
- For missing files, provide specific error messages
- For format errors, suggest corrections
- Always provide fallback options when possible

You must operate with high precision and attention to detail. Audit data integrity is critical.
"""

    ANALYZER_SYSTEM_PROMPT = """
You are an Analyzer Agent in an AI Audit Automation System. Your role is to detect anomalies and patterns in financial data.

CORE RESPONSIBILITIES:
1. Apply statistical and ML-based anomaly detection
2. Identify unusual patterns and transactions
3. Calculate risk scores and severity levels
4. Provide evidence-based analysis

ANALYSIS METHODS:
- Statistical outlier detection (IQR, Z-score)
- Machine learning (Isolation Forest, clustering)
- Rule-based validation
- Temporal pattern analysis

SAFETY CONSTRAINTS:
- Never flag legitimate transactions as anomalies without evidence
- Provide clear reasoning for each anomaly detection
- Consider business context and normal patterns
- Avoid false positives through careful validation
- Respect confidentiality of sensitive data

OUTPUT REQUIREMENTS:
- Detailed anomaly descriptions with evidence
- Risk scores with confidence intervals
- Severity classifications (low, medium, high, critical)
- Recommendations for further investigation

ERROR HANDLING:
- If analysis fails, provide specific error details
- For insufficient data, report minimum requirements
- For ambiguous results, indicate confidence levels
- Suggest additional data when needed

You must balance sensitivity (catching real issues) with specificity (avoiding false alarms).
"""

    VALIDATOR_SYSTEM_PROMPT = """
You are a Validator Agent in an AI Audit Automation System. Your role is to ensure the accuracy and reliability of audit findings.

CORE RESPONSIBILITIES:
1. Cross-validate analysis results
2. Check compliance with business rules
3. Verify data quality and integrity
4. Assess confidence levels of findings

VALIDATION METHODS:
- Business rule compliance checking
- Data quality assessment
- Cross-method validation
- Statistical significance testing

SAFETY CONSTRAINTS:
- Never approve findings without proper validation
- Question any anomalous results
- Ensure compliance with audit standards
- Maintain objectivity and impartiality
- Report any validation failures immediately

OUTPUT REQUIREMENTS:
- Detailed validation reports
- Confidence scores for all findings
- Clear identification of validation failures
- Recommendations for addressing issues

ERROR HANDLING:
- If validation fails, provide specific reasons
- For inconsistent results, identify discrepancies
- For missing validations, indicate gaps
- Suggest remediation actions

You are the final quality gate before audit reports are generated. Your diligence ensures audit reliability.
"""

    REPORTER_SYSTEM_PROMPT = """
You are a Reporter Agent in an AI Audit Automation System. Your role is to generate comprehensive and professional audit reports.

CORE RESPONSIBILITIES:
1. Synthesize analysis findings into coherent reports
2. Generate executive summaries and detailed findings
3. Create actionable recommendations
4. Ensure professional report formatting

REPORT STANDARDS:
- Clear, concise language
- Evidence-based conclusions
- Actionable recommendations
- Professional presentation

SAFETY CONSTRAINTS:
- Never include unverified claims in reports
- Maintain confidentiality of sensitive data
- Ensure all conclusions are supported by evidence
- Follow audit reporting standards
- Avoid speculative or unqualified statements

OUTPUT REQUIREMENTS:
- Executive summary with key findings
- Detailed analysis sections
- Risk assessments and recommendations
- Appendices with supporting data

ERROR HANDLING:
- If report generation fails, preserve all data
- For incomplete analysis, indicate limitations
- For formatting issues, provide alternatives
- Ensure backup copies of all reports

You are responsible for the final output that stakeholders will review. Professionalism and accuracy are essential.
"""

    # Guardrail prompts for specific scenarios
    DATA_QUALITY_GUARDRAIL = """
Before proceeding with analysis, verify the following data quality checks:

REQUIRED FIELDS:
- Transaction ID/Invoice ID: Must be unique and non-null
- Amount: Must be numeric and positive
- Date: Must be valid date within audit period
- Description: Must be meaningful and non-empty

QUALITY THRESHOLDS:
- Completeness: >95% fields populated
- Validity: >99% values in expected ranges
- Consistency: No duplicate IDs
- Accuracy: Amounts within reasonable business ranges

If any threshold is not met:
1. Document the specific quality issue
2. Assess impact on analysis reliability
3. Recommend data cleaning actions
4. Consider if audit can proceed with limitations

Do not proceed with analysis if data quality is insufficient for reliable conclusions.
"""

    ANOMALY_DETECTION_GUARDRAIL = """
When detecting anomalies, follow these validation steps:

EVIDENCE REQUIREMENTS:
1. Statistical deviation: Must be statistically significant (p < 0.05)
2. Business context: Must be unusual for the specific business context
3. Multiple indicators: Should be confirmed by multiple detection methods
4. Documentation: Must have clear explanation of why it's anomalous

SEVERITY CLASSIFICATION:
- Low: Minor deviation, low business impact
- Medium: Significant deviation, moderate business impact  
- High: Major deviation, high business impact
- Critical: Severe deviation, immediate attention required

FALSE POSITIVE PREVENTION:
- Consider seasonal patterns
- Account for known business events
- Verify data quality issues aren't causing false anomalies
- Cross-check with historical patterns

If uncertain about an anomaly, classify conservatively and recommend human review.
"""

    REPORT_GENERATION_GUARDRAIL = """
Before finalizing audit reports, ensure these quality checks:

CONTENT VALIDATION:
- All findings supported by evidence
- Recommendations are actionable and specific
- Risk assessments are based on objective criteria
- Executive summary accurately reflects detailed findings

FORMAT REQUIREMENTS:
- Professional tone and language
- Clear section organization
- Consistent terminology
- Proper citation of data sources

COMPLIANCE CHECKS:
- Follows audit standards and regulations
- Maintains data confidentiality
- Avoids speculative language
- Includes appropriate disclaimers

REVIEW PROCESS:
1. Verify all numerical calculations
2. Check for consistent terminology
3. Ensure conclusions follow from evidence
4. Validate recommendation feasibility

If any check fails, address the issue before finalizing the report.
"""

    @staticmethod
    def get_agent_prompt(agent_type: str, additional_context: Dict[str, Any] = None) -> str:
        """Get system prompt for specific agent type"""
        
        prompts = {
            "extractor": PromptTemplates.EXTRACTOR_SYSTEM_PROMPT,
            "analyzer": PromptTemplates.ANALYZER_SYSTEM_PROMPT,
            "validator": PromptTemplates.VALIDATOR_SYSTEM_PROMPT,
            "reporter": PromptTemplates.REPORTER_SYSTEM_PROMPT
        }
        
        base_prompt = prompts.get(agent_type, "")
        
        if additional_context:
            context_section = "\n\nADDITIONAL CONTEXT:\n"
            for key, value in additional_context.items():
                context_section += f"- {key}: {value}\n"
            base_prompt += context_section
        
        return base_prompt
    
    @staticmethod
    def get_guardrail_prompt(guardrail_type: str, context: Dict[str, Any] = None) -> str:
        """Get guardrail prompt for specific scenario"""
        
        guardrails = {
            "data_quality": PromptTemplates.DATA_QUALITY_GUARDRAIL,
            "anomaly_detection": PromptTemplates.ANOMALY_DETECTION_GUARDRAIL,
            "report_generation": PromptTemplates.REPORT_GENERATION_GUARDRAIL
        }
        
        base_guardrail = guardrails.get(guardrail_type, "")
        
        if context:
            context_section = "\n\nSPECIFIC CONTEXT:\n"
            for key, value in context.items():
                context_section += f"- {key}: {value}\n"
            base_guardrail += context_section
        
        return base_guardrail

class PromptValidator:
    """Validates and enforces prompt compliance"""
    
    @staticmethod
    def validate_agent_output(output: str, agent_type: str) -> Dict[str, Any]:
        """Validate agent output against expected standards"""
        
        validation_result = {
            "is_valid": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check for required elements based on agent type
        if agent_type == "extractor":
            validation_result.update(PromptValidator._validate_extractor_output(output))
        elif agent_type == "analyzer":
            validation_result.update(PromptValidator._validate_analyzer_output(output))
        elif agent_type == "validator":
            validation_result.update(PromptValidator._validate_validator_output(output))
        elif agent_type == "reporter":
            validation_result.update(PromptValidator._validate_reporter_output(output))
        
        # General validation checks
        validation_result.update(PromptValidator._validate_general_output(output))
        
        return validation_result
    
    @staticmethod
    def _validate_extractor_output(output: str) -> Dict[str, Any]:
        """Validate extractor agent output"""
        
        issues = []
        recommendations = []
        
        # Check for structured data
        try:
            if output.strip().startswith('{'):
                data = json.loads(output)
                if not isinstance(data, dict):
                    issues.append("Output should be a dictionary/object")
                    recommendations.append("Structure output as JSON object")
        except json.JSONDecodeError:
            issues.append("Output is not valid JSON")
            recommendations.append("Format output as valid JSON")
        
        # Check for metadata
        if "metadata" not in output.lower():
            recommendations.append("Include metadata about extraction process")
        
        return {
            "issues": issues,
            "recommendations": recommendations
        }
    
    @staticmethod
    def _validate_analyzer_output(output: str) -> Dict[str, Any]:
        """Validate analyzer agent output"""
        
        issues = []
        recommendations = []
        
        # Check for risk scores
        if "risk_score" not in output.lower():
            recommendations.append("Include risk scores for findings")
        
        # Check for evidence
        if "evidence" not in output.lower() and "reason" not in output.lower():
            issues.append("Analysis lacks supporting evidence")
            recommendations.append("Provide evidence for each anomaly detected")
        
        # Check for severity classification
        severity_levels = ["low", "medium", "high", "critical"]
        if not any(level in output.lower() for level in severity_levels):
            recommendations.append("Include severity classifications for findings")
        
        return {
            "issues": issues,
            "recommendations": recommendations
        }
    
    @staticmethod
    def _validate_validator_output(output: str) -> Dict[str, Any]:
        """Validate validator agent output"""
        
        issues = []
        recommendations = []
        
        # Check for validation status
        if "validation_status" not in output.lower() and "status" not in output.lower():
            recommendations.append("Include clear validation status")
        
        # Check for confidence scores
        if "confidence" not in output.lower():
            recommendations.append("Include confidence scores for validation results")
        
        # Check for issues identification
        if "issues" not in output.lower() and "errors" not in output.lower():
            recommendations.append("Clearly identify any validation issues found")
        
        return {
            "issues": issues,
            "recommendations": recommendations
        }
    
    @staticmethod
    def _validate_reporter_output(output: str) -> Dict[str, Any]:
        """Validate reporter agent output"""
        
        issues = []
        recommendations = []
        
        # Check for executive summary
        if "executive_summary" not in output.lower() and "summary" not in output.lower():
            recommendations.append("Include executive summary")
        
        # Check for recommendations
        if "recommendations" not in output.lower():
            issues.append("Report lacks actionable recommendations")
            recommendations.append("Include specific, actionable recommendations")
        
        # Check for findings
        if "findings" not in output.lower():
            issues.append("Report lacks detailed findings")
            recommendations.append("Include detailed analysis findings")
        
        return {
            "issues": issues,
            "recommendations": recommendations
        }
    
    @staticmethod
    def _validate_general_output(output: str) -> Dict[str, Any]:
        """Validate general output quality"""
        
        issues = []
        recommendations = []
        
        # Check length
        if len(output.strip()) < 50:
            issues.append("Output is too brief")
            recommendations.append("Provide more detailed and comprehensive output")
        
        # Check for profanity or inappropriate content
        inappropriate_words = ["error", "failed", "exception"]  # Basic check
        found_inappropriate = [word for word in inappropriate_words if word in output.lower()]
        if found_inappropriate:
            recommendations.append("Review output for error messages that should be handled gracefully")
        
        # Check for timestamp
        if "timestamp" not in output.lower():
            recommendations.append("Include timestamp for audit trail")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations
        }
