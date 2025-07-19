#!/usr/bin/env python3
"""
Simple Database Test - Direct SQLite Operations
Tests database connectivity and CSV-to-SQL without complex imports
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

def test_basic_database():
    """Test basic database operations"""
    print("🔍 Testing Basic Database Connection...")
    
    db_path = "data/sales.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test connection
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"✅ SQLite Version: {version[0]}")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ Found {len(tables)} tables:")
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"   📋 {table_name}: {row_count} rows, {len(columns)} columns")
            print(f"      Columns: {', '.join([col[1] for col in columns])}")
            
            # Show sample data
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2;")
                sample_data = cursor.fetchall()
                print(f"      Sample: {sample_data[0] if sample_data else 'No data'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_csv_upload():
    """Test CSV upload and conversion to SQL"""
    print("\n🔄 Testing CSV Upload & SQL Conversion...")
    
    try:
        # Create test CSV
        test_data = {
            'id': [1, 2, 3, 4, 5],
            'product': ['Laptop', 'Mouse', 'Monitor', 'Keyboard', 'Webcam'],
            'price': [1299.99, 29.99, 449.99, 89.99, 79.99],
            'category': ['Electronics', 'Accessories', 'Electronics', 'Accessories', 'Electronics']
        }
        
        df = pd.DataFrame(test_data)
        csv_file = "test_upload.csv"
        df.to_csv(csv_file, index=False)
        print(f"✅ Created test CSV: {csv_file}")
        
        # Read CSV back
        df_loaded = pd.read_csv(csv_file)
        print(f"✅ Loaded CSV: {len(df_loaded)} rows, {len(df_loaded.columns)} columns")
        print(f"   Columns: {list(df_loaded.columns)}")
        print(f"   Data types: {dict(df_loaded.dtypes)}")
        
        # Create SQL table
        db_path = "data/sales.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop existing test table
        cursor.execute("DROP TABLE IF EXISTS test_upload")
        
        # Create table with proper types
        create_sql = """
        CREATE TABLE test_upload (
            id INTEGER,
            product TEXT,
            price REAL,
            category TEXT
        )
        """
        
        cursor.execute(create_sql)
        print("✅ Created test_upload table")
        
        # Insert data
        df_loaded.to_sql('test_upload', conn, if_exists='replace', index=False)
        print("✅ Inserted CSV data into SQL table")
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM test_upload")
        count = cursor.fetchone()[0]
        print(f"✅ Verified: {count} rows in test_upload table")
        
        # Show sample data
        cursor.execute("SELECT * FROM test_upload LIMIT 3")
        sample = cursor.fetchall()
        print("✅ Sample data from SQL table:")
        for row in sample:
            print(f"   📊 {row}")
        
        # Test queries
        cursor.execute("SELECT category, COUNT(*), AVG(price) FROM test_upload GROUP BY category")
        analysis = cursor.fetchall()
        print("✅ Analysis query:")
        for row in analysis:
            print(f"   📈 {row[0]}: {row[1]} items, avg price ${row[2]:.2f}")
        
        conn.close()
        
        # Clean up
        os.remove(csv_file)
        print("✅ Test CSV cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV upload test failed: {e}")
        return False

def test_existing_data():
    """Test operations on existing sales data"""
    print("\n📊 Testing Existing Sales Data Operations...")
    
    try:
        db_path = "data/sales.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test complex queries
        test_queries = [
            ("Total Sales", "SELECT SUM(Sale) FROM sales"),
            ("Top Regions", "SELECT Region, SUM(Sale) FROM sales GROUP BY Region ORDER BY SUM(Sale) DESC LIMIT 3"),
            ("Product Count", "SELECT COUNT(DISTINCT Product) FROM sales"),
            ("Average Sale", "SELECT AVG(Sale) FROM sales"),
            ("Date Range", "SELECT MIN(Date), MAX(Date) FROM sales")
        ]
        
        for query_name, sql in test_queries:
            cursor.execute(sql)
            result = cursor.fetchone()
            print(f"   ✅ {query_name}: {result}")
        
        # Test joins if multiple tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        if len(tables) > 1:
            print(f"✅ Multiple tables available for joins: {tables}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Existing data test failed: {e}")
        return False

def main():
    """Run all database tests"""
    print("🔬 AI Data Analyst - Simple Database Integration Test")
    print("=" * 60)
    
    tests = [
        ("Basic Database Connection", test_basic_database),
        ("CSV Upload & SQL Conversion", test_csv_upload),
        ("Existing Data Operations", test_existing_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            if success:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
    
    print(f"\n{'='*60}")
    print(f"🎯 Database Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database connectivity tests passed!")
        print("✅ CSV upload to SQL database conversion works correctly")
        print("✅ Database queries and operations are functional")
    else:
        print("⚠️ Some database tests failed")
    
    return passed == total

if __name__ == "__main__":
    main()
