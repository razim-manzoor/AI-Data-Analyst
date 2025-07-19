"""
Agent Manager for optimized agent operations.

This module provides a centralized agent manager that:
- Implements agent instance caching to avoid repeated creation
- Provides lazy loading of agent instances
- Manages agent lifecycle efficiently
- Reduces agent initialization overhead
"""

import logging
from typing import Dict, Any, Optional
from functools import lru_cache
from agents import create_router_agent, create_sql_agent, create_chart_agent


class AgentManager:
    """
    Singleton agent manager with instance caching and lazy loading.
    """
    
    _instance: Optional['AgentManager'] = None
    _agents: Dict[str, Any] = {}
    
    def __new__(cls) -> 'AgentManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the agent manager."""
        self._agents = {}
        logging.info("Agent manager initialized")
    
    @lru_cache(maxsize=1)
    def get_router_agent(self) -> Any:
        """
        Get or create the router agent with caching.
        
        Returns:
            Router agent instance
        """
        if 'router' not in self._agents:
            logging.info("Creating new router agent instance")
            self._agents['router'] = create_router_agent()
        return self._agents['router']
    
    @lru_cache(maxsize=1)
    def get_sql_agent(self) -> Any:
        """
        Get or create the SQL agent with caching.
        
        Returns:
            SQL agent instance
        """
        if 'sql' not in self._agents:
            logging.info("Creating new SQL agent instance")
            self._agents['sql'] = create_sql_agent()
        return self._agents['sql']
    
    @lru_cache(maxsize=1)
    def get_chart_agent(self) -> Any:
        """
        Get or create the chart agent with caching.
        
        Returns:
            Chart agent instance
        """
        if 'chart' not in self._agents:
            logging.info("Creating new chart agent instance")
            self._agents['chart'] = create_chart_agent()
        return self._agents['chart']
    
    def route_question(self, question: str) -> str:
        """
        Route a question using the cached router agent.
        
        Args:
            question: User question to route
            
        Returns:
            Routing decision ('sql' or 'chart')
        """
        try:
            logging.info(f"Routing question: {question[:50]}...")
            router = self.get_router_agent()
            route = router.invoke({"question": question})
            route_clean = route.strip().lower()
            
            # Validate route
            valid_routes = ["sql", "chart"]
            if route_clean not in valid_routes:
                logging.warning(f"Invalid route '{route_clean}' received, defaulting to 'sql'")
                route_clean = "sql"
                
            logging.info(f"Question routed to: {route_clean}")
            return route_clean
            
        except Exception as e:
            logging.error(f"Error during question routing: {e}")
            return "sql"  # Default to SQL on error
    
    def generate_sql_query(self, question: str, schema: str) -> str:
        """
        Generate SQL query using the cached SQL agent.
        
        Args:
            question: User question
            schema: Database schema
            
        Returns:
            Generated SQL query
        """
        try:
            logging.info("Generating SQL query using SQL agent")
            sql_agent = self.get_sql_agent()
            query = sql_agent.invoke({
                "question": question,
                "schema": schema
            })
            
            if not query or not query.strip():
                raise ValueError("SQL agent returned empty query")
                
            logging.info(f"Generated SQL query: {query[:100]}...")
            return query.strip()
            
        except Exception as e:
            logging.error(f"Error generating SQL query: {e}")
            raise
    
    def generate_chart_code(self, question: str, data: str) -> str:
        """
        Generate chart code using the cached chart agent.
        
        Args:
            question: User question
            data: Data for visualization
            
        Returns:
            Generated Python chart code
        """
        try:
            logging.info("Generating chart code using chart agent")
            chart_agent = self.get_chart_agent()
            chart_code = chart_agent.invoke({
                "question": question,
                "data": data
            })
            
            if not chart_code or not chart_code.strip():
                raise ValueError("Chart agent returned empty code")
                
            logging.info("Chart code generated successfully")
            return chart_code.strip()
            
        except Exception as e:
            logging.error(f"Error generating chart code: {e}")
            raise
    
    def clear_cache(self) -> None:
        """
        Clear all cached agents (useful for testing or memory management).
        """
        logging.info("Clearing agent cache")
        self._agents.clear()
        # Clear LRU cache
        self.get_router_agent.cache_clear()
        self.get_sql_agent.cache_clear()
        self.get_chart_agent.cache_clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached agents.
        
        Returns:
            Dictionary with cache information
        """
        return {
            "cached_agents": list(self._agents.keys()),
            "router_cache_info": self.get_router_agent.cache_info(),
            "sql_cache_info": self.get_sql_agent.cache_info(),
            "chart_cache_info": self.get_chart_agent.cache_info()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the agent manager.
        
        Returns:
            Dictionary with health status information
        """
        try:
            # Check if we can create agents
            router = self.get_router_agent()
            sql_agent = self.get_sql_agent()
            chart_agent = self.get_chart_agent()
            
            return {
                "status": "healthy",
                "agents_loaded": len(self._agents),
                "available_agents": ["router", "sql", "chart"],
                "cache_info": self.get_cache_info()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "agents_loaded": len(self._agents)
            }
    
    # Alias methods for compatibility
    def get_router(self) -> Any:
        """Alias for get_router_agent()"""
        return self.get_router_agent()
    
    def get_sql(self) -> Any:
        """Alias for get_sql_agent()"""
        return self.get_sql_agent()
    
    def get_chart(self) -> Any:
        """Alias for get_chart_agent()"""
        return self.get_chart_agent()


# Global instance
agent_manager = AgentManager()
