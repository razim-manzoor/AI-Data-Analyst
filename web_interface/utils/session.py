"""
Session state management utilities for Streamlit.

Provides centralized session state initialization and management.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List


class SessionManager:
    """Manages Streamlit session state with type safety and defaults."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize all session state variables with defaults."""
        defaults = {
            'messages': [],
            'query_history': [],
            'performance_history': [],
            'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'system_initialized': False,
            'ai_system_status': {
                'initialized': False,
                'error': None,
                'interface': None
            }
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def get_ai_status() -> Dict[str, Any]:
        """Get AI system status from session state."""
        if 'ai_system_status' not in st.session_state:
            st.session_state.ai_system_status = {
                'initialized': False,
                'error': None,
                'interface': None
            }
        return st.session_state.ai_system_status
    
    @staticmethod
    def update_ai_status(status: Dict[str, Any]) -> None:
        """Update AI system status in session state."""
        if 'ai_system_status' not in st.session_state:
            st.session_state.ai_system_status = {}
        
        st.session_state.ai_system_status.update(status)
    
    @staticmethod
    def add_message(role: str, content: str, **kwargs) -> None:
        """Add a message to the chat history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        st.session_state.messages.append(message)
    
    @staticmethod
    def add_query_to_history(question: str, response: str, 
                           processing_time: float, success: bool) -> None:
        """Add a query to the query history."""
        query_record = {
            "question": question,
            "response": response,
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        
        st.session_state.query_history.append(query_record)
    
    @staticmethod
    def clear_chat() -> None:
        """Clear chat messages and query history."""
        st.session_state.messages = []
        st.session_state.query_history = []
    
    @staticmethod
    def get_session_stats() -> Dict[str, Any]:
        """Get session statistics."""
        messages = st.session_state.get('messages', [])
        queries = st.session_state.get('query_history', [])
        
        return {
            'session_id': st.session_state.get('session_id', 'unknown'),
            'message_count': len(messages),
            'query_count': len(queries),
            'system_initialized': st.session_state.get('system_initialized', False)
        }
