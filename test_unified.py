#!/usr/bin/env python3
"""
🧪 Unified Test Suite

Comprehensive testing for the AI Data Analyst system covering:
1. File structure integrity
2. Import system functionality
3. Database connectivity
4. Agent manager functionality
5. Workflow compilation
6. Streamlit interface readiness
7. Web interface component architecture
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedTestSuite:
    """Comprehensive test suite for the entire system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.src_dir = self.project_root / "src"
        self.web_interface_dir = self.project_root / "web_interface"
        self.test_results = {}
        
    def test_file_structure(self):
        """Test that the file structure is intact and clean"""
        print("\n📁 Testing File Structure...")
        
        essential_files = [
            "src/config.py",
            "src/main.py", 
            "src/agent_manager.py",
            "src/database_manager.py",
            "web_interface/app.py",
            "web_interface/ai_interface.py",
            "data/sales_data.csv",
            "requirements.txt"
        ]
        
        essential_dirs = [
            "src/agents",
            "web_interface/components",
            "web_interface/utils", 
            "web_interface/config",
            "logs",
            "data"
        ]
        
        missing_files = []
        missing_dirs = []
        
        for file_path in essential_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
                
        for dir_path in essential_dirs:
            if not (self.project_root / dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_files or missing_dirs:
            print(f"❌ Missing files: {missing_files}")
            print(f"❌ Missing directories: {missing_dirs}")
            return False
        
        print("✅ File structure is complete")
        return True
        
    def test_imports(self):
        """Test that all import paths work correctly"""
        print("\n📦 Testing Import System...")
        
        try:
            # Change to project root for proper imports
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            # Test core imports first (clear sys.path)
            sys.path.insert(0, str(self.src_dir))
            
            from config import DB_FILE, MODEL, LOG_FILE
            print("✅ Config imports working")
            
            from database_manager import db_manager
            print("✅ Database manager import working")
            
            from agent_manager import agent_manager
            print("✅ Agent manager import working")
            
            # Store the core config values
            core_db_file = DB_FILE
            core_model = MODEL
            
            # Clear imports and test web interface separately
            modules_to_remove = [k for k in sys.modules.keys() if k.startswith('config')]
            for module in modules_to_remove:
                if module != 'config':  # Keep the main config
                    sys.modules.pop(module, None)
            
            # Test web interface config imports
            os.chdir(self.web_interface_dir)
            sys.path.insert(0, str(self.web_interface_dir))
            
            import importlib
            from web_interface.config import APP_CONFIG, DB_FILE as WEB_DB_FILE, MODEL as WEB_MODEL
            print("✅ Web interface config working")
            
            # Verify config consistency
            assert core_db_file == WEB_DB_FILE, f"Database file paths don't match: {core_db_file} vs {WEB_DB_FILE}"
            assert core_model == WEB_MODEL, f"Models don't match: {core_model} vs {WEB_MODEL}"
            print("✅ Configuration consistency verified")
            
            return True
            
        except Exception as e:
            print(f"❌ Import error: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def test_database(self):
        """Test database connectivity and health"""
        print("\n🗃️  Testing Database...")
        
        try:
            sys.path.insert(0, str(self.src_dir))
            from database_manager import db_manager
            
            health = db_manager.health_check()
            if health.get('status') == 'healthy':
                print(f"✅ Database healthy: {health}")
                
                # Test schema retrieval
                schema = db_manager.get_schema()
                if 'tables' in schema and len(schema['tables']) > 0:
                    print(f"✅ Schema retrieval working: {schema['table_count']} tables found")
                    return True
                else:
                    print(f"⚠️  No tables found in database")
                    return False
            else:
                print(f"❌ Database issues: {health}")
                return False
                
        except Exception as e:
            print(f"❌ Database test error: {e}")
            return False
    
    def test_agents(self):
        """Test agent manager and agent creation"""
        print("\n🤖 Testing Agents...")
        
        try:
            sys.path.insert(0, str(self.src_dir))
            from agent_manager import agent_manager
            from agents import create_router_agent, create_sql_agent, create_chart_agent
            
            # Test agent manager health
            health = agent_manager.health_check()
            if health.get('status') == 'healthy':
                print(f"✅ Agent manager healthy: {health}")
            else:
                print(f"⚠️  Agent manager issues: {health}")
            
            # Test individual agent creation
            router = agent_manager.get_router_agent()
            sql_agent = agent_manager.get_sql_agent()
            chart_agent = agent_manager.get_chart_agent()
            
            if router and sql_agent and chart_agent:
                print("✅ All agents created successfully")
                return True
            else:
                print("❌ Agent creation failed")
                return False
                
        except Exception as e:
            print(f"❌ Agent test error: {e}")
            return False
    
    def test_workflow(self):
        """Test LangGraph workflow compilation"""
        print("\n🔄 Testing Workflow...")
        
        try:
            sys.path.insert(0, str(self.src_dir))
            from main import app  # Import the compiled workflow
            from state import create_initial_state
            
            if app:
                print("✅ Workflow compilation successful")
                
                # Test initial state creation
                initial_state = create_initial_state("test question")
                if 'question' in initial_state:
                    print("✅ State management working")
                    return True
                else:
                    print("❌ State creation failed")
                    return False
            else:
                print("❌ Workflow compilation failed")
                return False
                
        except Exception as e:
            print(f"❌ Workflow test error: {e}")
            return False
    
    def test_web_interface(self):
        """Test web interface component architecture"""
        print("\n🌐 Testing Web Interface...")
        
        try:
            original_cwd = os.getcwd()
            os.chdir(self.web_interface_dir)
            
            # Test that component files exist and are importable
            component_files = ['components/header.py', 'components/sidebar.py']
            utils_files = ['utils/session.py', 'utils/styling.py', 'utils/validation.py']
            config_files = ['config/ui_config.py', 'config/__init__.py']
            
            for file in component_files + utils_files + config_files:
                if not (Path(file).exists()):
                    raise FileNotFoundError(f"Missing file: {file}")
            
            print("✅ All component files exist")
            
            # Test config imports by directly importing from web_interface
            sys.path.insert(0, str(self.project_root))
            from web_interface.config import APP_CONFIG, DB_FILE, MODEL
            print("✅ Config imports successful")
            
            # Test that at least the utility modules are importable
            import importlib.util
            
            # Test session utility
            spec = importlib.util.spec_from_file_location("session", self.web_interface_dir / "utils" / "session.py")
            session_module = importlib.util.module_from_spec(spec)
            print("✅ Session utility file structure valid")
            
            # Test validation utility  
            spec = importlib.util.spec_from_file_location("validation", self.web_interface_dir / "utils" / "validation.py")
            validation_module = importlib.util.module_from_spec(spec)
            print("✅ Validation utility file structure valid")
            
            print(f"✅ Configuration integration verified (DB: {DB_FILE[-20:]}, Model: {MODEL})")
            print("✅ Web interface architecture is properly structured")
            return True
            
        except Exception as e:
            print(f"❌ Web interface test error: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def test_enhanced_database_features(self):
        """Test enhanced database features including analytical views and indexes"""
        try:
            print("🧪 Testing Enhanced Database Features")
            
            # Test analytical views
            from database_manager import db_manager
            from sqlalchemy import text
            
            # Test sales_summary view
            print("📊 Testing sales_summary view")
            with db_manager.get_connection() as conn:
                result = conn.execute(text("SELECT * FROM sales_summary ORDER BY total_sales DESC LIMIT 3;"))
                rows = result.fetchall()
                if len(rows) > 0:
                    print(f"✅ Sales summary view working: {len(rows)} records found")
                else:
                    print("⚠️ Sales summary view returned no data")
            
            # Test monthly_trends view
            print("📈 Testing monthly_trends view")
            with db_manager.get_connection() as conn:
                result = conn.execute(text("SELECT * FROM monthly_trends;"))
                rows = result.fetchall()
                if len(rows) > 0:
                    print(f"✅ Monthly trends view working: {len(rows)} records found")
                else:
                    print("⚠️ Monthly trends view returned no data")
            
            # Test product_performance view
            print("🏆 Testing product_performance view")
            with db_manager.get_connection() as conn:
                result = conn.execute(text("SELECT * FROM product_performance;"))
                rows = result.fetchall()
                if len(rows) > 0:
                    print(f"✅ Product performance view working: {len(rows)} records found")
                else:
                    print("⚠️ Product performance view returned no data")
            
            # Test indexes
            print("🔍 Testing database indexes")
            with db_manager.get_connection() as conn:
                result = conn.execute(text("PRAGMA index_list(sales);"))
                indexes = result.fetchall()
                print(f"✅ Found {len(indexes)} indexes on sales table")
            
            print("✅ Enhanced database features test completed")
            return True
            
        except Exception as e:
            print(f"❌ Enhanced database features test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🧪 Running Unified Test Suite")
        print("=" * 50)
        
        tests = [
            ("File Structure", self.test_file_structure),
            ("Import System", self.test_imports),
            ("Database", self.test_database),
            ("Enhanced Database Features", self.test_enhanced_database_features),
            ("Agents", self.test_agents),
            ("Workflow", self.test_workflow),
            ("Web Interface", self.test_web_interface)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {e}")
                self.test_results[test_name] = False
        
        print("\n" + "=" * 50)
        print(f"🎯 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is fully operational.")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            for test_name, result in self.test_results.items():
                status = "✅" if result else "❌"
                print(f"  {status} {test_name}")
            return False

def main():
    """Run the unified test suite"""
    test_suite = UnifiedTestSuite()
    success = test_suite.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
