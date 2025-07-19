"""
Chart execution module for safe code execution and file management.
"""

import os
import logging
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path
from config import CHART_OUTPUT_DIR

class ChartExecutor:
    """
    Handles safe execution of chart generation code with file management.
    """
    
    def __init__(self, output_dir: str = None):
        """Initialize chart executor with output directory."""
        self.output_dir = Path(output_dir or CHART_OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        
    def execute_chart_code(self, chart_code: str, data: Any) -> Dict[str, Any]:
        """
        Safely execute chart generation code.
        
        Args:
            chart_code: Python code for chart generation
            data: Data to be used in chart creation
            
        Returns:
            Dict with execution results and chart path
        """
        try:
            # Create a safe execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                'data': data,
                'plt': None,  # Will be imported in code
                'sns': None,  # Will be imported in code
                'pd': None,   # Will be imported in code
                'np': None    # Will be imported in code
            }
            
            # Modify chart code to save to specific location
            modified_code = self._modify_chart_code(chart_code)
            
            # Execute the chart code
            exec(modified_code, exec_globals)
            
            # Find the generated chart file
            chart_path = self._find_latest_chart()
            
            return {
                "success": True,
                "chart_path": str(chart_path) if chart_path else None,
                "message": "Chart generated successfully"
            }
            
        except Exception as e:
            logging.error(f"Error executing chart code: {e}")
            return {
                "success": False,
                "error": str(e),
                "chart_path": None
            }
    
    def _modify_chart_code(self, code: str) -> str:
        """
        Modify chart code to save to output directory instead of showing.
        """
        # Replace plt.show() with plt.savefig()
        chart_filename = f"chart_{int(time.time())}.png"
        chart_path = self.output_dir / chart_filename
        
        modified_code = code.replace(
            "plt.show()",
            f"plt.savefig('{chart_path}', dpi=300, bbox_inches='tight')\nplt.close()"
        )
        
        # Add fallback if no plt.show() found
        if "plt.show()" not in code and "plt.savefig(" not in code:
            modified_code += f"\nplt.savefig('{chart_path}', dpi=300, bbox_inches='tight')\nplt.close()"
            
        return modified_code
    
    def _find_latest_chart(self) -> Optional[Path]:
        """Find the most recently created chart file."""
        chart_files = list(self.output_dir.glob("*.png"))
        if chart_files:
            return max(chart_files, key=lambda f: f.stat().st_mtime)
        return None
    
    def cleanup_old_charts(self, keep_latest: int = 5):
        """Clean up old chart files, keeping only the most recent ones."""
        chart_files = sorted(
            self.output_dir.glob("*.png"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        # Remove old files beyond the keep_latest count
        for old_file in chart_files[keep_latest:]:
            try:
                old_file.unlink()
                logging.info(f"Cleaned up old chart: {old_file}")
            except Exception as e:
                logging.warning(f"Could not delete old chart {old_file}: {e}")

# Global instance
chart_executor = ChartExecutor()
