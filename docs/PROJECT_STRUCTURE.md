# 📁 Project Structure

Clean, organized architecture for the AI Data Analyst platform.

## 🏗️ Directory Structure

```
AI_Data_Analyst/
├── 📄 README.md                    # Project overview and quick start
├── 📄 requirements.txt             # Python dependencies
├── 📄 setup.py                     # Package configuration
├── 📄 launch.py                    # Full launcher with options
├── 📄 quick_launch.py              # Simple web interface launcher
├── 📄 test_unified.py              # Comprehensive test suite
├── 📄 .gitignore                   # Git ignore patterns
│
├── 📁 src/                         # Core application source
│   ├── main.py                     # Main workflow orchestration
│   ├── config.py                   # Global configuration
│   ├── database_manager.py         # Database operations
│   ├── agent_manager.py            # AI agent management
│   ├── state.py                    # Application state management
│   ├── error_handling.py           # Error handling utilities
│   ├── config_validator.py         # Configuration validation
│   ├── chart_executor.py           # Chart generation
│   ├── create_database.py          # Database initialization
│   └── agents/                     # AI agent implementations
│       ├── __init__.py
│       ├── router.py               # Query routing agent
│       ├── sql_agent.py            # SQL generation agent
│       └── chart_agent.py          # Chart creation agent
│
├── 📁 web_interface/               # Streamlit web application
│   ├── app.py                      # Main Streamlit application
│   ├── ai_interface.py             # AI system interface layer
│   ├── components/                 # Modular UI components
│   │   ├── __init__.py
│   │   ├── header.py               # App header component
│   │   ├── sidebar.py              # Navigation sidebar
│   │   ├── data_upload.py          # Basic file upload
│   │   ├── schema_aware_upload.py  # Schema-validated upload
│   │   └── universal_dataset.py    # Universal dataset support
│   ├── config/                     # Web interface configuration
│   │   ├── __init__.py
│   │   └── ui_config.py            # UI settings and constants
│   └── utils/                      # Web interface utilities
│       ├── __init__.py
│       ├── session.py              # Session state management
│       ├── styling.py              # CSS and styling
│       └── validation.py           # Data validation helpers
│
├── 📁 data/                        # Data storage
│   ├── sales_data.csv              # Sample sales dataset
│   ├── sales.db                    # SQLite database
│   └── product_sales.png           # Sample visualization
│
├── 📁 sample_datasets/             # Example datasets for testing
│   ├── customers.csv               # Customer data example
│   ├── inventory.xlsx              # Product inventory example
│   ├── analytics.json              # Website analytics example
│   └── employees.tsv               # Employee data example
│
├── 📁 utilities/                   # Utility scripts and tools
│   ├── enhance_database.py         # Database optimization tool
│   └── create_sample_datasets.py   # Sample data generator
│
├── 📁 docs/                        # Documentation
│   ├── DEVELOPMENT_LOG.md          # Technical development log
│   ├── PROJECT_DOCUMENTATION.md    # Comprehensive project docs
│   └── WEB_INTERFACE_REVIEW.md     # Architecture review
│
├── 📁 logs/                        # Application logs
│   └── project.log                 # Main application log
│
└── 📁 .streamlit/                  # Streamlit configuration
    └── config.toml                 # Streamlit settings
```

## 🎯 Key Architectural Principles

### **Modular Design**
- Each component has a single responsibility
- Clean interfaces between modules
- Easy to extend and maintain

### **Separation of Concerns**
- **src/**: Core business logic and AI workflows
- **web_interface/**: User interface and presentation
- **data/**: Data storage and management
- **utilities/**: Helper tools and scripts

### **Configuration Management**
- Centralized configuration in `src/config.py`
- UI-specific settings in `web_interface/config/`
- Environment-based configuration support

### **Error Handling**
- Comprehensive error handling throughout
- Graceful degradation for missing components
- Detailed logging and debugging support

### **Testing Strategy**
- Unified test suite covering all components
- Integration testing for end-to-end workflows
- Performance testing for database operations

## 🔧 Component Responsibilities

### **Core System (`src/`)**
- **main.py**: Orchestrates the multi-agent workflow
- **database_manager.py**: Handles all database operations
- **agent_manager.py**: Manages AI agent lifecycle
- **agents/**: Individual AI agents for specific tasks

### **Web Interface (`web_interface/`)**
- **app.py**: Main Streamlit application with tab interface
- **components/**: Reusable UI components
- **utils/**: Helper functions for web interface
- **config/**: UI-specific configuration

### **Data Management (`data/`, `sample_datasets/`)**
- **data/**: Production data and database
- **sample_datasets/**: Example datasets for testing
- Support for multiple data formats

### **Development Tools (`utilities/`, `docs/`, `logs/`)**
- **utilities/**: Development and maintenance scripts
- **docs/**: Comprehensive documentation
- **logs/**: Application logging and debugging

This structure ensures maintainability, scalability, and ease of development while providing clear separation of concerns across the entire platform.
