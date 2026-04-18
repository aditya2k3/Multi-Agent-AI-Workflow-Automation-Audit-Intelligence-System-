"""
FastAPI Backend for AI Audit Automation System

This module provides REST API endpoints for:
- Running audit workflows
- Managing audit sessions
- Retrieving reports and results
- System health monitoring
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os
import uuid
import json
from datetime import datetime
import asyncio
import logging

# Import our modules
from workflows.audit_workflow import AuditWorkflow, AuditState
from agents import ExtractorAgent, AnalyzerAgent, ValidatorAgent, ReporterAgent
from tools import tool_registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Audit Automation System",
    description="Multi-agent AI system for automated audit workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for workflow management
active_workflows: Dict[str, AuditWorkflow] = {}
workflow_results: Dict[str, Dict[str, Any]] = {}

# Pydantic models for API
class AuditRequest(BaseModel):
    """Model for audit request"""
    data_source: str = Field(..., description="Data source type (file, database, api)")
    data_config: Dict[str, Any] = Field(..., description="Data source configuration")
    audit_config: Optional[Dict[str, Any]] = Field(None, description="Audit configuration options")

class AuditResponse(BaseModel):
    """Model for audit response"""
    audit_id: str
    status: str
    message: str
    timestamp: str

class WorkflowStatus(BaseModel):
    """Model for workflow status"""
    audit_id: str
    status: str
    progress: float
    current_step: str
    estimated_completion: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class ReportRequest(BaseModel):
    """Model for report request"""
    audit_id: str
    report_format: str = Field("json", description="Report format (json, pdf)")

# Initialize agents
def initialize_agents():
    """Initialize all agents with default configurations"""
    
    extractor_config = {
        "supported_formats": ["csv", "json", "sql"],
        "validation_enabled": True
    }
    
    analyzer_config = {
        "anomaly_threshold": 0.1,
        "ml_methods": ["isolation_forest"],
        "rule_methods": ["threshold", "pattern"]
    }
    
    validator_config = {
        "validation_rules": {
            "data_quality": {"min_completeness": 80},
            "business_rules": {"high_value_threshold": 10000}
        }
    }
    
    reporter_config = {
        "report_templates": {
            "executive": "standard",
            "detailed": "comprehensive"
        }
    }
    
    extractor_agent = ExtractorAgent(extractor_config)
    analyzer_agent = AnalyzerAgent(analyzer_config)
    validator_agent = ValidatorAgent(validator_config)
    reporter_agent = ReporterAgent(reporter_config)
    
    return extractor_agent, analyzer_agent, validator_agent, reporter_agent

# Dependency to get agents
def get_agents():
    """Get initialized agents"""
    return initialize_agents()

# Background task for running audit
async def run_audit_background(audit_id: str, request: AuditRequest, agents: tuple):
    """Run audit workflow in background"""
    
    try:
        extractor_agent, analyzer_agent, validator_agent, reporter_agent = agents
        
        # Create workflow
        workflow = AuditWorkflow(extractor_agent, analyzer_agent, validator_agent, reporter_agent)
        active_workflows[audit_id] = workflow
        
        # Prepare data based on data source
        raw_data = await prepare_data(request.data_source, request.data_config)
        
        # Run audit
        result = workflow.run_audit(raw_data, audit_id)
        
        # Store result
        workflow_results[audit_id] = result
        
        logger.info(f"Audit {audit_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Audit {audit_id} failed: {str(e)}")
        workflow_results[audit_id] = {
            "audit_id": audit_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        # Clean up active workflow
        if audit_id in active_workflows:
            del active_workflows[audit_id]

async def prepare_data(data_source: str, data_config: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare data based on data source type"""
    
    if data_source == "file":
        file_path = data_config.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"File not found: {file_path}")
        
        # Use CSV loader tool
        csv_result = tool_registry.csv_loader_tool({
            "file_path": file_path,
            "encoding": data_config.get("encoding", "utf-8")
        })
        
        if not csv_result["success"]:
            raise HTTPException(status_code=400, detail=f"Failed to load CSV: {csv_result['error']}")
        
        # Determine data type from file name or config
        file_name = os.path.basename(file_path).lower()
        if "transaction" in file_name:
            return {"transactions_data": csv_result["data"]}
        elif "invoice" in file_name:
            return {"invoices_data": csv_result["data"]}
        else:
            # Try to determine from columns
            if csv_result["data"]:
                columns = set(csv_result["data"][0].keys())
                if "transaction_id" in columns:
                    return {"transactions_data": csv_result["data"]}
                elif "invoice_id" in columns:
                    return {"invoices_data": csv_result["data"]}
            
            # Default to transactions
            return {"transactions_data": csv_result["data"]}
    
    elif data_source == "database":
        # Database data preparation
        db_config = data_config.get("connection", {})
        query = data_config.get("query", "")
        
        if not query:
            raise HTTPException(status_code=400, detail="Database query is required")
        
        # Use SQL query tool
        sql_result = tool_registry.sql_query_tool({
            "query": query,
            "database_path": db_config.get("database_path", ":memory:")
        })
        
        if not sql_result["success"]:
            raise HTTPException(status_code=400, detail=f"Database query failed: {sql_result['error']}")
        
        # Determine data type
        return {"transactions_data": sql_result["data"]}
    
    elif data_source == "api":
        # API data preparation (placeholder)
        api_url = data_config.get("url")
        if not api_url:
            raise HTTPException(status_code=400, detail="API URL is required")
        
        # This would implement API data fetching
        raise HTTPException(status_code=501, detail="API data source not yet implemented")
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported data source: {data_source}")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Audit Automation System API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_workflows": len(active_workflows),
        "completed_workflows": len(workflow_results)
    }

