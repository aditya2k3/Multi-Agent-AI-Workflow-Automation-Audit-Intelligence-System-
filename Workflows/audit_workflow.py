from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import TypedDict, List, Dict, Any, Annotated
import json
from datetime import datetime

class AuditState(TypedDict):
    """State for the audit workflow"""
    messages: Annotated[List, add_messages]
    raw_data: Dict[str, Any]
    extracted_data: Dict[str, Any]
    analysis_results: Dict[str, Any]
    validation_results: Dict[str, Any]
    report_data: Dict[str, Any]
    audit_id: str
    timestamp: str
    status: str
    errors: List[str]

class AuditWorkflow:
    """Main audit workflow orchestration using LangGraph"""
    
    def __init__(self, extractor_agent, analyzer_agent, validator_agent, reporter_agent):
        self.extractor_agent = extractor_agent
        self.analyzer_agent = analyzer_agent
        self.validator_agent = validator_agent
        self.reporter_agent = reporter_agent
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AuditState)
        
        # Add nodes
        workflow.add_node("extractor", self._extractor_node)
        workflow.add_node("analyzer", self._analyzer_node)
        workflow.add_node("validator", self._validator_node)
        workflow.add_node("reporter", self._reporter_node)
        
        # Add edges
        workflow.set_entry_point("extractor")
        workflow.add_edge("extractor", "analyzer")
        workflow.add_edge("analyzer", "validator")
        workflow.add_edge("validator", "reporter")
        workflow.add_edge("reporter", END)
        
        return workflow.compile()
    
    def _extractor_node(self, state: AuditState) -> AuditState:
        """Extractor agent node"""
        try:
            print(f"[{datetime.now()}] Starting data extraction...")
            
            # Call extractor agent
            extraction_result = self.extractor_agent.extract_data(state["raw_data"])
            
            state["extracted_data"] = extraction_result
            state["status"] = "extracted"
            state["messages"].append({
                "role": "system",
                "content": f"Data extraction completed. Found {extraction_result.get('record_count', 0)} records."
            })
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Extraction failed: {str(e)}")
            state["status"] = "extraction_failed"
            return state
    
    def _analyzer_node(self, state: AuditState) -> AuditState:
        """Analyzer agent node"""
        try:
            print(f"[{datetime.now()}] Starting anomaly analysis...")
            
            # Call analyzer agent
            analysis_result = self.analyzer_agent.analyze_data(state["extracted_data"])
            
            state["analysis_results"] = analysis_result
            state["status"] = "analyzed"
            state["messages"].append({
                "role": "system", 
                "content": f"Analysis completed. Found {analysis_result.get('anomaly_count', 0)} anomalies."
            })
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Analysis failed: {str(e)}")
            state["status"] = "analysis_failed"
            return state
    
    def _validator_node(self, state: AuditState) -> AuditState:
        """Validator agent node"""
        try:
            print(f"[{datetime.now()}] Starting validation...")
            
            # Call validator agent
            validation_result = self.validator_agent.validate_findings(
                state["extracted_data"], 
                state["analysis_results"]
            )
            
            state["validation_results"] = validation_result
            state["status"] = "validated"
            state["messages"].append({
                "role": "system",
                "content": f"Validation completed. {validation_result.get('validation_status', 'unknown')}"
            })
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Validation failed: {str(e)}")
            state["status"] = "validation_failed"
            return state
    
    def _reporter_node(self, state: AuditState) -> AuditState:
        """Reporter agent node"""
        try:
            print(f"[{datetime.now()}] Generating audit report...")
            
            # Call reporter agent
            report_result = self.reporter_agent.generate_report(
                state["extracted_data"],
                state["analysis_results"],
                state["validation_results"]
            )
            
            state["report_data"] = report_result
            state["status"] = "completed"
            state["messages"].append({
                "role": "system",
                "content": f"Report generated successfully. Risk score: {report_result.get('overall_risk_score', 0)}"
            })
            
            return state
            
        except Exception as e:
            state["errors"].append(f"Report generation failed: {str(e)}")
            state["status"] = "report_failed"
            return state
    
    def run_audit(self, raw_data: Dict[str, Any], audit_id: str = None) -> Dict[str, Any]:
        """Run the complete audit workflow"""
        
        if audit_id is None:
            audit_id = f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize state
        initial_state = AuditState(
            messages=[],
            raw_data=raw_data,
            extracted_data={},
            analysis_results={},
            validation_results={},
            report_data={},
            audit_id=audit_id,
            timestamp=datetime.now().isoformat(),
            status="initialized",
            errors=[]
        )
        
        try:
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Prepare result
            result = {
                "audit_id": final_state["audit_id"],
                "timestamp": final_state["timestamp"],
                "status": final_state["status"],
                "extracted_data": final_state["extracted_data"],
                "analysis_results": final_state["analysis_results"],
                "validation_results": final_state["validation_results"],
                "report_data": final_state["report_data"],
                "messages": final_state["messages"],
                "errors": final_state["errors"]
            }
            
            return result
            
        except Exception as e:
            return {
                "audit_id": audit_id,
                "timestamp": datetime.now().isoformat(),
                "status": "workflow_failed",
                "error": str(e),
                "errors": [f"Workflow execution failed: {str(e)}"]
            }
    
    def get_workflow_status(self, audit_id: str) -> Dict[str, Any]:
        """Get the status of a running audit workflow"""
        # This would be implemented with actual workflow tracking in production
        return {
            "audit_id": audit_id,
            "status": "unknown",
            "message": "Status tracking not implemented in this demo"
        }
