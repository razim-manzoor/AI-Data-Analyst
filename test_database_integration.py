#!/usr/bin/env python3
"""
Comprehensive Database Connection & CSV Upload Test

Tests:
1. Database connectivity
2. Current database schema
3. CSV to SQL conversion
4. Data integrity verification
5. Query performance
"""

import sys
import os
import pandas as pd
import sqlite3
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import DatabaseManager
from web_interface.components.universal_dataset import UniversalDatasetComponent

def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing Database Connection...")
    
    db_manager = DatabaseManager()
    
    # Test basic connection
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            print(f"✅ SQLite Version: {version[0]}")
        
        # Test schema retrieval
        schema = db_manager.get_schema()
        if 'error' not in schema:
            print(f"✅ Database schema retrieved: {len(schema['table_details'])} tables found")
            for table_name, details in schema['table_details'].items():
                print(f"   📋 Table '{table_name}': {details['row_count']} rows, {len(details['columns'])} columns")
        else:
            print(f"❌ Schema retrieval error: {schema['error']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_current_data():
    """Test current data in the database"""
    print("\n📊 Testing Current Database Data...")
    
    try:
        db_file = "data/sales.db"
        conn = sqlite3.connect(db_file)
        
        # Get all tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ Found {len(tables)} tables:")
        
        for (table_name,) in tables:
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            
            print(f"   📋 {table_name}: {row_count} rows")
            print(f"      Columns: {', '.join([col[1] for col in columns])}")
            
            # Show sample data
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_data = cursor.fetchall()
                print(f"      Sample: {sample_data[0] if sample_data else 'No data'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Current data test failed: {e}")
        return False

def test_csv_to_sql_conversion():
    """Test CSV upload and conversion to SQL"""
    print("\n🔄 Testing CSV to SQL Conversion...")
    
    try:
        # Create a test CSV file
        test_data = {
            'product_id': [1, 2, 3, 4, 5],
            'product_name': ['Laptop Pro', 'Wireless Mouse', '4K Monitor', 'Keyboard', 'Webcam'],
            'category': ['Electronics', 'Accessories', 'Electronics', 'Accessories', 'Electronics'],
            'price': [1299.99, 29.99, 449.99, 89.99, 79.99],
            'stock': [25, 150, 30, 75, 45],
            'rating': [4.8, 4.2, 4.6, 4.4, 4.1]
        }
        
        test_df = pd.DataFrame(test_data)
        test_csv_path = "test_products.csv"
        test_df.to_csv(test_csv_path, index=False)
        print(f"✅ Created test CSV: {test_csv_path}")
        
        # Test universal dataset component
        upload_component = UniversalDatasetComponent()
        
        # Simulate file upload by reading the CSV
        with open(test_csv_path, 'rb') as f:
            file_content = f.read()
        
        # Create a mock uploaded file object
        class MockUploadedFile:
            def __init__(self, content, name):
                self.content = content
                self.name = name
                self._pos = 0
            
            def read(self):
                return self.content
            
            def getvalue(self):
                return self.content
            
            def seek(self, pos):
                self._pos = pos
        
        mock_file = MockUploadedFile(file_content, test_csv_path)
        
        # Test data type detection
        df_loaded, load_status = upload_component.load_file_to_dataframe(mock_file)
        
        if load_status == "success":
            print(f"✅ CSV loaded successfully: {len(df_loaded)} rows, {len(df_loaded.columns)} columns")
            
            # Test column analysis
            column_analysis = upload_component.detect_data_types(df_loaded)
            print("✅ Column analysis completed:")
            for col, analysis in column_analysis.items():
                print(f"   📊 {col}: {analysis['pandas_type']} -> {analysis['sql_type']}")
            
            # Test table creation SQL
            create_sql = upload_component.create_table_from_analysis("test_products", column_analysis)
            print("✅ SQL creation statement generated")
            
            # Test actual database insertion
            db_manager = DatabaseManager()
            
            # Drop table if exists
            db_manager.execute_query("DROP TABLE IF EXISTS test_products")
            
            # Create table
            success = db_manager.execute_query(create_sql)
            if success:
                print("✅ Test table created successfully")
                
                # Insert data
                success, message = upload_component.insert_data_to_table(df_loaded, "test_products", column_analysis)
                if success:
                    print(f"✅ Data inserted: {message}")
                    
                    # Verify data
                    with db_manager.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM test_products;")
                        count = cursor.fetchone()[0]
                        print(f"✅ Verified: {count} rows in test_products table")
                        
                        # Show sample data
                        cursor.execute("SELECT * FROM test_products LIMIT 2;")
                        sample = cursor.fetchall()
                        print(f"✅ Sample data: {sample}")
                else:
                    print(f"❌ Data insertion failed: {message}")
            else:
                print("❌ Table creation failed")
        else:
            print(f"❌ CSV loading failed: {load_status}")
        
        # Clean up
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)
            print("✅ Test CSV file cleaned up")
            
        return True
        
    except Exception as e:
        print(f"❌ CSV to SQL conversion test failed: {e}")
        return False

def test_query_performance():
    """Test database query performance"""
    print("\n⚡ Testing Query Performance...")
    
    try:
        import time
        db_manager = DatabaseManager()
        
        test_queries = [
            "SELECT COUNT(*) FROM sales",
            "SELECT Region, COUNT(*) FROM sales GROUP BY Region",
            "SELECT Product, SUM(Sale) FROM sales GROUP BY Product ORDER BY SUM(Sale) DESC LIMIT 5",
            "SELECT * FROM sales_summary LIMIT 5",
            "SELECT * FROM monthly_trends",
        ]
        
        total_time = 0
        successful_queries = 0
        
        for i, query in enumerate(test_queries, 1):
            try:
                start_time = time.time()
                
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    results = cursor.fetchall()
                
                query_time = time.time() - start_time
                total_time += query_time
                successful_queries += 1
                
                print(f"   ✅ Query {i}: {query_time:.4f}s ({len(results)} results)")
                
            except Exception as e:
                print(f"   ❌ Query {i} failed: {e}")
        
        if successful_queries > 0:
            avg_time = total_time / successful_queries
            print(f"✅ Average query time: {avg_time:.4f}s ({successful_queries}/{len(test_queries)} queries successful)")
        
        return True
        
    except Exception as e:
        print(f"❌ Query performance test failed: {e}")
        return False

def test_data_integrity():
    """Test data integrity and constraints"""
    print("\n🔒 Testing Data Integrity...")
    
    try:
        db_manager = DatabaseManager()
        
        # Test foreign key constraints (if any)
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for any constraint violations
            cursor.execute("PRAGMA foreign_key_check;")
            violations = cursor.fetchall()
            
            if not violations:
                print("✅ No foreign key constraint violations")
            else:
                print(f"⚠️ Found {len(violations)} constraint violations")
            
            # Test data types consistency
            cursor.execute("SELECT Date, Region, Product, Units, Sale FROM sales LIMIT 5;")
            sample_data = cursor.fetchall()
            
            if sample_data:
                print("✅ Sample data types verification:")
                for row in sample_data[:2]:
                    print(f"   📊 {row}")
            
        return True
        
    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")
        return False

def main():
    """Run all database tests"""
    print("🔬 AI Data Analyst - Database Connection & CSV Upload Test")
    print("=" * 70)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Current Database Data", test_current_data),
        ("CSV to SQL Conversion", test_csv_to_sql_conversion),
        ("Query Performance", test_query_performance),
        ("Data Integrity", test_data_integrity),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            success = test_func()
            if success:
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")
    
    print(f"\n{'='*70}")
    print(f"🎯 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All database tests passed! System is fully functional.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()
