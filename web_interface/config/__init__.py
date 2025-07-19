"""
Web Interface Configuration Package

Contains configuration constants and settings for the web interface.
"""

try:
    from .ui_config import (
        APP_CONFIG,
        MENU_ITEMS,
        SAMPLE_QUESTIONS,
        DIAGNOSTIC_MODULES,
        PERFORMANCE_CONFIG,
        DISPLAY_CONFIG,
        FILE_CONFIG,
        ERROR_MESSAGES,
        SUCCESS_MESSAGES,
        THEME_COLORS,
        COMPONENT_CONFIG,
        LOG_FILE,
        DB_FILE,
        MODEL,
        llm,
        get_app_config
    )
except ImportError:
    # Fallback for direct imports
    from ui_config import (
        APP_CONFIG,
        MENU_ITEMS,
        SAMPLE_QUESTIONS,
        DIAGNOSTIC_MODULES,
        PERFORMANCE_CONFIG,
        DISPLAY_CONFIG,
        FILE_CONFIG,
        ERROR_MESSAGES,
        SUCCESS_MESSAGES,
        THEME_COLORS,
        COMPONENT_CONFIG,
        LOG_FILE,
        DB_FILE,
        MODEL,
        llm,
        get_app_config
    )

__all__ = [
    'APP_CONFIG',
    'MENU_ITEMS',
    'SAMPLE_QUESTIONS',
    'DIAGNOSTIC_MODULES', 
    'PERFORMANCE_CONFIG',
    'DISPLAY_CONFIG',
    'FILE_CONFIG',
    'ERROR_MESSAGES',
    'SUCCESS_MESSAGES',
    'THEME_COLORS',
    'COMPONENT_CONFIG',
    'LOG_FILE',
    'DB_FILE',
    'MODEL',
    'llm',
    'get_app_config'
]
