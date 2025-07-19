"""
Header Component for Streamlit Interface

Handles the main header display with system status indicators.
"""

import streamlit as st
from typing import Dict, Any

# Import styling - handle both relative and absolute imports
try:
    from ..utils.styling import get_status_css_class
except ImportError:
    from utils.styling import get_status_css_class


class HeaderComponent:
    """Component for rendering the application header with status indicators."""
    
    def __init__(self):
        """Initialize the header component."""
        self.title = "🤖 AI Data Analyst"
    
    def render(self, ai_status: Dict[str, Any], venv_status: bool) -> None:
        """
        Render the header with system status.
        
        Args:
            ai_status: Current AI system status
            venv_status: Virtual environment status
        """
        # Main title
        st.markdown(f'<h1 class="main-header">{self.title}</h1>', unsafe_allow_html=True)
        
        # System status indicators
        self._render_status_indicators(ai_status, venv_status)
    
    def _render_status_indicators(self, ai_status: Dict[str, Any], venv_status: bool) -> None:
        """Render the system status indicator row."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_ai_status(ai_status)
        
        with col2:
            self._render_venv_status(venv_status)
        
        with col3:
            self._render_database_status(ai_status)
        
        with col4:
            self._render_streamlit_status()
    
    def _render_ai_status(self, ai_status: Dict[str, Any]) -> None:
        """Render AI system status."""
        if ai_status['initialized']:
            st.markdown(
                '<div class="system-status status-online">🟢 AI System Online</div>', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="system-status status-offline">🔴 AI System Offline</div>', 
                unsafe_allow_html=True
            )
    
    def _render_venv_status(self, venv_status: bool) -> None:
        """Render virtual environment status."""
        if venv_status:
            st.markdown(
                '<div class="system-status status-online">🟢 VEnv Active</div>', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="system-status status-offline">🟡 System Python</div>', 
                unsafe_allow_html=True
            )
    
    def _render_database_status(self, ai_status: Dict[str, Any]) -> None:
        """Render database connection status."""
        if ai_status['initialized'] and ai_status['interface']:
            try:
                health = ai_status['interface'].get_system_health()
                if health.get('database', {}).get('status') == 'healthy':
                    st.markdown(
                        '<div class="system-status status-online">🟢 Database OK</div>', 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="system-status status-offline">🔴 Database Error</div>', 
                        unsafe_allow_html=True
                    )
            except:
                st.markdown(
                    '<div class="system-status status-offline">🔴 Database Unknown</div>', 
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<div class="system-status status-offline">🔴 Database N/A</div>', 
                unsafe_allow_html=True
            )
    
    def _render_streamlit_status(self) -> None:
        """Render Streamlit application status."""
        st.markdown(
            '<div class="system-status status-online">🟢 Streamlit Ready</div>', 
            unsafe_allow_html=True
        )
