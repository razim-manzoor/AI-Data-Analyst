"""
Sidebar Component for Streamlit Interface

Handles the sidebar controls and system information display.
"""

import streamlit as st
import time
import os
import sys
from typing import Dict, Any, Callable

# Import utilities - handle both relative and absolute imports
try:
    from ..utils.session import SessionManager
    from ..config.ui_config import SUCCESS_MESSAGES, ERROR_MESSAGES
except ImportError:
    from utils.session import SessionManager
    from config.ui_config import SUCCESS_MESSAGES, ERROR_MESSAGES


class SidebarComponent:
    """Component for rendering the sidebar with controls and information."""
    
    def __init__(self, initialize_callback: Callable[[], bool]):
        """
        Initialize the sidebar component.
        
        Args:
            initialize_callback: Function to call for AI system initialization
        """
        self.initialize_callback = initialize_callback
    
    def render(self, venv_status: bool) -> None:
        """
        Render the complete sidebar.
        
        Args:
            venv_status: Virtual environment status
        """
        with st.sidebar:
            self._render_controls()
            st.markdown("---")
            self._render_system_info(venv_status)
            self._render_system_status()
            self._render_diagnostics_button()
    
    def _render_controls(self) -> None:
        """Render the main control buttons."""
        st.markdown("### 🎛️ System Controls")
        
        # Initialize/Reinitialize button
        if st.button("🔄 Initialize AI System", use_container_width=True):
            with st.spinner("Initializing AI system..."):
                success = self.initialize_callback()
                st.session_state.system_initialized = success
                
                if success:
                    st.success(SUCCESS_MESSAGES["system_initialized"])
                else:
                    st.error(ERROR_MESSAGES["initialization_failed"])
                
                time.sleep(1)
                st.rerun()
        
        # Clear chat button
        if st.button("🧹 Clear Chat", use_container_width=True):
            SessionManager.clear_chat()
            st.success(SUCCESS_MESSAGES["chat_cleared"])
            time.sleep(0.5)
            st.rerun()
    
    def _render_system_info(self, venv_status: bool) -> None:
        """Render system information section."""
        st.markdown("### 📋 System Information")
        
        session_stats = SessionManager.get_session_stats()
        
        st.info(f"**Session ID:** {session_stats['session_id']}")
        st.info(f"**Messages:** {session_stats['message_count']}")
        st.info(f"**Queries:** {session_stats['query_count']}")
        
        # Environment Information
        st.markdown("### 🔧 Environment")
        st.info(f"**Python:** {os.path.basename(sys.executable)}")
        st.info(f"**Virtual Env:** {'✅ Active' if venv_status else '❌ Not Active'}")
        st.info(f"**Working Dir:** {os.getcwd()}")
    
    def _render_system_status(self) -> None:
        """Render current system status."""
        st.markdown("### 📊 System Status")
        
        ai_status = SessionManager.get_ai_status()
        
        if ai_status['initialized']:
            st.success("AI System: ✅ Ready")
        else:
            st.error("AI System: ❌ Not Ready")
            if ai_status['error']:
                st.error(f"Error: {ai_status['error']}")
    
    def _render_diagnostics_button(self) -> None:
        """Render the system diagnostics button."""
        if st.button("🔍 System Diagnostics", use_container_width=True):
            # This will be handled by the main app to show diagnostics
            st.session_state.show_diagnostics = True
            st.rerun()
