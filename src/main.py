import os
import logging
import time
from langgraph.graph import StateGraph, END
from config import LOG_FILE
from state import AgentState, create_initial_state, update_state_efficiently, get_state_summary
from database_manager import db_manager
from agent_manager import agent_manager
from typing import Dict, Any

# Set up optimized logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    filename=LOG_FILE,
    filemode='a'
)

# Add console handler for better debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

def get_schema(state: Dict[str, Any]) -> Dict[str, Any]:
    """Optimized database schema extraction with performance tracking"""
    step_start = time.time()
    
    try:
        logging.info("Starting optimized database schema extraction")
        
        # Use optimized database manager
        schema_info = db_manager.get_schema()
        
        if "error" in schema_info:
            logging.error(f"Schema extraction error: {schema_info['error']}")
            return update_state_efficiently(state, {
                "schema": schema_info["schema_text"],
                "errors": {**state.get("errors", {}), "schema": schema_info["error"]}
            })
        
        logging.info(f"Schema extracted successfully: {schema_info['table_count']} tables found")
        
        # Track performance
        elapsed = time.time() - step_start
        step_times = state.get("step_times", {})
        step_times["get_schema"] = elapsed
        
        return update_state_efficiently(state, {
            "schema": schema_info["schema_text"],
            "step_times": step_times
        })
        
    except Exception as e:
        error_msg = f"Unexpected error during schema extraction: {str(e)}"
        logging.error(error_msg)
        return update_state_efficiently(state, {
            "schema": f"Error: {error_msg}",
            "errors": {**state.get("errors", {}), "schema": error_msg}
        })

def route_question(state: Dict[str, Any]) -> Dict[str, Any]:
    """Optimized question routing with cached agents"""
    step_start = time.time()
    
    try:
        question = state.get("question", "")
        if not question:
            logging.error("No question provided for routing")
            return update_state_efficiently(state, {"route": "sql"})
        
        # Use cached agent manager
        route = agent_manager.route_question(question)
        
        # Track performance
        elapsed = time.time() - step_start
        step_times = state.get("step_times", {})
        step_times["route_question"] = elapsed
        
        return update_state_efficiently(state, {
            "route": route,
            "step_times": step_times
        })
        
    except Exception as e:
        error_msg = f"Error during question routing: {str(e)}"
        logging.error(error_msg)
        return update_state_efficiently(state, {
            "route": "sql",
            "errors": {**state.get("errors", {}), "routing": error_msg}
        })

def run_sql_query(state: Dict[str, Any]) -> Dict[str, Any]:
    """Optimized SQL query generation and execution"""
    step_start = time.time()
    
    try:
        question = state.get("question", "")
        schema = state.get("schema", "")
        
        if not question or not schema:
            error_msg = "Missing required state: question or schema"
            logging.error(error_msg)
            return update_state_efficiently(state, {
                "sql_query": "ERROR: " + error_msg,
                "data": "No data due to error",
                "errors": {**state.get("errors", {}), "sql": error_msg}
            })
        
        # Generate SQL using cached agent
        query = agent_manager.generate_sql_query(question, schema)
        
        # Execute query using optimized database manager
        data = db_manager.execute_query(query)
        
        # Track performance
        elapsed = time.time() - step_start
        step_times = state.get("step_times", {})
        step_times["run_sql_query"] = elapsed
        
        logging.info(f"SQL operation completed successfully in {elapsed:.2f}s")
        
        return update_state_efficiently(state, {
            "sql_query": query,
            "data": str(data),
            "step_times": step_times
        })
        
    except Exception as e:
        error_msg = f"Error during SQL query execution: {str(e)}"
        logging.error(error_msg)
        return update_state_efficiently(state, {
            "sql_query": state.get("sql_query", "Unknown"),
            "data": f"Error: {error_msg}",
            "errors": {**state.get("errors", {}), "sql_execution": error_msg}
        })

def generate_chart(state: Dict[str, Any]) -> Dict[str, Any]:
    """Optimized chart code generation"""
    step_start = time.time()
    
    try:
        question = state.get("question", "")
        if not question:
            error_msg = "Missing required state: question"
            logging.error(error_msg)
            return update_state_efficiently(state, {
                "chart_code": "# ERROR: " + error_msg,
                "errors": {**state.get("errors", {}), "chart": error_msg}
            })
        
        # Generate chart code using cached agent
        chart_code = agent_manager.generate_chart_code(question, state.get("data", ""))
        
        # Track performance
        elapsed = time.time() - step_start
        step_times = state.get("step_times", {})
        step_times["generate_chart"] = elapsed
        
        logging.info(f"Chart generation completed successfully in {elapsed:.2f}s")
        
        return update_state_efficiently(state, {
            "chart_code": chart_code,
            "step_times": step_times
        })
        
    except Exception as e:
        error_msg = f"Error during chart code generation: {str(e)}"
        logging.error(error_msg)
        return update_state_efficiently(state, {
            "chart_code": f"# Error: {error_msg}",
            "errors": {**state.get("errors", {}), "chart_generation": error_msg}
        })

