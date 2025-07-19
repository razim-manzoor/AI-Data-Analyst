"""
Optimized state management for the LangGraph multi-agent system.

This module provides:
- Efficient state serialization
- Optional field handling
- Memory-optimized state transitions
- Type-safe state management
"""

from typing import TypedDict, Annotated, Sequence, Optional, Any, Dict
import operator
from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):  # total=False allows optional fields
    """
    Optimized state dictionary for the multi-agent workflow.
    
    Fields are optional to reduce memory usage when not needed.
    """
    question: str
    data: Optional[str]
    schema: Optional[str]  
    chart_code: Optional[str]
    route: Optional[str]
    sql_query: Optional[str]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Performance tracking fields
    start_time: Optional[float]
    step_times: Optional[Dict[str, float]]
    
    # Error handling fields
    errors: Optional[Dict[str, str]]
    warnings: Optional[Dict[str, str]]


def create_initial_state(question: str) -> AgentState:
    """
    Create an optimized initial state with only required fields.
    
    Args:
        question: User question
        
    Returns:
        Initial agent state
    """
    import time
    
    return AgentState(
        question=question,
        start_time=time.time(),
        step_times={},
        errors={},
        warnings={}
    )


def update_state_efficiently(current_state: AgentState, updates: Dict[str, Any]) -> AgentState:
    """
    Efficiently update state by only modifying changed fields.
    
    Args:
        current_state: Current state
        updates: Dictionary of updates to apply
        
    Returns:
        Updated state
    """
    import time
    
    # Track timing for performance monitoring
    if 'step_times' not in current_state:
        current_state['step_times'] = {}
    
    # Update only the fields that changed
    for key, value in updates.items():
        if key in AgentState.__annotations__:
            current_state[key] = value
    
    # Update timing
    current_time = time.time()
    if 'start_time' in current_state:
        elapsed = current_time - current_state['start_time']
        current_state['step_times'][f"total_elapsed"] = elapsed
    
    return current_state


def get_state_summary(state: AgentState) -> Dict[str, Any]:
    """
    Get a memory-efficient summary of the current state.
    
    Args:
        state: Current agent state
        
    Returns:
        Summary dictionary
    """
    summary = {
        "has_question": bool(state.get("question")),
        "has_data": bool(state.get("data")),
        "has_schema": bool(state.get("schema")),
        "has_chart_code": bool(state.get("chart_code")),
        "route": state.get("route"),
        "has_sql_query": bool(state.get("sql_query")),
        "error_count": len(state.get("errors", {})),
        "warning_count": len(state.get("warnings", {}))
    }
    
    # Add timing information if available
    if state.get("step_times"):
        summary["timing"] = state["step_times"]
    
    return summary


def clear_large_fields(state: AgentState) -> AgentState:
    """
    Clear large fields from state to reduce memory usage.
    
    Args:
        state: Current agent state
        
    Returns:
        State with large fields cleared
    """
    # Clear potentially large fields while keeping metadata
    if state.get("data") and len(str(state["data"])) > 1000:
        state["data"] = f"[Large dataset cleared - {len(str(state['data']))} chars]"
    
    if state.get("schema") and len(str(state["schema"])) > 500:
        state["schema"] = f"[Schema cleared - {len(str(state['schema']))} chars]"
    
    return state
