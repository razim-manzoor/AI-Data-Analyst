"""
Database Connection Manager for optimized database operations.

This module provides a centralized database connection manager that:
- Implements connection pooling for better performance
- Provides automatic connection health checks
- Handles connection lifecycle management
- Reduces database connection overhead
"""

import logging
import os
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool
from typing import Generator, Optional, Any, Dict, List
from config import DB_FILE


class DatabaseManager:
    """
    Singleton database manager with connection pooling and health checks.
    """
    
    _instance: Optional['DatabaseManager'] = None
    _engine = None
    
    def __new__(cls) -> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the database engine with optimized settings."""
        try:
            # Create engine with connection pooling for SQLite
            self._engine = create_engine(
                f"sqlite:///{DB_FILE}",
                poolclass=StaticPool,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
                connect_args={
                    "check_same_thread": False,  # Allow multi-threading
                    "timeout": 30,  # 30 second timeout
                },
                echo=False  # Set to True for SQL debugging
            )
            logging.info("Database manager initialized with connection pooling")
        except Exception as e:
            logging.error(f"Failed to initialize database manager: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database connection.
        
        Returns:
            Dict: Health check results with status and details
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT 1"))
                return {
                    "status": "healthy",
                    "message": "Database connection successful",
                    "tables_accessible": True
                }
        except Exception as e:
            logging.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy", 
                "message": f"Database connection failed: {str(e)}",
                "tables_accessible": False
            }
    
    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """
        Get a database connection with automatic cleanup.
        
        Yields:
            Connection: SQLAlchemy connection object
        """
        if not os.path.exists(DB_FILE):
            raise FileNotFoundError(f"Database file not found: {DB_FILE}")
        
        connection = None
        try:
            connection = self._engine.connect()
            yield connection
        except SQLAlchemyError as e:
            logging.error(f"Database operation error: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get comprehensive database schema information.
        
        Returns:
            Dict containing schema information and metadata
        """
        try:
            with self.get_connection() as connection:
                # Get table names
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                tables = [row[0] for row in result]
                
                if not tables:
                    return {
                        "tables": [],
                        "schema_text": "No tables found in database",
                        "table_count": 0
                    }
                
                # Get detailed schema for each table
                schema_info = []
                table_details = {}
                
                for table in tables:
                    # Get column information
                    result = connection.execute(text(f"PRAGMA table_info({table});"))
                    columns = result.fetchall()
                    
                    # Get row count
                    count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table};"))
                    row_count = count_result.scalar()
                    
                    schema_info.append(f"Table: {table} ({row_count} rows)")
                    table_columns = []
                    
                    for col in columns:
                        col_info = f"  - {col[1]} ({col[2]})"
                        if col[5]:  # Primary key
                            col_info += " [PRIMARY KEY]"
                        if col[3]:  # Not null
                            col_info += " [NOT NULL]"
                        schema_info.append(col_info)
                        table_columns.append({
                            "name": col[1],
                            "type": col[2],
                            "nullable": not col[3],
                            "primary_key": bool(col[5])
                        })
                    
                    table_details[table] = {
                        "columns": table_columns,
                        "row_count": row_count
                    }
                
                return {
                    "tables": tables,
                    "schema_text": "\n".join(schema_info),
                    "table_count": len(tables),
                    "table_details": table_details
                }
                
        except Exception as e:
            logging.error(f"Error getting schema: {e}")
            return {
                "tables": [],
                "schema_text": f"Error retrieving schema: {e}",
                "table_count": 0,
                "error": str(e)
            }
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            
        Returns:
            List of dictionaries representing query results
        """
        try:
            with self.get_connection() as connection:
                result = connection.execute(text(query))
                data = [dict(row._mapping) for row in result]
                logging.info(f"Query executed successfully, returned {len(data)} rows")
                return data
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise
    
    def get_table_sample(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get a sample of data from a table for preview purposes.
        
        Args:
            table_name: Name of the table
            limit: Number of rows to return
            
        Returns:
            List of dictionaries representing sample data
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return self.execute_query(query)
        except Exception as e:
            logging.error(f"Error getting table sample: {e}")
            return []


# Global instance
db_manager = DatabaseManager()
