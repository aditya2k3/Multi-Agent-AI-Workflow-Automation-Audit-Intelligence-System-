import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_transactions(n_records=1000):
    """Generate synthetic transaction data with anomalies"""
    
    # Base dates
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=random.randint(0, 365)) for _ in range(n_records)]
    
    # Normal transactions
    data = []
    for i in range(n_records):
        # 80% normal transactions
        if i < n_records * 0.8:
            amount = round(np.random.normal(1000, 300), 2)
            amount = max(50, min(amount, 5000))  # Clamp to reasonable range
            risk_score = np.random.uniform(0.1, 0.4)
        # 20% anomalous transactions
        else:
            anomaly_type = random.choice(['high_amount', 'round_number', 'unusual_time', 'duplicate'])
            
            if anomaly_type == 'high_amount':
                amount = round(np.random.uniform(10000, 50000), 2)
                risk_score = np.random.uniform(0.7, 0.9)
            elif anomaly_type == 'round_number':
                amount = round(random.choice([10000, 25000, 50000, 100000]), 2)
                risk_score = np.random.uniform(0.6, 0.8)
            elif anomaly_type == 'unusual_time':
                amount = round(np.random.normal(1000, 300), 2)
                risk_score = np.random.uniform(0.5, 0.7)
            else:  # duplicate
                amount = round(np.random.normal(1000, 300), 2)
                risk_score = np.random.uniform(0.6, 0.8)
        
        transaction = {
            'transaction_id': f'TXN{100000 + i}',
            'date': dates[i].strftime('%Y-%m-%d'),
            'amount': amount,
            'account_id': f'ACC{random.randint(1000, 9999)}',
            'description': random.choice([
                'Office Supplies', 'Software License', 'Consulting Services',
                'Travel Expenses', 'Marketing Campaign', 'Equipment Purchase',
                'Salary Payment', 'Vendor Payment', 'Client Refund'
            ]),
            'category': random.choice(['Opex', 'Capex', 'Salary', 'Travel', 'Marketing']),
            'risk_score': risk_score,
            'anomaly_flag': risk_score > 0.6
        }
        data.append(transaction)
    
    df = pd.DataFrame(data)
    df.to_csv('transactions.csv', index=False)
    return df

def generate_invoices(n_records=500):
    """Generate synthetic invoice data with anomalies"""
    
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=random.randint(0, 365)) for _ in range(n_records)]
    
    data = []
    for i in range(n_records):
        # 85% normal invoices
        if i < n_records * 0.85:
            amount = round(np.random.normal(5000, 1500), 2)
            amount = max(100, min(amount, 25000))
            due_days = random.randint(30, 90)
            risk_score = np.random.uniform(0.1, 0.3)
        # 15% anomalous invoices
        else:
            anomaly_type = random.choice(['overdue', 'unusual_terms', 'duplicate', 'round_amount'])
            
            if anomaly_type == 'overdue':
                amount = round(np.random.normal(5000, 1500), 2)
                due_days = random.randint(180, 365)  # Very overdue
                risk_score = np.random.uniform(0.7, 0.9)
            elif anomaly_type == 'unusual_terms':
                amount = round(np.random.normal(5000, 1500), 2)
                due_days = random.choice([0, 7, 14])  # Unusual payment terms
                risk_score = np.random.uniform(0.5, 0.7)
            elif anomaly_type == 'duplicate':
                amount = round(np.random.normal(5000, 1500), 2)
                due_days = random.randint(30, 90)
                risk_score = np.random.uniform(0.6, 0.8)
            else:  # round_amount
                amount = round(random.choice([10000, 20000, 50000, 100000]), 2)
                due_days = random.randint(30, 90)
                risk_score = np.random.uniform(0.5, 0.7)
        
        invoice = {
            'invoice_id': f'INV{200000 + i}',
            'date': dates[i].strftime('%Y-%m-%d'),
            'due_date': (dates[i] + timedelta(days=due_days)).strftime('%Y-%m-%d'),
            'amount': amount,
            'vendor_id': f'VEN{random.randint(100, 999)}',
            'vendor_name': random.choice([
                'Tech Solutions Inc', 'Global Consulting Ltd', 'Office Supplies Co',
                'Software Services LLC', 'Marketing Experts Inc', 'Equipment Pro'
            ]),
            'category': random.choice(['Software', 'Consulting', 'Supplies', 'Equipment', 'Services']),
            'due_days': due_days,
            'risk_score': risk_score,
            'anomaly_flag': risk_score > 0.5
        }
        data.append(invoice)
    
    df = pd.DataFrame(data)
    df.to_csv('invoices.csv', index=False)
    return df

if __name__ == "__main__":
    print("Generating synthetic audit data...")
    
    # Generate datasets
    transactions_df = generate_transactions(1000)
    invoices_df = generate_invoices(500)
    
    print(f"Generated {len(transactions_df)} transactions")
    print(f"Generated {len(invoices_df)} invoices")
    print(f"Transaction anomalies: {transactions_df['anomaly_flag'].sum()}")
    print(f"Invoice anomalies: {invoices_df['anomaly_flag'].sum()}")
    
    # Create summary statistics
    summary = {
        'total_transactions': len(transactions_df),
        'transaction_anomalies': transactions_df['anomaly_flag'].sum(),
        'total_invoices': len(invoices_df),
        'invoice_anomalies': invoices_df['anomaly_flag'].sum(),
        'avg_transaction_amount': transactions_df['amount'].mean(),
        'avg_invoice_amount': invoices_df['amount'].mean()
    }
    
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv('data_summary.csv', index=False)
    
    print("Data generation complete!")
