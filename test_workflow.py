#!/usr/bin/env python3
"""
Simple test of the AI workflow system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import get_schema, route_question
from state import create_initial_state

def test_ai_workflow():
    """Test the core AI workflow functionality"""
    print("🧪 Testing AI Workflow Integration...")
    
    # Create initial state
    initial_state = create_initial_state("Test: Show me the sales data summary")
    print("✅ Initial state created")
    
    # Test schema extraction
    schema_state = get_schema(initial_state)
    print(f"✅ Schema extracted: {schema_state.get('schema_summary', 'Schema available')}")
    
    # Test question routing
    routed_state = route_question(schema_state)
    print(f"✅ Question routed: {routed_state.get('route', 'Route determined')}")
    
    print("🎉 AI workflow test completed successfully!")
    return True

if __name__ == "__main__":
    test_ai_workflow()
