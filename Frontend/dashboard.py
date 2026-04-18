"""
Streamlit Dashboard for AI Audit Automation System

This module provides an interactive web interface for:
- Uploading and managing audit data
- Running audit workflows
- Visualizing results and anomalies
- Downloading reports
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import os
from datetime import datetime, timedelta
import time
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000"
st.set_page_config(
    page_title="AI Audit Automation System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-running {
        color: #ff9800;
        font-weight: bold;
    }
    .status-completed {
        color: #4caf50;
        font-weight: bold;
    }
    .status-failed {
        color: #f44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def api_call(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make API call to backend"""
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def upload_file(uploaded_file) -> str:
    """Upload file to backend"""
    
    if uploaded_file is None:
        return None
    
    try:
        files = {"file": uploaded_file}
        response = requests.post(f"{API_BASE_URL}/upload-data", files=files)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("file_path")
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def run_audit(file_path: str, data_source: str = "file") -> str:
    """Run audit workflow"""
    
    audit_request = {
        "data_source": data_source,
        "data_config": {
            "file_path": file_path,
            "encoding": "utf-8"
        },
        "audit_config": {
            "anomaly_threshold": 0.1,
            "generate_report": True
        }
    }
    
    result = api_call("/run-audit", "POST", audit_request)
    
    if result:
        return result.get("audit_id")
    else:
        return None

def get_audit_status(audit_id: str) -> Dict[str, Any]:
    """Get audit status"""
    
    result = api_call(f"/audit-status/{audit_id}")
    return result

def get_audit_result(audit_id: str) -> Dict[str, Any]:
    """Get audit result"""
    
    result = api_call(f"/audit-result/{audit_id}")
    return result

def list_audits() -> List[Dict[str, Any]]:
    """List all audits"""
    
    result = api_call("/list-audits")
    if result:
        return result.get("audits", [])
    return []

def create_anomaly_chart(anomalies: List[Dict[str, Any]]) -> go.Figure:
    """Create anomaly visualization chart"""
    
    if not anomalies:
        fig = go.Figure()
        fig.add_annotation(
            text="No anomalies found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Prepare data
    df = pd.DataFrame(anomalies)
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Anomaly Severity Distribution", "Anomaly Amounts", 
                       "Detection Methods", "Anomaly Timeline"),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # Severity distribution
    severity_counts = df['severity'].value_counts()
    fig.add_trace(
        go.Pie(labels=severity_counts.index, values=severity_counts.values, name="Severity"),
        row=1, col=1
    )
    
    # Amounts by severity
    if 'amount' in df.columns:
        severity_amounts = df.groupby('severity')['amount'].mean()
        fig.add_trace(
            go.Bar(x=severity_amounts.index, y=severity_amounts.values, name="Avg Amount"),
            row=1, col=2
        )
    
    # Detection methods
    if 'detection_method' in df.columns:
        method_counts = df['detection_method'].value_counts()
        fig.add_trace(
            go.Bar(x=method_counts.index, y=method_counts.values, name="Detection Method"),
            row=2, col=1
        )
    
    # Timeline (if dates available)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        daily_counts = df.groupby(df['date'].dt.date).size()
        fig.add_trace(
            go.Scatter(x=daily_counts.index, y=daily_counts.values, mode='lines+markers', name="Daily Anomalies"),
            row=2, col=2
        )
    
    fig.update_layout(height=600, showlegend=False)
    return fig

def create_risk_dashboard(analysis_results: Dict[str, Any]) -> go.Figure:
    """Create risk assessment dashboard"""
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Risk Score Distribution", "Anomaly Trends", 
                       "Risk by Category", "Overall Risk Assessment"),
        specs=[[{"type": "indicator"}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "gauge"}]]
    )
    
    # Overall risk score
    overall_risk = analysis_results.get("summary", {}).get("overall_risk_score", 0)
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=overall_risk,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Risk Score"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 30], 'color': "lightgray"},
                       {'range': [30, 60], 'color': "yellow"},
                       {'range': [60, 100], 'color': "red"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': 80}}
        ),
        row=1, col=1
    )
    
    # Anomaly trends
    tx_anomalies = analysis_results.get("transaction_analysis", {}).get("anomaly_count", 0)
    inv_anomalies = analysis_results.get("invoice_analysis", {}).get("anomaly_count", 0)
    
    fig.add_trace(
        go.Bar(x=['Transactions', 'Invoices'], y=[tx_anomalies, inv_anomalies], name="Anomaly Count"),
        row=1, col=2
    )
    
    # Risk by category (placeholder data)
    categories = ['High', 'Medium', 'Low']
    values = [30, 45, 25]  # Placeholder
    
    fig.add_trace(
        go.Pie(labels=categories, values=values, name="Risk Distribution"),
        row=2, col=1
    )
    
    # Risk gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge",
            value=overall_risk,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Risk Level"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkred"},
                   'steps': [
                       {'range': [0, 30], 'color': "green"},
                       {'range': [30, 60], 'color': "yellow"},
                       {'range': [60, 100], 'color': "red"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': 80}}
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    return fig

# Main application
def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔍 AI Audit Automation System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", [
        "Dashboard", "Upload Data", "Run Audit", "Results", "Reports", "System Info"
    ])
    
    # Initialize session state
    if 'current_audit_id' not in st.session_state:
        st.session_state.current_audit_id = None
    if 'audit_results' not in st.session_state:
        st.session_state.audit_results = {}
    
    # Page content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload Data":
        show_upload_page()
    elif page == "Run Audit":
        show_run_audit_page()
    elif page == "Results":
        show_results_page()
    elif page == "Reports":
        show_reports_page()
    elif page == "System Info":
        show_system_info_page()

