"""
Universal Dataset Examples

This script demonstrates how the AI Data Analyst can now work with ANY dataset.
"""

import pandas as pd
import os

# Create example datasets of different types to demonstrate universal capability

# 1. Customer dataset
customers_data = {
    'customer_id': [1001, 1002, 1003, 1004, 1005],
    'name': ['Alice Johnson', 'Bob Smith', 'Carol Brown', 'David Wilson', 'Eve Davis'],
    'age': [28, 34, 45, 29, 38],
    'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'signup_date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2023-05-12'],
    'total_spent': [1250.50, 890.25, 2100.75, 567.00, 1450.30],
    'is_premium': [True, False, True, False, True]
}

# 2. Product inventory dataset
inventory_data = {
    'product_code': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'],
    'product_name': ['Gaming Laptop', 'Wireless Mouse', '4K Monitor', 'Mechanical Keyboard', 'USB-C Hub'],
    'category': ['Electronics', 'Accessories', 'Electronics', 'Accessories', 'Accessories'],
    'price': [1299.99, 29.99, 399.99, 149.99, 79.99],
    'stock_quantity': [15, 200, 45, 80, 120],
    'supplier': ['TechCorp', 'AccessoryPlus', 'ScreenMakers', 'KeyboardCo', 'ConnectTech'],
    'last_restock': ['2024-07-01', '2024-07-10', '2024-06-25', '2024-07-05', '2024-07-08']
}

# 3. Website analytics dataset
analytics_data = {
    'date': pd.date_range('2024-07-01', periods=10, freq='D'),
    'page_views': [1250, 1340, 1180, 1420, 1390, 1580, 1720, 1650, 1480, 1560],
    'unique_visitors': [890, 920, 850, 980, 950, 1100, 1200, 1150, 1020, 1080],
    'bounce_rate': [0.45, 0.42, 0.48, 0.40, 0.43, 0.38, 0.35, 0.37, 0.44, 0.41],
    'avg_session_duration': [145, 162, 138, 175, 168, 189, 201, 195, 156, 172],
    'conversion_rate': [0.035, 0.042, 0.031, 0.048, 0.045, 0.055, 0.061, 0.058, 0.039, 0.051]
}

# 4. Employee dataset
employees_data = {
    'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
    'name': ['John Anderson', 'Sarah Martinez', 'Michael Chen', 'Lisa Thompson', 'Robert Kim'],
    'department': ['Engineering', 'Marketing', 'Sales', 'HR', 'Engineering'],
    'salary': [95000, 72000, 68000, 75000, 102000],
    'hire_date': ['2022-03-15', '2023-01-20', '2021-08-10', '2022-11-05', '2020-06-01'],
    'performance_score': [4.2, 3.8, 4.5, 4.0, 4.7],
    'years_experience': [5, 3, 8, 6, 12]
}

# Create the datasets
os.makedirs('sample_datasets', exist_ok=True)

# Save as different formats
pd.DataFrame(customers_data).to_csv('sample_datasets/customers.csv', index=False)
pd.DataFrame(inventory_data).to_excel('sample_datasets/inventory.xlsx', index=False)
pd.DataFrame(analytics_data).to_json('sample_datasets/analytics.json', orient='records', date_format='iso')
pd.DataFrame(employees_data).to_csv('sample_datasets/employees.tsv', sep='\t', index=False)

print("📁 Sample datasets created in 'sample_datasets/' folder:")
print("  • customers.csv - Customer data with demographics and spending")
print("  • inventory.xlsx - Product inventory with stock and pricing")
print("  • analytics.json - Website analytics with metrics")
print("  • employees.tsv - Employee data with salaries and performance")
print()
print("🌍 Upload any of these files using the Universal Dataset mode to see how")
print("   the AI Data Analyst can automatically analyze ANY type of data!")
print()
print("📊 Example questions you could ask after uploading:")
print("  Customers: 'What is the average age of premium customers?'")
print("  Inventory: 'Which category has the highest total value?'")
print("  Analytics: 'Show me the trend of conversion rates over time'")
print("  Employees: 'What is the average salary by department?'")
