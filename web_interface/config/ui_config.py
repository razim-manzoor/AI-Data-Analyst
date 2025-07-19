"""
UI Configuration constants and settings.

Centralized configuration for the web interface components.
"""

import os
from typing import Dict, List, Any

# Import main project configuration
try:
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))
    from config import LOG_FILE, PROJECT_ROOT, DB_FILE, MODEL, llm
except ImportError:
    # Fallback if main config not available
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "project.log")
    DB_FILE = os.path.join(PROJECT_ROOT, "data", "sales.db")
    MODEL = "mistral"
    # Create a fallback LLM object
    try:
        from langchain_ollama.chat_models import ChatOllama
        llm = ChatOllama(model=MODEL)
    except ImportError:
        llm = None

# Application metadata
APP_CONFIG = {
    "title": "🤖 AI Data Analyst",
    "icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Menu items for Streamlit
MENU_ITEMS = {
    'Get Help': 'https://github.com/your-repo/ai-data-analyst',
    'Report a bug': 'https://github.com/your-repo/ai-data-analyst/issues',
    'About': "AI Data Analyst - Enterprise-grade data analysis with multi-agent AI"
}

# Sample questions for users
SAMPLE_QUESTIONS = [
    "What tables are in the database?",
    "Show me the top 5 products by sales",
    "Create a chart of monthly revenue trends",
    "What's the average order value?",
    "Show me sales by region",
    "Which products have the highest profit margins?",
    "Create a pie chart of sales by category",
    "What are the monthly sales trends?",
    "Show me customer demographics"
]

# System diagnostic modules to check
DIAGNOSTIC_MODULES = {
    'ai_interface': 'AI Interface Module',
    'config': 'Configuration',
    'database_manager': 'Database Manager',
    'agent_manager': 'Agent Manager',
    'main': 'Main Workflow'
}

# Performance thresholds
PERFORMANCE_CONFIG = {
    "slow_response_threshold": 10.0,  # seconds
    "fast_response_threshold": 2.0,   # seconds
    "max_query_history": 100,         # maximum queries to keep in history
    "chart_cache_timeout": 300        # seconds to keep charts cached
}

# UI Display settings
DISPLAY_CONFIG = {
    "max_message_display": 50,        # maximum chat messages to display
    "data_preview_rows": 5,           # rows to show in data preview
    "max_data_display": 10,           # maximum data rows to show
    "chart_width": 800,               # default chart width
    "chart_height": 400               # default chart height
}

# File handling settings
FILE_CONFIG = {
    "max_filename_length": 255,
    "allowed_chart_extensions": ['.png', '.jpg', '.jpeg', '.svg'],
    "max_file_size_mb": 10
}

# Error messages
ERROR_MESSAGES = {
    "system_not_ready": "🚨 AI System not initialized. Please click '🔄 Initialize AI System' in the sidebar.",
    "processing_error": "🚨 **Processing Error**\n\nError: {error}\n\nPlease try again or check system health.",
    "initialization_failed": "❌ AI System initialization failed",
    "invalid_input": "❌ Invalid input provided. Please check your question and try again.",
    "file_not_found": "❌ Requested file could not be found",
    "permission_denied": "❌ Permission denied for the requested operation"
}

# Success messages
SUCCESS_MESSAGES = {
    "system_initialized": "✅ System initialized successfully!",
    "chat_cleared": "✅ Chat history cleared",
    "export_complete": "✅ Data exported successfully",
    "chart_generated": "✅ Chart generated successfully"
}

# Theme colors (matching .streamlit/config.toml)
THEME_COLORS = {
    "primary": "#ff6b6b",
    "background": "#ffffff", 
    "secondary_background": "#f0f2f6",
    "text": "#262730",
    "success": "#28a745",
    "error": "#dc3545",
    "warning": "#ffc107",
    "info": "#17a2b8"
}

# Component settings
COMPONENT_CONFIG = {
    "header": {
        "show_status_indicators": True,
        "refresh_interval": 30  # seconds
    },
    "sidebar": {
        "show_system_info": True,
        "show_diagnostics_button": True,
        "show_clear_button": True
    },
    "chat": {
        "enable_file_upload": False,  # Future feature
        "enable_voice_input": False,  # Future feature
        "auto_scroll": True
    },
    "analytics": {
        "enable_export": True,
        "show_performance_charts": True,
        "enable_filtering": True
    }
}

def get_app_config() -> Dict[str, Any]:
    """Get the complete application configuration."""
    return {
        "app": APP_CONFIG,
        "menu_items": MENU_ITEMS,
        "performance": PERFORMANCE_CONFIG,
        "display": DISPLAY_CONFIG,
        "files": FILE_CONFIG,
        "theme": THEME_COLORS,
        "components": COMPONENT_CONFIG
    }