def show_dashboard():
    """Show main dashboard"""
    
    st.header("📊 Audit Dashboard")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Get system info
        system_info = api_call("/system-info")
        if system_info:
            stats = system_info.get("statistics", {})
            st.metric("Active Workflows", stats.get("active_workflows", 0))
    
    with col2:
        if system_info:
            st.metric("Completed Audits", stats.get("completed_audits", 0))
    
    with col3:
        # Get recent audits
        audits = list_audits()
        completed = len([a for a in audits if a.get("status") == "completed"])
        st.metric("Successful Audits", completed)
    
    with col4:
        if system_info:
            st.metric("Available Tools", stats.get("available_tools", 0))
    
    # Recent audits
    st.subheader("📋 Recent Audits")
    
    if audits:
        df_audits = pd.DataFrame(audits)
        
        # Add status styling
        def style_status(status):
            if status == "running":
                return f'<span class="status-running">{status}</span>'
            elif status == "completed":
                return f'<span class="status-completed">{status}</span>'
            else:
                return f'<span class="status-failed">{status}</span>'
        
        df_audits['status'] = df_audits['status'].apply(style_status)
        
        st.write(df_audits.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.info("No audits found. Upload data and run an audit to get started.")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload New Data", type="primary"):
            st.session_state.page = "Upload Data"
            st.rerun()
    
    with col2:
        if st.button("▶️ Run Audit", type="primary"):
            st.session_state.page = "Run Audit"
            st.rerun()
    
    with col3:
        if st.button("📄 View Reports"):
            st.session_state.page = "Reports"
            st.rerun()

def show_upload_page():
    """Show data upload page"""
    
    st.header("📤 Upload Audit Data")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload transaction or invoice data in CSV format"
    )
    
    if uploaded_file is not None:
        st.success(f"File selected: {uploaded_file.name}")
        
        # Show file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        
        st.json(file_details)
        
        # Preview data
        st.subheader("📋 Data Preview")
        
        try:
            df = pd.read_csv(uploaded_file)
            st.write(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            st.dataframe(df.head(10))
            
            # Column info
            st.subheader("📊 Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum()
            })
            st.dataframe(col_info)
            
            # Upload button
            if st.button("🚀 Upload and Process", type="primary"):
                with st.spinner("Uploading file..."):
                    file_path = upload_file(uploaded_file)
                    
                    if file_path:
                        st.success(f"File uploaded successfully: {file_path}")
                        st.session_state.uploaded_file_path = file_path
                    else:
                        st.error("Upload failed")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

