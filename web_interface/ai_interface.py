"""
🔗 Interface Module for Streamlit Integration

This module provides a clean interface between Streamlit and the AI Data Analyst system.
"""

import time
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIDataAnalystInterface:
    """Interface class for the AI Data Analyst system"""
    
    def __init__(self):
        """Initialize the interface"""
        self.workflow_app = None
        self.db_manager = None
        self.agent_manager = None
        self.config = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            # Ensure we're working from the correct directory
            current_dir = Path(__file__).parent.absolute()
            project_root = current_dir.parent
            src_dir = project_root / "src"
            
            # Set working directory to project root
            os.chdir(project_root)
            
            # Add src directory to path for imports
            if str(src_dir) not in sys.path:
                sys.path.insert(0, str(src_dir))
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # Import required modules
            from config import LOG_FILE, DB_FILE, MODEL
            from database_manager import db_manager
            from agent_manager import agent_manager
            from state import create_initial_state
            
            # Import workflow components
            from main import get_schema, route_question, run_sql_query, generate_chart
            from langgraph.graph import StateGraph, END
            from state import AgentState
            
            # Initialize configuration
            logger.info("Configuration loaded successfully")
            
            # Initialize database manager
            self.db_manager = db_manager
            db_health = self.db_manager.health_check()
            if db_health.get('status') != 'healthy':
                raise Exception(f"Database health check failed: {db_health}")
            logger.info("Database manager initialized successfully")
            
            # Initialize agent manager
            self.agent_manager = agent_manager
            logger.info("Agent manager initialized successfully")
            
            # Create the workflow
            workflow = StateGraph(AgentState)
            workflow.add_node("get_schema", get_schema)
            workflow.add_node("route_question", route_question)
            workflow.add_node("run_sql_query", run_sql_query)
            workflow.add_node("generate_chart", generate_chart)
            
            workflow.set_entry_point("get_schema")
            workflow.add_edge("get_schema", "route_question")
            workflow.add_conditional_edges(
                "route_question",
                lambda x: x["route"],
                {
                    "sql": "run_sql_query",
                    "chart": "generate_chart",
                },
            )
            workflow.add_edge("run_sql_query", END)
            workflow.add_edge("generate_chart", END)
            
            # Compile the workflow
            self.workflow_app = workflow.compile()
            logger.info("Workflow compiled successfully")
            
            # Store the create_initial_state function for later use
            self.create_initial_state = create_initial_state
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI system: {e}")
            self._initialized = False
            return False
    
    def is_ready(self) -> bool:
        """Check if the system is ready to process requests"""
        return self._initialized and self.workflow_app is not None
    
    def get_response(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a response from the AI system for the given question
        
        Args:
            question: The user's question
            session_id: Optional session identifier
            
        Returns:
            Dictionary containing the response and metadata
        """
        if not self.is_ready():
            return {
                "final_answer": "❌ AI system is not properly initialized. Please check the system health.",
                "error": "System not initialized",
                "performance_tracking": {"total_time": 0}
            }
        
        start_time = time.time()
        
        try:
            logger.info(f"Processing question: {question}")
            
            # Create initial state
            initial_state = self.create_initial_state(question)
            if session_id:
                initial_state["session_id"] = session_id
            
            # Run the workflow
            result = self.workflow_app.invoke(initial_state)
            
            processing_time = time.time() - start_time
            logger.info(f"Question processed in {processing_time:.2f}s")
            
            # Format the response
            final_answer = self._format_response(result)
            
            return {
                "final_answer": final_answer,
                "sql_query": result.get("sql_query"),
                "query_result": result.get("data"),
                "chart_path": self._get_chart_path(result),
                "performance_tracking": {
                    "total_time": processing_time,
                    "step_times": result.get("step_times", {}),
                    "components_used": self._get_components_used(result)
                },
                "raw_result": result
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error processing question: {str(e)}"
            logger.error(error_msg)
            
            return {
                "final_answer": f"❌ {error_msg}",
                "error": str(e),
                "performance_tracking": {"total_time": processing_time}
            }
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """Format the workflow result into a user-friendly response"""
        try:
            # Check for errors first
            if result.get("errors"):
                error_parts = []
                for error_type, error_msg in result["errors"].items():
                    error_parts.append(f"**{error_type}**: {error_msg}")
                
                if error_parts:
                    return f"⚠️ **Issues encountered:**\n" + "\n".join(error_parts)
            
            # Format successful responses
            response_parts = []
            
            # Add SQL query if available
            if result.get("sql_query") and not str(result["sql_query"]).startswith("Error:"):
                response_parts.append(f"**SQL Query:**\n```sql\n{result['sql_query']}\n```")
            
            # Add data results
            if result.get("data") and not str(result["data"]).startswith("Error:"):
                data = result["data"]
                if isinstance(data, list) and len(data) > 0:
                    response_parts.append(f"**Results:** Found {len(data)} records")
                    
                    # Show sample data
                    if len(data) <= 10:
                        response_parts.append("**Data:**")
                        for i, row in enumerate(data, 1):
                            response_parts.append(f"{i}. {row}")
                    else:
                        response_parts.append("**Sample Data (first 5 rows):**")
                        for i, row in enumerate(data[:5], 1):
                            response_parts.append(f"{i}. {row}")
                        response_parts.append(f"... and {len(data) - 5} more rows")
                else:
                    response_parts.append("**Results:** No data found")
            
            # Add chart information
            if result.get("chart_code") and not str(result["chart_code"]).startswith("# ERROR:"):
                response_parts.append("**Chart:** Visualization has been generated successfully!")
            
            # Performance information
            if result.get("step_times"):
                total_time = sum(result["step_times"].values())
                response_parts.append(f"**Processing time:** {total_time:.2f} seconds")
            
            return "\n\n".join(response_parts) if response_parts else "✅ Request processed successfully!"
            
        except Exception as e:
            return f"❌ Error formatting response: {str(e)}"
    
    def _get_chart_path(self, result: Dict[str, Any]) -> Optional[str]:
        """Extract chart path from result if available"""
        # Check if chart was generated
        if result.get("chart_code") and not str(result["chart_code"]).startswith("# ERROR:"):
            # Look for common chart file patterns
            data_dir = Path("data")
            for pattern in ["*.png", "*.jpg", "*.jpeg"]:
                chart_files = list(data_dir.glob(pattern))
                if chart_files:
                    # Return the most recent chart file
                    latest_chart = max(chart_files, key=lambda f: f.stat().st_mtime)
                    return str(latest_chart)
        return None
    
    def _get_components_used(self, result: Dict[str, Any]) -> str:
        """Determine which components were used in processing"""
        components = []
        
        if result.get("schema"):
            components.append("Schema")
        if result.get("sql_query"):
            components.append("SQL")
        if result.get("data"):
            components.append("Data")
        if result.get("chart_code"):
            components.append("Chart")
            
        return " → ".join(components) if components else "None"
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information"""
        if not self._initialized:
            return {
                "status": "error",
                "error": "System not initialized",
                "ai_system": False,
                "database": {"status": "unavailable"}
            }
        
        try:
            health = {
                "status": "healthy",
                "ai_system": True,
                "database": self.db_manager.health_check() if self.db_manager else {"status": "unavailable"}
            }
            
            if self.agent_manager:
                health["agents"] = self.agent_manager.get_cache_stats()
            
            return health
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "ai_system": False
            }
    
    def get_database_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        if not self.db_manager:
            return {"error": "Database manager not initialized"}
        
        try:
            return self.db_manager.get_schema()
        except Exception as e:
            return {"error": str(e)}

# Create a global instance
_interface = AIDataAnalystInterface()

# Export convenience functions
def initialize_system() -> bool:
    """Initialize the AI system"""
    return _interface.initialize()

def get_response(question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Get a response from the AI system"""
    return _interface.get_response(question, session_id)

def get_system_health() -> Dict[str, Any]:
    """Get system health information"""
    return _interface.get_system_health()

def get_session_statistics() -> Dict[str, Any]:
    """Get session statistics (placeholder)"""
    return {
        "session_active": _interface.is_ready(),
        "system_ready": _interface.is_ready()
    }

def get_database_schema() -> Dict[str, Any]:
    """Get database schema"""
    return _interface.get_database_schema()

# Auto-initialize when imported
def auto_initialize():
    """Automatically initialize the system when this module is imported"""
    try:
        return _interface.initialize()
    except Exception as e:
        logger.warning(f"Auto-initialization failed: {e}")
        return False

# Initialize the system
system_ready = auto_initialize()
