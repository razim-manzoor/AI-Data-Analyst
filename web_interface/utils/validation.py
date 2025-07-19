"""
Input validation utilities for the web interface.

Provides validation and sanitization for user inputs.
"""

import re
from typing import Optional, Tuple, List


class InputValidator:
    """Validates and sanitizes user inputs for the web interface."""
    
    # Common SQL injection patterns to watch for
    SQL_INJECTION_PATTERNS = [
        r";\s*(drop|delete|insert|update|create|alter)\s+",
        r"union\s+select",
        r"'.*'.*or.*'.*'",
        r"--.*$",
        r"/\*.*\*/",
    ]
    
    # Maximum input lengths
    MAX_QUESTION_LENGTH = 1000
    MAX_SESSION_ID_LENGTH = 100
    
    @classmethod
    def validate_question(cls, question: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a user question for safety and appropriateness.
        
        Args:
            question: The user's question string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not question:
            return False, "Question cannot be empty"
        
        if not question.strip():
            return False, "Question cannot be only whitespace"
        
        if len(question) > cls.MAX_QUESTION_LENGTH:
            return False, f"Question too long (max {cls.MAX_QUESTION_LENGTH} characters)"
        
        # Check for potential SQL injection attempts
        question_lower = question.lower()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return False, "Question contains potentially unsafe content"
        
        return True, None
    
    @classmethod
    def sanitize_question(cls, question: str) -> str:
        """
        Sanitize a question string for safe processing.
        
        Args:
            question: Raw question string
            
        Returns:
            Sanitized question string
        """
        if not question:
            return ""
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', question.strip())
        
        # Remove potential script tags (just in case)
        sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Limit length
        if len(sanitized) > cls.MAX_QUESTION_LENGTH:
            sanitized = sanitized[:cls.MAX_QUESTION_LENGTH].strip()
        
        return sanitized
    
    @classmethod
    def validate_session_id(cls, session_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a session ID.
        
        Args:
            session_id: Session identifier string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not session_id:
            return False, "Session ID cannot be empty"
        
        if len(session_id) > cls.MAX_SESSION_ID_LENGTH:
            return False, f"Session ID too long (max {cls.MAX_SESSION_ID_LENGTH} characters)"
        
        # Session ID should only contain alphanumeric characters, underscores, and hyphens
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            return False, "Session ID contains invalid characters"
        
        return True, None
    
    @classmethod
    def get_safe_filename(cls, filename: str) -> str:
        """
        Generate a safe filename from user input.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename string
        """
        if not filename:
            return "unnamed_file"
        
        # Remove or replace unsafe characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove excessive dots and spaces
        safe_name = re.sub(r'\.{2,}', '.', safe_name)
        safe_name = re.sub(r'\s+', '_', safe_name.strip())
        
        # Ensure it's not empty after cleaning
        if not safe_name or safe_name == '.':
            safe_name = "unnamed_file"
        
        # Limit length
        if len(safe_name) > 255:
            name_part, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
            max_name_len = 255 - len(ext) - 1 if ext else 255
            safe_name = name_part[:max_name_len] + ('.' + ext if ext else '')
        
        return safe_name
    
    @classmethod
    def is_safe_for_display(cls, text: str) -> bool:
        """
        Check if text is safe for HTML display.
        
        Args:
            text: Text to check
            
        Returns:
            True if safe, False otherwise
        """
        if not text:
            return True
        
        # Check for script tags
        if re.search(r'<script', text, re.IGNORECASE):
            return False
        
        # Check for javascript: protocol
        if re.search(r'javascript:', text, re.IGNORECASE):
            return False
        
        # Check for event handlers
        event_handlers = ['onclick', 'onload', 'onerror', 'onmouseover']
        for handler in event_handlers:
            if handler in text.lower():
                return False
        
        return True