def show_run_audit_page():
    """Show run audit page"""
    
    st.header("▶️ Run Audit Workflow")
    
    # Check for uploaded file
    if 'uploaded_file_path' not in st.session_state:
        st.warning("Please upload data first.")
        return
    
    file_path = st.session_state.uploaded_file_path
    st.info(f"Using file: {file_path}")
    
    # Audit configuration
    st.subheader("⚙️ Audit Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        anomaly_threshold = st.slider(
            "Anomaly Detection Threshold",
            min_value=0.01, max_value=0.5, value=0.1, step=0.01,
            help="Lower values detect more anomalies"
        )
        
        generate_report = st.checkbox("Generate Report", value=True)
    
    with col2:
        data_source = st.selectbox(
            "Data Source Type",
            ["file", "database", "api"],
            help="Type of data source to analyze"
        )
        
        audit_type = st.selectbox(
            "Audit Type",
            ["Financial", "Compliance", "Operational", "Custom"],
            help="Type of audit to perform"
        )
    
    # Run audit button
    if st.button("🚀 Start Audit", type="primary"):
        with st.spinner("Starting audit workflow..."):
            audit_id = run_audit(file_path, data_source)
            
            if audit_id:
                st.session_state.current_audit_id = audit_id
                st.success(f"Audit started successfully! Audit ID: {audit_id}")
                
                # Start status monitoring
                st.session_state.monitoring = True
            else:
                st.error("Failed to start audit")
    
    # Monitor current audit
    if st.session_state.get("current_audit_id") and st.session_state.get("monitoring"):
        st.subheader("📊 Audit Progress")
        
        audit_id = st.session_state.current_audit_id
        
        # Create placeholder for status
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        # Monitor progress
        for _ in range(60):  # Monitor for up to 60 seconds
            status = get_audit_status(audit_id)
            
            if status:
                status_data = status.get("result", {})
                audit_status = status_data.get("status", "unknown")
                
                # Update status
                status_placeholder.json(status)
                
                # Update progress
                if audit_status == "running":
                    progress = status.get("progress", 0)
                    progress_placeholder.progress(progress / 100)
                    time.sleep(2)
                elif audit_status == "completed":
                    progress_placeholder.progress(1.0)
                    st.success("Audit completed successfully!")
                    st.session_state.monitoring = False
                    
                    # Store results
                    result = get_audit_result(audit_id)
                    if result:
                        st.session_state.audit_results[audit_id] = result
                    
                    break
                elif audit_status == "failed":
                    st.error("Audit failed!")
                    st.session_state.monitoring = False
                    break
            else:
                st.error("Failed to get audit status")
                break

