"""
Styling utilities for Streamlit components.

Contains CSS styles and helper functions for consistent UI appearance.
"""

def get_main_css() -> str:
    """Get the main CSS styles for the application."""
    return """
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .system-status {
            padding: 0.5rem;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            margin: 0.5rem 0;
            border: 1px solid #e0e0e0;
        }
        
        .status-online {
            background-color: #d4edda;
            border-left-color: #28a745;
            border-color: #c3e6cb;
            color: #155724;
        }
        
        .status-offline {
            background-color: #f8d7da;
            border-left-color: #dc3545;
            border-color: #f5c6cb;
            color: #721c24;
        }
        
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .user-message {
            background-color: #f8f9fa;
            border-left-color: #007bff;
        }
        
        .assistant-message {
            background-color: #e8f5e8;
            border-left-color: #28a745;
        }
        
        .error-message {
            background-color: #ffebee;
            border-left-color: #f44336;
            border-color: #ffcdd2;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
    """

def get_status_css_class(status: str) -> str:
    """
    Get the appropriate CSS class for a status indicator.
    
    Args:
        status: Status string ('online', 'offline', etc.)
        
    Returns:
        CSS class name
    """
    status_classes = {
        'online': 'status-online',
        'offline': 'status-offline',
        'healthy': 'status-online',
        'error': 'status-offline',
        'unknown': 'status-offline'
    }
    
    return status_classes.get(status.lower(), 'status-offline')
