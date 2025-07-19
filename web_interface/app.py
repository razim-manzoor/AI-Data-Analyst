"""
🚀 AI Data Analyst - Streamlit Web Interface (Refactored Version)

Modular Streamlit interface with clean component architecture.
Features comprehensive error handling, virtual environment verification, and
seamless integration with the multi-agent LangGraph workflow.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, Any

# Import new modular components
try:
    from components import HeaderComponent, SidebarComponent, DataUploadComponent
    from components.schema_aware_upload import SchemaAwareDataUploadComponent
    from components.universal_dataset import UniversalDatasetComponent
    from utils import SessionManager, get_main_css
    from config import APP_CONFIG, MENU_ITEMS, SAMPLE_QUESTIONS, ERROR_MESSAGES
except ImportError:
    # Fallback to direct imports if package structure not working
    import sys
    from pathlib import Path
    web_interface_path = Path(__file__).parent
    sys.path.insert(0, str(web_interface_path))
    
    from components.header import HeaderComponent
    from components.sidebar import SidebarComponent
    from components.data_upload import DataUploadComponent
    from components.schema_aware_upload import SchemaAwareDataUploadComponent
    from components.universal_dataset import UniversalDatasetComponent
    from utils.session import SessionManager
    from utils.styling import get_main_css
    from config.ui_config import APP_CONFIG, MENU_ITEMS, SAMPLE_QUESTIONS, ERROR_MESSAGES

# Configure Streamlit page FIRST
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["initial_sidebar_state"],
    menu_items=MENU_ITEMS
)

# Apply CSS styling
st.markdown(get_main_css(), unsafe_allow_html=True)

# Setup import paths and verify virtual environment
def setup_environment():
    """Setup proper environment and import paths"""
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent  # Go up one level to project root
    src_dir = project_root / "src"
    
    # Change working directory to project root for proper relative path resolution
    os.chdir(project_root)
    
    # Verify virtual environment
    venv_active = 'venv' in sys.executable.lower()
    if not venv_active:
        st.warning(f"⚠️ Not using virtual environment. Current Python: {sys.executable}")
    
    # Add paths to sys.path
    paths_to_add = [str(project_root), str(src_dir)]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return project_root, src_dir, venv_active

# Initialize environment and session
project_root, src_dir, venv_status = setup_environment()
SessionManager.initialize()

def initialize_ai_system():
    """Initialize the AI system with comprehensive error handling"""
    ai_status = SessionManager.get_ai_status()
    
    try:
        # Import the interface module (from current directory or parent src)
        try:
            from ai_interface import AIDataAnalystInterface
        except ImportError:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent))
            from ai_interface import AIDataAnalystInterface
        
        # Create interface instance
        interface = AIDataAnalystInterface()
        
        # Initialize the system
        success = interface.initialize()
        
        if success:
            SessionManager.update_ai_status({
                'initialized': True,
                'error': None,
                'interface': interface
            })
            st.session_state.system_initialized = True
            return True
        else:
            SessionManager.update_ai_status({
                'initialized': False,
                'error': "System initialization failed",
                'interface': None
            })
            st.session_state.system_initialized = False
            return False
            
    except ImportError as e:
        error_msg = f"Import error: {str(e)}. Please ensure all dependencies are installed."
        SessionManager.update_ai_status({
            'initialized': False,
            'error': error_msg,
            'interface': None
        })
        st.session_state.system_initialized = False
        st.error(f"❌ {error_msg}")
        return False
        
    except Exception as e:
        error_msg = f"Initialization error: {str(e)}"
        SessionManager.update_ai_status({
            'initialized': False,
            'error': error_msg,
            'interface': None
        })
        st.session_state.system_initialized = False
        st.error(f"❌ {error_msg}")
        return False

# Custom CSS for beautiful styling (optimized for light theme)
st.markdown("""
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
        color: #155724;
        border-color: #c3e6cb;
    }
    
    .status-offline {
        background-color: #f8d7da;
        color: #721c24;
        border-color: #f5c6cb;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background-color: #f8f9fa;
        border-left-color: #667eea;
        border-color: #dee2e6;
    }
    
    .assistant-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
        border-color: #bbdefb;
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
""", unsafe_allow_html=True)

class StreamlitApp:
    """Main Streamlit application class"""
    
    def __init__(self):
        """Initialize the application with new component architecture."""
        self.header_component = HeaderComponent()
        self.sidebar_component = SidebarComponent(initialize_ai_system)
        self.data_upload_component = DataUploadComponent()
        
    def render_header(self):
        """Render the application header using HeaderComponent."""
        ai_status = SessionManager.get_ai_status()
        self.header_component.render(ai_status, venv_status)
        
    def render_sidebar(self):
        """Render the sidebar using SidebarComponent."""
        self.sidebar_component.render(venv_status)
    
    def show_system_diagnostics(self):
        """Show comprehensive system diagnostics"""
        st.markdown("### 🔍 System Diagnostics")
        
        # Environment Check
        st.markdown("#### 🌍 Environment")
        env_data = {
            "Component": ["Python Executable", "Virtual Environment", "Working Directory", "Streamlit Version"],
            "Status": [
                sys.executable,
                "✅ Active" if venv_status else "❌ Not Active",
                str(Path.cwd()),
                st.__version__
            ]
        }
        st.dataframe(pd.DataFrame(env_data), use_container_width=True, hide_index=True)
        
        # Module Import Status
        st.markdown("#### 📦 Module Import Status")
        modules_to_check = {
            'ai_interface': 'AI Interface Module',
            'config': 'Configuration',
            'database_manager': 'Database Manager',
            'agent_manager': 'Agent Manager',
            'main': 'Main Workflow'
        }
        
        import_status = []
        for module, description in modules_to_check.items():
            try:
                __import__(module)
                status = "✅ Available"
                error = "None"
            except Exception as e:
                status = "❌ Failed"
                error = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            
            import_status.append({
                "Module": description,
                "Status": status,
                "Error": error
            })
        
        st.dataframe(pd.DataFrame(import_status), use_container_width=True, hide_index=True)
        
        # System Health
        ai_status = SessionManager.get_ai_status()
        if ai_status['initialized'] and ai_status['interface']:
            st.markdown("#### 🏥 System Health")
            try:
                health = ai_status['interface'].get_system_health()
                
                health_data = []
                for component, details in health.items():
                    if isinstance(details, dict):
                        status = details.get('status', 'unknown')
                        health_data.append({
                            "Component": component.title(),
                            "Status": f"✅ {status}" if status == 'healthy' else f"❌ {status}",
                            "Details": str(details)[:100] + "..." if len(str(details)) > 100 else str(details)
                        })
                    elif isinstance(details, bool):
                        # Handle boolean values properly
                        health_data.append({
                            "Component": component.replace('_', ' ').title(),
                            "Status": f"✅ Online" if details else f"❌ Offline", 
                            "Details": "System operational" if details else "System not ready"
                        })
                    else:
                        # Handle other non-dict values
                        health_data.append({
                            "Component": component.replace('_', ' ').title(),
                            "Status": f"✅ {details}" if details else f"❌ {details}",
                            "Details": "N/A"
                        })
                
                if health_data:
                    st.dataframe(pd.DataFrame(health_data), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Could not retrieve system health: {e}")
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        # Display messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="chat-message user-message">'
                    f'<strong>👤 You:</strong><br>{message["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                css_class = "error-message" if message.get("error") else "assistant-message"
                st.markdown(
                    f'<div class="chat-message {css_class}">'
                    f'<strong>🤖 AI Analyst:</strong><br>{message["content"]}</div>',
                    unsafe_allow_html=True
                )
                
                # Show performance metrics
                if "performance" in message and not message.get("error"):
                    perf = message["performance"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("⏱️ Total Time", f"{perf.get('total_time', 0):.2f}s")
                    with col2:
                        st.metric("🔄 Components", perf.get('components_used', 'N/A'))
                    with col3:
                        st.metric("📊 Steps", len(perf.get('step_times', {})))
                
                # Show chart if available
                if "chart_path" in message and message["chart_path"]:
                    chart_path = message["chart_path"]
                    if os.path.exists(chart_path):
                        st.image(chart_path, caption="Generated Chart", use_column_width=True)
                        
                        # Download button
                        with open(chart_path, "rb") as file:
                            st.download_button(
                                label="📥 Download Chart",
                                data=file.read(),
                                file_name=os.path.basename(chart_path),
                                mime="image/png",
                                key=f"download_{hash(chart_path)}"
                            )
        
        # Chat input
        ai_status = SessionManager.get_ai_status()
        if ai_status['initialized']:
            user_input = st.chat_input("Ask me anything about your data... 💬")
            if user_input:
                self.process_user_input(user_input)
        else:
            st.error("🚨 AI System not initialized. Please click '🔄 Initialize AI System' in the sidebar.")
            st.chat_input("AI system not ready...", disabled=True)
    
    def process_user_input(self, user_input: str):
        """Process user input and generate response"""
        # Add user message
        SessionManager.add_message("user", user_input)
        
        ai_status = SessionManager.get_ai_status()
        if not ai_status['initialized'] or not ai_status['interface']:
            SessionManager.add_message(
                "assistant", 
                ERROR_MESSAGES["system_not_ready"],
                error=True
            )
            st.rerun()
            return
        
        # Process with AI system
        with st.spinner("🤖 AI is analyzing your question..."):
            try:
                start_time = time.time()
                
                # Get response from AI system
                response_data = ai_status['interface'].get_response(
                    user_input, 
                    session_id=st.session_state.session_id
                )
                
                processing_time = time.time() - start_time
                
                # Create response message using SessionManager
                SessionManager.add_message(
                    "assistant",
                    response_data.get("final_answer", "No response generated"),
                    performance=response_data.get("performance_tracking", {"total_time": processing_time}),
                    chart_path=response_data.get("chart_path"),
                    sql_query=response_data.get("sql_query"),
                    error="error" in response_data
                )
                
                # Add to query history using SessionManager
                SessionManager.add_query_to_history(
                    user_input,
                    response_data.get("final_answer", ""),
                    processing_time,
                    "error" not in response_data
                )
                
            except Exception as e:
                SessionManager.add_message(
                    "assistant",
                    ERROR_MESSAGES["processing_error"].format(error=str(e)),
                    error=True
                )
        
        st.rerun()
    
    def render_analytics_tab(self):
        """Render analytics and performance tab"""
        st.markdown("### 📈 Performance Analytics")
        
        if not st.session_state.query_history:
            st.info("📝 No queries processed yet. Start asking questions to see analytics!")
            
            # Show sample questions
            st.markdown("#### 💡 Try asking:")
            
            for question in SAMPLE_QUESTIONS[:5]:  # Show first 5 sample questions
                if st.button(f"💬 {question}", key=f"sample_{hash(question)}"):
                    # Add the sample question as if user typed it
                    ai_status = SessionManager.get_ai_status()
                    if ai_status['initialized']:
                        self.process_user_input(question)
                    else:
                        st.error("Please initialize the AI system first!")
            return
        
        # Analytics for existing queries
        df = pd.DataFrame(st.session_state.query_history)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Queries", len(df))
        with col2:
            avg_time = df['processing_time'].mean()
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
        with col3:
            success_rate = (df['success'].sum() / len(df)) * 100 if len(df) > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col4:
            fastest = df['processing_time'].min()
            st.metric("Fastest Response", f"{fastest:.2f}s")
        
        # Performance chart
        if len(df) > 1:
            st.markdown("#### ⏱️ Response Time Trends")
            fig = px.line(
                df.reset_index(), 
                x='index', 
                y='processing_time',
                title='Response Time Over Queries',
                labels={'index': 'Query Number', 'processing_time': 'Response Time (seconds)'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Query history table
        st.markdown("#### 📋 Query History")
        display_df = df[['timestamp', 'question', 'processing_time', 'success']].copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
        display_df['processing_time'] = display_df['processing_time'].round(3)
        display_df['success'] = display_df['success'].map({True: '✅', False: '❌'})
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Export functionality
        if st.button("📥 Export Query History"):
            export_data = {
                "session_id": st.session_state.session_id,
                "export_time": datetime.now().isoformat(),
                "query_history": st.session_state.query_history,
                "summary": {
                    "total_queries": len(df),
                    "avg_response_time": float(df['processing_time'].mean()),
                    "success_rate": float(success_rate)
                }
            }
            
            st.download_button(
                label="💾 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"query_history_{st.session_state.session_id}.json",
                mime="application/json"
            )
    
    def render_data_upload_tab(self):
        """Render enhanced data upload tab with universal dataset support"""
        st.markdown("### 📁 Data Upload & Management")
        
        # Option to choose upload mode
        upload_mode = st.radio(
            "📊 Choose Upload Mode:",
            ["universal", "schema_aware", "flexible"],
            format_func=lambda x: {
                "universal": "🌍 Universal Dataset (NEW!) - Accept ANY dataset format",
                "schema_aware": "🔒 Schema-Aware - Strict validation for sales data",
                "flexible": "🔧 Flexible Mode - Basic upload with manual mapping"
            }[x],
            help="Universal mode can handle any dataset. Schema-aware ensures sales data compatibility. Flexible allows customization."
        )
        
        try:
            if upload_mode == "universal":
                # Use the universal dataset component
                st.markdown("#### 🌍 Universal Dataset Upload")
                st.success("🎯 **Transform any dataset into an AI-analyzable format!** This mode can handle any CSV, Excel, JSON, or TSV file.")
                
                upload_component = UniversalDatasetComponent()
                upload_component.render_universal_upload_interface()
                
            elif upload_mode == "schema_aware":
                # Use the enhanced schema-aware component
                st.markdown("#### 🎯 Schema-Aware Upload")
                st.info("📋 This mode validates your CSV against the exact sales database schema for maximum compatibility.")
                
                upload_component = SchemaAwareDataUploadComponent()
                upload_component.render_upload_interface()
                
            else:
                # Use the original flexible component
                st.markdown("#### 🔧 Flexible Upload")
                st.warning("⚠️ This mode requires manual column mapping and may need data cleanup.")
                
                upload_component = DataUploadComponent()
                upload_component.render_upload_interface()
            
        except Exception as e:
            st.error(f"🚨 Upload component error: {e}")
            st.markdown("### 🔧 Recovery Options")
            
            if st.button("🔄 Retry Upload Component"):
                st.rerun()
                
            with st.expander("🔍 Error Details"):
                st.code(str(e))
    
    def run(self):
        """Main application runner"""
        self.render_header()
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📈 Analytics", "� Data Upload", "�🔧 System"])
        
        with tab1:
            self.render_chat_interface()
        
        with tab2:
            self.render_analytics_tab()
        
        with tab3:
            self.render_data_upload_tab()
        
        with tab4:
            self.show_system_diagnostics()

# Main application entry point
def main():
    """Main function to run the Streamlit app"""
    try:
        # Don't auto-initialize - let user control when to initialize
        # This prevents issues with working directory and state management
        
        # Run the application
        app = StreamlitApp()
        app.run()
        
    except Exception as e:
        st.error(f"🚨 Application Error: {e}")
        st.markdown("### 🔧 Recovery Options")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Restart App"):
                st.rerun()
        with col2:
            if st.button("🧹 Clear All Data"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Show detailed error
        with st.expander("🔍 Error Details"):
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