def show_results_page():
    """Show audit results page"""
    
    st.header("📈 Audit Results")
    
    # Select audit
    audits = list_audits()
    if not audits:
        st.info("No audit results available.")
        return
    
    audit_options = [f"{a['audit_id']} - {a['status']}" for a in audits]
    selected_audit = st.selectbox("Select Audit", audit_options)
    
    if selected_audit:
        audit_id = selected_audit.split(" - ")[0]
        
        # Get results
        result = get_audit_result(audit_id)
        
        if result:
            # Summary metrics
            st.subheader("📊 Summary Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                analysis_results = result.get("analysis_results", {})
                total_anomalies = analysis_results.get("summary", {}).get("total_anomalies", 0)
                st.metric("Total Anomalies", total_anomalies)
            
            with col2:
                high_risk_items = analysis_results.get("summary", {}).get("high_risk_items", [])
                st.metric("High Risk Items", len(high_risk_items))
            
            with col3:
                overall_risk = analysis_results.get("summary", {}).get("overall_risk_score", 0)
                st.metric("Risk Score", f"{overall_risk:.1f}")
            
            with col4:
                validation_results = result.get("validation_results", {})
                confidence = validation_results.get("summary", {}).get("confidence_score", 0)
                st.metric("Confidence", f"{confidence:.1f}%")
            
            # Anomaly visualization
            st.subheader("🔍 Anomaly Analysis")
            
            # Transaction anomalies
            tx_anomalies = analysis_results.get("transaction_analysis", {}).get("combined_anomalies", [])
            if tx_anomalies:
                st.write("**Transaction Anomalies**")
                fig = create_anomaly_chart(tx_anomalies)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show anomaly details
                if st.checkbox("Show Transaction Anomaly Details"):
                    df_anomalies = pd.DataFrame(tx_anomalies)
                    st.dataframe(df_anomalies)
            
            # Invoice anomalies
            inv_anomalies = analysis_results.get("invoice_analysis", {}).get("combined_anomalies", [])
            if inv_anomalies:
                st.write("**Invoice Anomalies**")
                fig = create_anomaly_chart(inv_anomalies)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show anomaly details
                if st.checkbox("Show Invoice Anomaly Details"):
                    df_anomalies = pd.DataFrame(inv_anomalies)
                    st.dataframe(df_anomalies)
            
            # Risk dashboard
            st.subheader("⚠️ Risk Assessment")
            fig_risk = create_risk_dashboard(analysis_results)
            st.plotly_chart(fig_risk, use_container_width=True)
            
            # Recommendations
            st.subheader("💡 Recommendations")
            recommendations = analysis_results.get("summary", {}).get("recommendations", [])
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")
            else:
                st.info("No recommendations available.")
            
            # Validation results
            st.subheader("✅ Validation Results")
            validation_summary = validation_results.get("summary", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Validation Status**")
                st.write(validation_summary.get("validation_status", "Unknown"))
            
            with col2:
                st.write("**Confidence Score**")
                st.write(f"{validation_summary.get('confidence_score', 0):.1f}%")
            
            # Issues found
            issues = validation_summary.get("issues_found", [])
            if issues:
                st.write("**Issues Found:**")
                for issue in issues:
                    st.error(f"• {issue.get('description', 'Unknown issue')}")
            
            # Download results
            st.subheader("💾 Download Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Download JSON Report"):
                    json_data = json.dumps(result, indent=2, default=str)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"audit_results_{audit_id}.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("📊 Download CSV Summary"):
                    # Create summary CSV
                    summary_data = {
                        "Audit ID": [audit_id],
                        "Total Anomalies": [total_anomalies],
                        "High Risk Items": [len(high_risk_items)],
                        "Risk Score": [overall_risk],
                        "Confidence Score": [confidence]
                    }
                    df_summary = pd.DataFrame(summary_data)
                    csv_data = df_summary.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"audit_summary_{audit_id}.csv",
                        mime="text/csv"
                    )

def show_reports_page():
    """Show reports page"""
    
    st.header("📄 Audit Reports")
    
    # Select audit for report generation
    audits = list_audits()
    completed_audits = [a for a in audits if a.get("status") == "completed"]
    
    if not completed_audits:
        st.info("No completed audits available for report generation.")
        return
    
    audit_options = [a['audit_id'] for a in completed_audits]
    selected_audit = st.selectbox("Select Audit for Report", audit_options)
    
    if selected_audit:
        st.info(f"Generating report for: {selected_audit}")
        
        # Report format selection
        report_format = st.selectbox("Report Format", ["json", "pdf"])
        
        # Generate report button
        if st.button("📄 Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                report_request = {
                    "audit_id": selected_audit,
                    "report_format": report_format
                }
                
                result = api_call("/get-report", "POST", report_request)
                
                if result:
                    if report_format == "json":
                        st.success("JSON report generated successfully!")
                        st.json(result)
                    else:
                        st.success("PDF report generated successfully!")
                        st.info("PDF report is available for download from the API.")
                else:
                    st.error("Failed to generate report")

def show_system_info_page():
    """Show system information page"""
    
    st.header("ℹ️ System Information")
    
    # Get system info
    system_info = api_call("/system-info")
    
    if system_info:
        # System overview
        st.subheader("🖥️ System Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("System Version", system_info.get("version", "Unknown"))
        
        with col2:
            stats = system_info.get("statistics", {})
            st.metric("Active Workflows", stats.get("active_workflows", 0))
        
        with col3:
            st.metric("Completed Audits", stats.get("completed_audits", 0))
        
        # Components
        st.subheader("🔧 System Components")
        
        components = system_info.get("components", {})
        
        st.write("**Agents:**")
        for agent in components.get("agents", []):
            st.write(f"• {agent}")
        
        st.write("**Tools:**")
        for tool in components.get("tools", []):
            st.write(f"• {tool}")
        
        st.write("**Workflow Engine:**")
        st.write(f"• {components.get('workflow', 'Unknown')}")
        
        # Available tools
        st.subheader("🛠️ Available Tools")
        
        tools_info = api_call("/tools")
        if tools_info:
            df_tools = pd.DataFrame(tools_info.get("tools", []))
            st.dataframe(df_tools)
        
        # System health
        st.subheader("🏥 System Health")
        
        health_info = api_call("/health")
        if health_info:
            st.write(f"**Status:** {health_info.get('status', 'Unknown')}")
            st.write(f"**Timestamp:** {health_info.get('timestamp', 'Unknown')}")
    
    # Test tool execution
    st.subheader("🧪 Tool Testing")
    
    tool_name = st.selectbox("Select Tool to Test", tool_registry.list_tools())
    
    if tool_name:
        st.write(f"**Tool:** {tool_name}")
        
        # Example parameters for common tools
        if tool_name == "csv_loader":
            params = {
                "file_path": "data/transactions.csv",
                "sample_rows": 5
            }
        elif tool_name == "sql_query":
            params = {
                "query": "SELECT COUNT(*) as count FROM transactions LIMIT 1",
                "database_path": ":memory:"
            }
        elif tool_name == "python_executor":
            params = {
                "code": "result = 2 + 2\nprint('Hello from Python tool!')",
                "variables": {}
            }
        else:
            params = {}
        
        if st.button("🧪 Test Tool"):
            with st.spinner("Testing tool..."):
                result = api_call(f"/tools/{tool_name}", "POST", params)
                
                if result:
                    st.success("Tool executed successfully!")
                    st.json(result)
                else:
                    st.error("Tool execution failed")

if __name__ == "__main__":
    main()
