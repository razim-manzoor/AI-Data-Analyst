"""
Configuration validation and management module.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from error_handling import error_handler, ErrorCodes, SystemError, ErrorSeverity

@dataclass
class ValidationResult:
    """Result of configuration validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    config_summary: Dict[str, Any]

class ConfigValidator:
    """Validates system configuration and dependencies."""
    
    def __init__(self, config_module):
        """Initialize with configuration module."""
        self.config = config_module
        
    def validate_all(self) -> ValidationResult:
        """Perform comprehensive configuration validation."""
        errors = []
        warnings = []
        
        # Validate paths
        path_validation = self._validate_paths()
        errors.extend(path_validation.get("errors", []))
        warnings.extend(path_validation.get("warnings", []))
        
        # Validate files
        file_validation = self._validate_files()
        errors.extend(file_validation.get("errors", []))
        warnings.extend(file_validation.get("warnings", []))
        
        # Validate LLM connection
        llm_validation = self._validate_llm()
        errors.extend(llm_validation.get("errors", []))
        warnings.extend(llm_validation.get("warnings", []))
        
        # Validate environment
        env_validation = self._validate_environment()
        errors.extend(env_validation.get("errors", []))
        warnings.extend(env_validation.get("warnings", []))
        
        # Create configuration summary
        config_summary = {
            "project_root": str(self.config.PROJECT_ROOT),
            "model": self.config.MODEL,
            "db_file": self.config.DB_FILE,
            "csv_file": self.config.CSV_FILE,
            "log_file": self.config.LOG_FILE,
            "chart_output_dir": getattr(self.config, 'CHART_OUTPUT_DIR', 'Not set'),
            "paths_exist": {
                "database": os.path.exists(self.config.DB_FILE),
                "csv": os.path.exists(self.config.CSV_FILE),
                "logs_dir": os.path.exists(os.path.dirname(self.config.LOG_FILE))
            }
        }
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            config_summary=config_summary
        )
    
    def _validate_paths(self) -> Dict[str, List[str]]:
        """Validate all configured paths."""
        errors = []
        warnings = []
        
        # Check if project root exists and is accessible
        if not os.path.exists(self.config.PROJECT_ROOT):
            errors.append(f"Project root does not exist: {self.config.PROJECT_ROOT}")
        elif not os.access(self.config.PROJECT_ROOT, os.R_OK):
            errors.append(f"Project root is not readable: {self.config.PROJECT_ROOT}")
            
        # Check data directory
        data_dir = os.path.dirname(self.config.DB_FILE)
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
                warnings.append(f"Created missing data directory: {data_dir}")
            except Exception as e:
                errors.append(f"Could not create data directory {data_dir}: {e}")
        
        # Check logs directory
        logs_dir = os.path.dirname(self.config.LOG_FILE)
        if not os.path.exists(logs_dir):
            try:
                os.makedirs(logs_dir, exist_ok=True)
                warnings.append(f"Created missing logs directory: {logs_dir}")
            except Exception as e:
                errors.append(f"Could not create logs directory {logs_dir}: {e}")
                
        return {"errors": errors, "warnings": warnings}
    
    def _validate_files(self) -> Dict[str, List[str]]:
        """Validate required files."""
        errors = []
        warnings = []
        
        # Check database file
        if not os.path.exists(self.config.DB_FILE):
            warnings.append(f"Database file does not exist: {self.config.DB_FILE}")
            warnings.append("Run 'python src/create_database.py' to create it")
        
        # Check CSV file
        if not os.path.exists(self.config.CSV_FILE):
            warnings.append(f"CSV file does not exist: {self.config.CSV_FILE}")
            warnings.append("Some features may not work without source data")
        
        return {"errors": errors, "warnings": warnings}
    
    def _validate_llm(self) -> Dict[str, List[str]]:
        """Validate LLM configuration and connectivity."""
        errors = []
        warnings = []
        
        try:
            # Test if LLM is accessible
            if hasattr(self.config, 'llm'):
                # Try a simple invoke test
                test_response = self.config.llm.invoke("test")
                if not test_response:
                    warnings.append("LLM test returned empty response")
            else:
                errors.append("LLM not properly initialized in config")
                
        except Exception as e:
            errors.append(f"LLM validation failed: {e}")
            errors.append(f"Ensure {self.config.MODEL} model is available in Ollama")
            
        return {"errors": errors, "warnings": warnings}
    
    def _validate_environment(self) -> Dict[str, List[str]]:
        """Validate environment setup."""
        errors = []
        warnings = []
        
        # Check Python version
        import sys
        python_version = sys.version_info
        if python_version < (3, 8):
            errors.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        
        # Check virtual environment
        if 'venv' not in sys.executable.lower() and 'conda' not in sys.executable.lower():
            warnings.append("Not running in virtual environment - recommended for isolation")
        
        # Check required packages
        required_packages = ['langchain', 'langgraph', 'streamlit', 'pandas', 'matplotlib']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            errors.append(f"Missing required packages: {', '.join(missing_packages)}")
            errors.append("Run 'pip install -r requirements.txt' to install dependencies")
            
        return {"errors": errors, "warnings": warnings}
    
    def create_missing_directories(self) -> bool:
        """Create any missing directories."""
        try:
            directories = [
                os.path.dirname(self.config.DB_FILE),
                os.path.dirname(self.config.LOG_FILE),
                getattr(self.config, 'CHART_OUTPUT_DIR', os.path.join(self.config.PROJECT_ROOT, 'data'))
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                
            return True
        except Exception as e:
            error_handler.add_error(SystemError(
                code=ErrorCodes.CONFIG_INVALID,
                message=f"Could not create required directories: {e}",
                severity=ErrorSeverity.ERROR
            ))
            return False

def validate_configuration(config_module) -> ValidationResult:
    """Convenience function to validate configuration."""
    validator = ConfigValidator(config_module)
    return validator.validate_all()
