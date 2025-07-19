"""
Web Interface Components Package

This package contains modular UI components for the Streamlit interface.
Each component is responsible for a specific part of the user interface.
"""

try:
    from .header import HeaderComponent
    from .sidebar import SidebarComponent  
    from .data_upload import DataUploadComponent
    from .schema_aware_upload import SchemaAwareDataUploadComponent
    from .universal_dataset import UniversalDatasetComponent
    # from .chat import ChatComponent
    # from .analytics import AnalyticsComponent
    # from .diagnostics import DiagnosticsComponent
except ImportError:
    # Fallback for direct imports
    from header import HeaderComponent
    from sidebar import SidebarComponent
    from data_upload import DataUploadComponent
    from schema_aware_upload import SchemaAwareDataUploadComponent
    from universal_dataset import UniversalDatasetComponent

__all__ = [
    'HeaderComponent',
    'SidebarComponent',
    'DataUploadComponent'
    # 'ChatComponent',
    # 'AnalyticsComponent',
    # 'DiagnosticsComponent'
]