# Define the optimized graph
workflow = StateGraph(AgentState)

workflow.add_node("get_schema", get_schema)
workflow.add_node("route_question", route_question)
workflow.add_node("run_sql_query", run_sql_query)
workflow.add_node("generate_chart", generate_chart)

workflow.set_entry_point("get_schema")
workflow.add_edge("get_schema", "route_question")
workflow.add_conditional_edges(
    "route_question",
    lambda x: x["route"],
    {
        "sql": "run_sql_query",
        "chart": "generate_chart",
    },
)
workflow.add_edge("run_sql_query", END)
workflow.add_edge("generate_chart", END)

# Compile the optimized graph
app = workflow.compile()

def main():
    """
    Optimized main function with performance monitoring and better error handling.
    """
    try:
        logging.info("=== Starting Optimized AI Data Analyst Application ===")
        
        # Perform system health checks
        if not db_manager.health_check():
            print("ERROR: Database health check failed")
            print("Please ensure the database is properly created and accessible.")
            return
        
        # Display agent cache info
        cache_info = agent_manager.get_cache_info()
        logging.info(f"Agent manager cache info: {cache_info}")
        
        print("--- Optimized AI Data Analyst is ready. Ask a question or type 'exit' to quit. ---")
        print("Performance monitoring is enabled. Check logs for detailed timing information.")
        
        session_start = time.time()
        question_count = 0
        
        while True:
            try:
                user_question = input("\nYour question: ")
                
                if user_question.lower() == 'exit':
                    session_duration = time.time() - session_start
                    print(f"\nSession Statistics:")
                    print(f"Total time: {session_duration:.2f}s")
                    print(f"Questions processed: {question_count}")
                    if question_count > 0:
                        print(f"Average time per question: {session_duration/question_count:.2f}s")
                    print("Exiting application.")
                    logging.info(f"Session completed: {question_count} questions in {session_duration:.2f}s")
                    break
                
                if not user_question.strip():
                    print("Please enter a question.")
                    continue

                question_start = time.time()
                question_count += 1
                
                logging.info(f"Processing question #{question_count}: {user_question}")

                # Create optimized initial state
                initial_state = create_initial_state(user_question)
                result = app.invoke(initial_state)
                
                question_duration = time.time() - question_start
                
                print(f"\n--- Agent's Answer (processed in {question_duration:.2f}s) ---")
                
                # Display results with error handling
                if result.get("errors"):
                    print("⚠️  Warnings/Errors occurred:")
                    for error_type, error_msg in result["errors"].items():
                        print(f"  - {error_type}: {error_msg}")
                
                if "data" in result and not str(result["data"]).startswith("Error:"):
                    print(f"SQL Query: {result.get('sql_query', 'N/A')}")
                    print(f"Data: {result['data']}")
                elif "chart_code" in result and not str(result["chart_code"]).startswith("# ERROR:"):
                    print(f"Chart Code:\n{result['chart_code']}")
                else:
                    print("❌ No valid results generated. Check the logs for details.")
                
                # Display performance info
                if result.get("step_times"):
                    print(f"\n📊 Performance Summary:")
                    for step, duration in result["step_times"].items():
                        print(f"  - {step}: {duration:.3f}s")
                
                # Display state summary for debugging
                summary = get_state_summary(result)
                logging.info(f"Question #{question_count} completed: {summary}")
                
            except KeyboardInterrupt:
                print("\nApplication interrupted by user.")
                logging.info("Application interrupted by user (Ctrl+C)")
                break
            except Exception as e:
                error_msg = f"Error processing question: {str(e)}"
                print(f"ERROR: {error_msg}")
                logging.error(error_msg)
                print("Please try again with a different question.")
                
    except Exception as e:
        error_msg = f"Fatal error in main application: {str(e)}"
        print(f"FATAL ERROR: {error_msg}")
        logging.critical(error_msg)

if __name__ == "__main__":
    main()
