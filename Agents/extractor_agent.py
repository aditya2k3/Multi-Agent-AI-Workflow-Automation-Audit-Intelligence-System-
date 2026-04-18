import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json
from .base_agent import BaseAgent

class ExtractorAgent(BaseAgent):
    """Agent responsible for data extraction and preprocessing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ExtractorAgent", config)
        self.supported_formats = ['csv', 'json', 'sql']
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method for data extraction"""
        return self.extract_data(data)
    
    def extract_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and preprocess data from various sources"""
        
        self.log_action("Starting data extraction", {
            "data_types": list(raw_data.keys()) if raw_data else []
        })
        
        try:
            extracted = {
                "transactions": [],
                "invoices": [],
                "metadata": {
                    "extraction_timestamp": pd.Timestamp.now().isoformat(),
                    "total_records": 0,
                    "data_sources": []
                }
            }
            
            # Process transactions data
            if 'transactions_file' in raw_data:
                transactions = self._extract_from_csv(raw_data['transactions_file'], 'transactions')
                extracted["transactions"] = transactions
                extracted["metadata"]["data_sources"].append("transactions_csv")
                
            elif 'transactions_data' in raw_data:
                transactions = self._process_dataframe(raw_data['transactions_data'], 'transactions')
                extracted["transactions"] = transactions
                extracted["metadata"]["data_sources"].append("transactions_data")
            
            # Process invoices data
            if 'invoices_file' in raw_data:
                invoices = self._extract_from_csv(raw_data['invoices_file'], 'invoices')
                extracted["invoices"] = invoices
                extracted["metadata"]["data_sources"].append("invoices_csv")
                
            elif 'invoices_data' in raw_data:
                invoices = self._process_dataframe(raw_data['invoices_data'], 'invoices')
                extracted["invoices"] = invoices
                extracted["metadata"]["data_sources"].append("invoices_data")
            
            # Calculate metadata
            extracted["metadata"]["total_records"] = len(extracted["transactions"]) + len(extracted["invoices"])
            extracted["metadata"]["transaction_count"] = len(extracted["transactions"])
            extracted["metadata"]["invoice_count"] = len(extracted["invoices"])
            
            self.log_action("Data extraction completed", {
                "total_records": extracted["metadata"]["total_records"],
                "transactions": len(extracted["transactions"]),
                "invoices": len(extracted["invoices"])
            })
            
            return extracted
            
        except Exception as e:
            self.log_action("Extraction failed", {"error": str(e)})
            raise
    
    def _extract_from_csv(self, file_path: str, data_type: str) -> List[Dict[str, Any]]:
        """Extract data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            return self._process_dataframe(df, data_type)
        except Exception as e:
            self.log_action("CSV extraction failed", {"file": file_path, "error": str(e)})
            raise
    
    def _process_dataframe(self, df: pd.DataFrame, data_type: str) -> List[Dict[str, Any]]:
        """Process pandas DataFrame and return structured data"""
        
        # Data cleaning and preprocessing
        df = self._clean_data(df, data_type)
        
        # Convert to list of dictionaries
        records = df.to_dict('records')
        
        # Add additional processing based on data type
        if data_type == 'transactions':
            records = self._process_transactions(records)
        elif data_type == 'invoices':
            records = self._process_invoices(records)
        
        return records
    
    def _clean_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Clean and preprocess data"""
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        if data_type == 'transactions':
            numeric_columns = ['amount', 'risk_score']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df[col] = df[col].fillna(0)
        
        elif data_type == 'invoices':
            numeric_columns = ['amount', 'risk_score', 'due_days']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df[col] = df[col].fillna(0)
        
        # Convert date columns
        date_columns = ['date', 'due_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _process_transactions(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Additional processing for transaction records"""
        
        processed = []
        for record in records:
            # Calculate additional metrics
            if 'amount' in record and record['amount'] > 0:
                record['amount_category'] = self._categorize_amount(record['amount'])
                record['is_round_amount'] = float(record['amount']).is_integer() and record['amount'] > 1000
            
            # Add risk indicators
            record['risk_indicators'] = self._calculate_risk_indicators(record)
            
            processed.append(record)
        
        return processed
    
    def _process_invoices(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Additional processing for invoice records"""
        
        processed = []
        for record in records:
            # Calculate aging
            if 'date' in record and 'due_date' in record:
                record['aging_days'] = (pd.Timestamp.now() - pd.Timestamp(record['date'])).days
                record['overdue'] = record['aging_days'] > record.get('due_days', 30)
            
            # Add risk indicators
            record['risk_indicators'] = self._calculate_invoice_risk_indicators(record)
            
            processed.append(record)
        
        return processed
    
    def _categorize_amount(self, amount: float) -> str:
        """Categorize transaction amount"""
        if amount < 100:
            return 'small'
        elif amount < 1000:
            return 'medium'
        elif amount < 10000:
            return 'large'
        else:
            return 'very_large'
    
    def _calculate_risk_indicators(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk indicators for transactions"""
        indicators = {
            "high_amount": record.get('amount', 0) > 10000,
            "round_amount": float(record.get('amount', 0)).is_integer() and record.get('amount', 0) > 1000,
            "unusual_category": record.get('category') in ['Capex', 'Travel'],
            "weekend_transaction": False  # Would need date parsing
        }
        
        # Count risk indicators
        indicators["risk_count"] = sum(indicators.values())
        indicators["risk_level"] = 'low' if indicators["risk_count"] <= 1 else 'medium' if indicators["risk_count"] <= 2 else 'high'
        
        return indicators
    
    def _calculate_invoice_risk_indicators(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk indicators for invoices"""
        indicators = {
            "high_amount": record.get('amount', 0) > 25000,
            "overdue": record.get('overdue', False),
            "unusual_terms": record.get('due_days', 0) < 15,
            "round_amount": float(record.get('amount', 0)).is_integer() and record.get('amount', 0) > 5000
        }
        
        # Count risk indicators
        indicators["risk_count"] = sum(indicators.values())
        indicators["risk_level"] = 'low' if indicators["risk_count"] <= 1 else 'medium' if indicators["risk_count"] <= 2 else 'high'
        
        return indicators