@app.post("/run-audit", response_model=AuditResponse)
async def run_audit(
    request: AuditRequest,
    background_tasks: BackgroundTasks,
    agents: tuple = Depends(get_agents)
):
    """Run audit workflow"""
    
    # Generate unique audit ID
    audit_id = f"AUDIT_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Start background task
    background_tasks.add_task(run_audit_background, audit_id, request, agents)
    
    return AuditResponse(
        audit_id=audit_id,
        status="started",
        message="Audit workflow started",
        timestamp=datetime.now().isoformat()
    )

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """Upload data file for audit"""
    
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate file
        if not file.filename.endswith(('.csv', '.json', '.xlsx')):
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        return {
            "message": "File uploaded successfully",
            "file_path": file_path,
            "file_size": len(content),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/audit-status/{audit_id}", response_model=WorkflowStatus)
async def get_audit_status(audit_id: str):
    """Get audit workflow status"""
    
    if audit_id in active_workflows:
        return WorkflowStatus(
            audit_id=audit_id,
            status="running",
            progress=50.0,  # Placeholder
            current_step="processing",
            estimated_completion=(datetime.now().isoformat())
        )
    
    elif audit_id in workflow_results:
        result = workflow_results[audit_id]
        return WorkflowStatus(
            audit_id=audit_id,
            status=result.get("status", "unknown"),
            progress=100.0,
            current_step="completed",
            result=result
        )
    
    else:
        raise HTTPException(status_code=404, detail="Audit not found")

@app.get("/audit-result/{audit_id}")
async def get_audit_result(audit_id: str):
    """Get complete audit results"""
    
    if audit_id not in workflow_results:
        raise HTTPException(status_code=404, detail="Audit result not found")
    
    return workflow_results[audit_id]

@app.post("/get-report")
async def get_report(request: ReportRequest):
    """Generate and retrieve audit report"""
    
    if request.audit_id not in workflow_results:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    result = workflow_results[request.audit_id]
    
    if request.report_format == "json":
        # Return JSON report
        return result
    
    elif request.report_format == "pdf":
        # Return PDF report
        report_data = result.get("report_data", {})
        pdf_path = report_data.get("metadata", {}).get("pdf_path")
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF report not found")
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"audit_report_{request.audit_id}.pdf"
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported report format")

@app.get("/list-audits")
async def list_audits():
    """List all audits"""
    
    audits = []
    
    # Add active audits
    for audit_id in active_workflows:
        audits.append({
            "audit_id": audit_id,
            "status": "running",
            "timestamp": datetime.now().isoformat()
        })
    
    # Add completed audits
    for audit_id, result in workflow_results.items():
        audits.append({
            "audit_id": audit_id,
            "status": result.get("status", "unknown"),
            "timestamp": result.get("timestamp", datetime.now().isoformat())
        })
    
    # Sort by timestamp (newest first)
    audits.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {"audits": audits}

@app.delete("/audit/{audit_id}")
async def delete_audit(audit_id: str):
    """Delete audit data"""
    
    if audit_id in active_workflows:
        raise HTTPException(status_code=400, detail="Cannot delete running audit")
    
    if audit_id in workflow_results:
        del workflow_results[audit_id]
        return {"message": f"Audit {audit_id} deleted successfully"}
    
    else:
        raise HTTPException(status_code=404, detail="Audit not found")

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    
    tools = []
    for tool_name in tool_registry.list_tools():
        tools.append({
            "name": tool_name,
            "description": f"MCP tool: {tool_name}",
            "available": True
        })
    
    return {"tools": tools}

@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, params: Dict[str, Any]):
    """Execute an MCP tool"""
    
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    try:
        result = tool(params)
        return {
            "tool": tool_name,
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@app.get("/system-info")
async def get_system_info():
    """Get system information"""
    
    return {
        "system": "AI Audit Automation System",
        "version": "1.0.0",
        "components": {
            "agents": ["ExtractorAgent", "AnalyzerAgent", "ValidatorAgent", "ReporterAgent"],
            "tools": tool_registry.list_tools(),
            "workflow": "LangGraph"
        },
        "statistics": {
            "active_workflows": len(active_workflows),
            "completed_audits": len(workflow_results),
            "available_tools": len(tool_registry.list_tools())
        },
        "timestamp": datetime.now().isoformat()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("AI Audit Automation System starting up...")
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    logger.info("System startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("AI Audit Automation System shutting down...")
    
    # Cleanup active workflows
    active_workflows.clear()
    
    logger.info("System shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
