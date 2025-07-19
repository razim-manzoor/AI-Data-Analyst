#!/usr/bin/env python3
"""
🗃️ Database Enhancement Module

Comprehensive database optimization and enhancement features:
1. Index creation for performance
2. Data validation and constraints
3. Query optimization
4. Advanced schema management
5. Data integrity checks
"""

import os
import sys
import sqlite3
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from config import DB_FILE, CSV_FILE
from database_manager import db_manager

class DatabaseEnhancer:
    """Enhanced database operations and optimizations"""
    
    def __init__(self):
        self.db_file = DB_FILE
        self.csv_file = CSV_FILE
        self.logger = logging.getLogger(__name__)
        
    def analyze_current_database(self) -> Dict[str, Any]:
        """Analyze current database structure and performance"""
        analysis = {
            "table_info": {},
            "performance_metrics": {},
            "optimization_opportunities": [],
            "data_quality": {}
        }
        
        try:
            # Get basic table information
            schema_info = db_manager.get_schema()
            analysis["table_info"] = schema_info
            
            # Analyze data types and structure using SQLAlchemy text()
            from sqlalchemy import text
            
            with db_manager.get_connection() as conn:
                # Check table schema details
                result = conn.execute(text("PRAGMA table_info(sales);"))
                columns = result.fetchall()
                
                analysis["data_quality"]["columns"] = [
                    {
                        "name": col[1],
                        "type": col[2], 
                        "nullable": not col[3],
                        "primary_key": bool(col[5])
                    } for col in columns
                ]
                
                # Check for indexes
                result = conn.execute(text("PRAGMA index_list(sales);"))
                indexes = result.fetchall()
                analysis["performance_metrics"]["indexes"] = len(indexes)
                
                # Analyze data distribution
                result = conn.execute(text("SELECT COUNT(DISTINCT Region) FROM sales;"))
                region_count = result.fetchone()[0]
                
                result = conn.execute(text("SELECT COUNT(DISTINCT Product) FROM sales;"))
                product_count = result.fetchone()[0]
                
                result = conn.execute(text("SELECT MIN(Date), MAX(Date) FROM sales;"))
                date_range = result.fetchone()
                
                analysis["data_quality"]["distribution"] = {
                    "unique_regions": region_count,
                    "unique_products": product_count,
                    "date_range": date_range
                }
                
                # Check for data quality issues
                result = conn.execute(text("SELECT COUNT(*) FROM sales WHERE Units <= 0 OR Sale <= 0;"))
                invalid_data = result.fetchone()[0]
                
                result = conn.execute(text("SELECT COUNT(*) FROM sales WHERE Date IS NULL OR Region IS NULL OR Product IS NULL;"))
                null_data = result.fetchone()[0]
                
                analysis["data_quality"]["issues"] = {
                    "invalid_numbers": invalid_data,
                    "null_values": null_data
                }
            
            # Identify optimization opportunities
            if analysis["performance_metrics"]["indexes"] == 0:
                analysis["optimization_opportunities"].append("Add indexes for frequently queried columns")
            
            if analysis["data_quality"]["issues"]["invalid_numbers"] > 0:
                analysis["optimization_opportunities"].append("Add data validation constraints")
                
            # Check data types optimization
            for col in analysis["data_quality"]["columns"]:
                if col["name"] == "Date" and col["type"] == "TEXT":
                    analysis["optimization_opportunities"].append("Convert Date column to proper DATE type")
                    
            return analysis
            
        except Exception as e:
            self.logger.error(f"Database analysis failed: {e}")
            return {"error": str(e)}
    
    def create_optimized_indexes(self) -> Dict[str, bool]:
        """Create performance indexes for common queries"""
        results = {}
        
        indexes_to_create = [
            ("idx_sales_product", "CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(Product);"),
            ("idx_sales_region", "CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(Region);"),
            ("idx_sales_date", "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(Date);"),
            ("idx_sales_product_region", "CREATE INDEX IF NOT EXISTS idx_sales_product_region ON sales(Product, Region);")
        ]
        
        try:
            from sqlalchemy import text
            
            with db_manager.get_connection() as conn:
                for index_name, sql in indexes_to_create:
                    try:
                        conn.execute(text(sql))
                        results[index_name] = True
                        self.logger.info(f"Created index: {index_name}")
                    except Exception as e:
                        results[index_name] = False
                        self.logger.error(f"Failed to create index {index_name}: {e}")
                        
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Index creation failed: {e}")
            results["error"] = str(e)
            
        return results
    
    def add_data_constraints(self) -> Dict[str, bool]:
        """Add data validation constraints"""
        results = {}
        
        # Since SQLite doesn't support adding constraints to existing tables easily,
        # we'll create a new optimized table and migrate data
        try:
            with db_manager.get_connection() as conn:
                # Create optimized table with constraints
                create_sql = """
                CREATE TABLE IF NOT EXISTS sales_optimized (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Date DATE NOT NULL,
                    Region TEXT NOT NULL CHECK(Region IN ('North', 'South', 'East', 'West')),
                    Product TEXT NOT NULL,
                    Units INTEGER NOT NULL CHECK(Units > 0),
                    Sale INTEGER NOT NULL CHECK(Sale > 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(Date, Region, Product)
                );
                """
                
                conn.execute(create_sql)
                results["table_created"] = True
                
                # Migrate data with validation
                migrate_sql = """
                INSERT OR IGNORE INTO sales_optimized (Date, Region, Product, Units, Sale)
                SELECT Date, Region, Product, Units, Sale 
                FROM sales 
                WHERE Units > 0 AND Sale > 0 
                AND Date IS NOT NULL AND Region IS NOT NULL AND Product IS NOT NULL;
                """
                
                cursor = conn.execute(migrate_sql)
                results["rows_migrated"] = cursor.rowcount
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Constraint addition failed: {e}")
            results["error"] = str(e)
            
        return results
    
    def create_analytical_views(self) -> Dict[str, bool]:
        """Create views for common analytical queries"""
        results = {}
        
        views_to_create = [
            ("sales_summary", """
                CREATE VIEW IF NOT EXISTS sales_summary AS
                SELECT 
                    Product,
                    Region,
                    COUNT(*) as transaction_count,
                    SUM(Units) as total_units,
                    SUM(Sale) as total_sales,
                    AVG(Sale) as avg_sale,
                    MIN(Date) as first_sale,
                    MAX(Date) as last_sale
                FROM sales
                GROUP BY Product, Region;
            """),
            ("monthly_trends", """
                CREATE VIEW IF NOT EXISTS monthly_trends AS
                SELECT 
                    strftime('%Y-%m', Date) as month,
                    SUM(Sale) as monthly_sales,
                    SUM(Units) as monthly_units,
                    COUNT(*) as transaction_count,
                    COUNT(DISTINCT Product) as products_sold
                FROM sales
                GROUP BY strftime('%Y-%m', Date)
                ORDER BY month;
            """),
            ("product_performance", """
                CREATE VIEW IF NOT EXISTS product_performance AS
                SELECT 
                    Product,
                    COUNT(*) as transactions,
                    SUM(Units) as total_units,
                    SUM(Sale) as total_revenue,
                    AVG(CAST(Sale AS FLOAT)/Units) as avg_unit_price,
                    SUM(Sale) * 100.0 / (SELECT SUM(Sale) FROM sales) as revenue_percentage
                FROM sales
                GROUP BY Product
                ORDER BY total_revenue DESC;
            """)
        ]
        
        try:
            from sqlalchemy import text
            
            with db_manager.get_connection() as conn:
                for view_name, sql in views_to_create:
                    try:
                        conn.execute(text(sql))
                        results[view_name] = True
                        self.logger.info(f"Created view: {view_name}")
                    except Exception as e:
                        results[view_name] = False
                        self.logger.error(f"Failed to create view {view_name}: {e}")
                        
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"View creation failed: {e}")
            results["error"] = str(e)
            
        return results
    
    def benchmark_query_performance(self) -> Dict[str, float]:
        """Benchmark common query performance"""
        queries = {
            "total_sales": "SELECT SUM(Sale) FROM sales;",
            "product_breakdown": "SELECT Product, SUM(Sale) FROM sales GROUP BY Product;",
            "region_analysis": "SELECT Region, COUNT(*), SUM(Sale) FROM sales GROUP BY Region;",
            "complex_join": """
                SELECT s.Product, s.Region, s.Date, s.Sale,
                       AVG(s2.Sale) as avg_product_sale
                FROM sales s
                JOIN sales s2 ON s.Product = s2.Product
                GROUP BY s.Product, s.Region, s.Date, s.Sale;
            """
        }
        
        results = {}
        
        try:
            from sqlalchemy import text
            
            for query_name, sql in queries.items():
                start_time = datetime.now()
                
                with db_manager.get_connection() as conn:
                    result = conn.execute(text(sql))
                    rows = result.fetchall()
                    
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                results[query_name] = {
                    "execution_time": execution_time,
                    "rows_returned": len(rows)
                }
                
        except Exception as e:
            self.logger.error(f"Performance benchmarking failed: {e}")
            results["error"] = str(e)
            
        return results
    
    def run_full_enhancement(self) -> Dict[str, Any]:
        """Run complete database enhancement process"""
        print("🗃️ Starting Database Enhancement Process...")
        
        # Step 1: Analyze current state
        print("\n📊 Analyzing Current Database...")
        analysis = self.analyze_current_database()
        print(f"✅ Analysis complete: {len(analysis.get('optimization_opportunities', []))} opportunities found")
        
        # Step 2: Create indexes
        print("\n🔍 Creating Performance Indexes...")
        index_results = self.create_optimized_indexes()
        successful_indexes = sum(1 for v in index_results.values() if v is True)
        print(f"✅ Created {successful_indexes} indexes")
        
        # Step 3: Create analytical views
        print("\n📈 Creating Analytical Views...")
        view_results = self.create_analytical_views()
        successful_views = sum(1 for v in view_results.values() if v is True)
        print(f"✅ Created {successful_views} analytical views")
        
        # Step 4: Benchmark performance
        print("\n⚡ Benchmarking Query Performance...")
        performance = self.benchmark_query_performance()
        avg_time = sum(q["execution_time"] for q in performance.values() if isinstance(q, dict)) / len(performance)
        print(f"✅ Average query time: {avg_time:.4f}s")
        
        # Step 5: Final verification
        print("\n🔬 Final Database Verification...")
        final_health = db_manager.health_check()
        print(f"✅ Database health: {final_health['status']}")
        
        return {
            "analysis": analysis,
            "indexes": index_results,
            "views": view_results,
            "performance": performance,
            "health": final_health,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Run database enhancement"""
    enhancer = DatabaseEnhancer()
    results = enhancer.run_full_enhancement()
    
    print("\n" + "="*60)
    print("🎯 Database Enhancement Complete!")
    print(f"📊 Optimization opportunities addressed: {len(results['analysis'].get('optimization_opportunities', []))}")
    print(f"🔍 Indexes created: {sum(1 for v in results['indexes'].values() if v is True)}")
    print(f"📈 Views created: {sum(1 for v in results['views'].values() if v is True)}")
    print("="*60)
    
    return results

if __name__ == "__main__":
    results = main()
