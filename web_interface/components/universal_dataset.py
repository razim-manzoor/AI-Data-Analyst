"""
Universal Dataset Support Component

Transforms the AI Data Analyst into a universal data analysis platform
that can work with ANY dataset by:
1. Dynamic schema detection and adaptation
2. Intelligent table management
3. Automatic data type inference
4. Flexible upload and integration
"""

import streamlit as st
import pandas as pd
import os
import io
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import tempfile
import numpy as np
import re
from pathlib import Path

# Import database utilities
try:
    from src.database_manager import DatabaseManager
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.database_manager import DatabaseManager


class UniversalDatasetComponent:
    """
    Universal component that can handle ANY dataset format and automatically
    integrate it into the AI analysis system.
    """
    
    def __init__(self):
        """Initialize the universal dataset component."""
        self.db_manager = DatabaseManager()
        self.supported_formats = ['.csv', '.xlsx', '.json', '.tsv']
        self.max_file_size = 100 * 1024 * 1024  # 100MB limit
        
        # Common data type mappings for intelligent inference
        self.type_mappings = {
            'int64': 'INTEGER',
            'float64': 'REAL',
            'object': 'TEXT',
            'datetime64[ns]': 'TEXT',  # Store as ISO format
            'bool': 'INTEGER',  # SQLite doesn't have native boolean
            'category': 'TEXT'
        }
    
    def detect_data_types(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Intelligent data type detection and analysis.
        
        Returns comprehensive column analysis including:
        - Detected type
        - Sample values
        - Null percentage
        - Unique value count
        - Recommended SQL type
        """
        column_analysis = {}
        
        for col in df.columns:
            series = df[col]
            
            # Basic statistics
            null_count = series.isnull().sum()
            null_percentage = (null_count / len(series)) * 100
            unique_count = series.nunique()
            
            # Type detection
            dtype = str(series.dtype)
            
            # Try to infer better types for object columns
            if dtype == 'object':
                # Check if it's actually numeric
                numeric_series = pd.to_numeric(series, errors='coerce')
                if not numeric_series.isnull().all():
                    if (numeric_series % 1 == 0).all():
                        dtype = 'int64_inferred'
                    else:
                        dtype = 'float64_inferred'
                
                # Check if it's datetime
                elif self._looks_like_datetime(series):
                    dtype = 'datetime_inferred'
                
                # Check if it's categorical (low unique values)
                elif unique_count / len(series) < 0.1 and unique_count < 50:
                    dtype = 'category_inferred'
            
            # Get sample values (non-null)
            sample_values = series.dropna().head(5).tolist()
            
            # SQL type recommendation
            sql_type = self._get_sql_type(dtype, series)
            
            column_analysis[col] = {
                'pandas_type': dtype,
                'sql_type': sql_type,
                'null_count': null_count,
                'null_percentage': null_percentage,
                'unique_count': unique_count,
                'total_rows': len(series),
                'sample_values': sample_values,
                'is_numeric': dtype in ['int64', 'float64', 'int64_inferred', 'float64_inferred'],
                'is_categorical': dtype in ['category', 'category_inferred'] or unique_count < 20,
                'is_datetime': dtype in ['datetime64[ns]', 'datetime_inferred']
            }
        
        return column_analysis
    
    def _looks_like_datetime(self, series: pd.Series) -> bool:
        """Check if a series looks like datetime data."""
        try:
            # Try to parse a sample of the data
            sample = series.dropna().head(10)
            if len(sample) == 0:
                return False
            
            parsed = pd.to_datetime(sample, errors='coerce')
            success_rate = (1 - parsed.isnull().sum() / len(sample))
            return success_rate > 0.7
        except:
            return False
    
    def _get_sql_type(self, pandas_type: str, series: pd.Series) -> str:
        """Convert pandas type to appropriate SQL type."""
        if 'int' in pandas_type:
            return 'INTEGER'
        elif 'float' in pandas_type:
            return 'REAL'
        elif 'datetime' in pandas_type:
            return 'TEXT'  # Store as ISO string
        elif pandas_type in ['bool']:
            return 'INTEGER'
        else:
            # For text fields, check if we should use VARCHAR with limit
            if pandas_type == 'object':
                max_length = series.astype(str).str.len().max()
                if pd.isna(max_length) or max_length > 500:
                    return 'TEXT'
                else:
                    return f'VARCHAR({min(int(max_length * 1.2), 500)})'
            return 'TEXT'
    
    def suggest_table_name(self, filename: str, existing_tables: List[str]) -> str:
        """Suggest a good table name based on filename."""
        # Clean filename for table name
        base_name = Path(filename).stem
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name.lower())
        table_name = re.sub(r'_+', '_', table_name)
        table_name = table_name.strip('_')
        
        # Ensure it starts with a letter
        if table_name and not table_name[0].isalpha():
            table_name = 'data_' + table_name
        
        # Handle empty or invalid names
        if not table_name or table_name in ['data', 'table']:
            table_name = 'dataset'
        
        # Make unique if conflicts with existing tables
        original_name = table_name
        counter = 1
        while table_name in existing_tables:
            table_name = f"{original_name}_{counter}"
            counter += 1
        
        return table_name
    
    def create_table_from_analysis(self, table_name: str, column_analysis: Dict[str, Dict]) -> str:
        """Generate CREATE TABLE SQL from column analysis."""
        columns = []
        
        for col_name, analysis in column_analysis.items():
            # Clean column name for SQL
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', col_name)
            clean_name = re.sub(r'_+', '_', clean_name).strip('_')
            
            if not clean_name or not clean_name[0].isalpha():
                clean_name = 'col_' + clean_name
            
            sql_type = analysis['sql_type']
            columns.append(f'"{clean_name}" {sql_type}')
        
        create_sql = f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            {',\\n    '.join(columns)}
        )
        '''
        
        return create_sql
    
    def load_file_to_dataframe(self, uploaded_file) -> Tuple[pd.DataFrame, str]:
        """Load various file formats into a pandas DataFrame."""
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        try:
            if file_extension == '.csv':
                # Try different encodings and separators
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                
            elif file_extension == '.xlsx':
                df = pd.read_excel(uploaded_file)
                
            elif file_extension == '.json':
                df = pd.read_json(uploaded_file)
                
            elif file_extension == '.tsv':
                df = pd.read_csv(uploaded_file, sep='\\t')
                
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            return df, "success"
            
        except Exception as e:
            return pd.DataFrame(), f"Error loading file: {str(e)}"
    
    def insert_data_to_table(self, df: pd.DataFrame, table_name: str, column_analysis: Dict[str, Dict]) -> Tuple[bool, str]:
        """Insert DataFrame data into the created table."""
        try:
            # Clean and prepare data
            df_clean = df.copy()
            
            # Convert data types based on analysis
            for col, analysis in column_analysis.items():
                if col in df_clean.columns:
                    if analysis['is_datetime']:
                        df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
                    elif analysis['is_numeric'] and 'int' in analysis['pandas_type']:
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype('Int64')
                    elif analysis['is_numeric'] and 'float' in analysis['pandas_type']:
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
            # Use SQLAlchemy to insert data
            from sqlalchemy import create_engine
            engine = create_engine(f"sqlite:///{self.db_manager.db_file}")
            
            df_clean.to_sql(table_name, engine, if_exists="append", index=False)
            
            return True, f"Successfully inserted {len(df_clean)} rows into table '{table_name}'"
            
        except Exception as e:
            return False, f"Data insertion error: {str(e)}"
    
    def get_existing_tables(self) -> List[str]:
        """Get list of existing tables in the database."""
        try:
            schema = self.db_manager.get_schema()
            if 'table_details' in schema:
                return list(schema['table_details'].keys())
            return []
        except:
            return []
    
    def render_universal_upload_interface(self):
        """Render the universal dataset upload interface."""
        st.markdown("### 🌍 Universal Dataset Upload")
        st.markdown("*Transform any dataset into an AI-analyzable format*")
        
        # Information about supported formats
        with st.expander("📋 Supported Formats & Features", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📁 Supported File Types:**")
                st.markdown("- CSV files (any delimiter)")
                st.markdown("- Excel files (.xlsx)")
                st.markdown("- JSON files")
                st.markdown("- TSV files")
            
            with col2:
                st.markdown("**🎯 Smart Features:**")
                st.markdown("- Automatic data type detection")
                st.markdown("- Intelligent column analysis")
                st.markdown("- Dynamic table creation")
                st.markdown("- Multi-format support")
        
        # File upload
        st.markdown("#### 📤 Upload Your Dataset")
        uploaded_file = st.file_uploader(
            "Choose any data file",
            type=['csv', 'xlsx', 'json', 'tsv'],
            help=f"Maximum file size: {self.max_file_size / (1024*1024):.0f}MB"
        )
        
        if uploaded_file is not None:
            # File info
            file_size = len(uploaded_file.getvalue())
            file_info_col1, file_info_col2, file_info_col3 = st.columns(3)
            
            with file_info_col1:
                st.metric("📁 File", uploaded_file.name)
            with file_info_col2:
                st.metric("💾 Size", f"{file_size / (1024*1024):.1f} MB")
            with file_info_col3:
                st.metric("🔗 Format", Path(uploaded_file.name).suffix.upper())
            
            # Load and analyze the file
            with st.spinner("🔍 Analyzing your dataset..."):
                df, load_status = self.load_file_to_dataframe(uploaded_file)
            
            if load_status != "success":
                st.error(f"❌ {load_status}")
                return
            
            if df.empty:
                st.error("❌ The uploaded file appears to be empty or invalid.")
                return
            
            # Show basic dataset info
            st.success(f"✅ **File loaded successfully!** {len(df)} rows × {len(df.columns)} columns")
            
            # Data preview
            st.markdown("#### 👀 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Column analysis
            with st.spinner("🧠 Performing intelligent column analysis..."):
                column_analysis = self.detect_data_types(df)
            
            st.markdown("#### 🔬 Column Analysis")
            
            # Create analysis table
            analysis_data = []
            for col, analysis in column_analysis.items():
                analysis_data.append({
                    'Column': col,
                    'Type': analysis['pandas_type'],
                    'SQL Type': analysis['sql_type'],
                    'Nulls': f"{analysis['null_percentage']:.1f}%",
                    'Unique': analysis['unique_count'],
                    'Sample Values': ', '.join(map(str, analysis['sample_values'][:3]))
                })
            
            analysis_df = pd.DataFrame(analysis_data)
            st.dataframe(analysis_df, use_container_width=True, hide_index=True)
            
            # Table configuration
            st.markdown("#### ⚙️ Table Configuration")
            
            # Get existing tables
            existing_tables = self.get_existing_tables()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Suggest table name
                suggested_name = self.suggest_table_name(uploaded_file.name, existing_tables)
                table_name = st.text_input(
                    "Table Name",
                    value=suggested_name,
                    help="Choose a unique name for your dataset table"
                )
            
            with col2:
                # Table action
                if existing_tables:
                    action = st.selectbox(
                        "Action",
                        ["create_new", "replace_existing", "append_to_existing"],
                        format_func=lambda x: {
                            "create_new": "🆕 Create new table",
                            "replace_existing": "🔄 Replace existing table",
                            "append_to_existing": "➕ Append to existing table"
                        }[x]
                    )
                else:
                    action = "create_new"
                    st.info("No existing tables found. Will create new table.")
            
            # Validation
            if not table_name:
                st.error("❌ Please provide a table name")
                return
            
            if action == "create_new" and table_name in existing_tables:
                st.error(f"❌ Table '{table_name}' already exists. Choose a different name or select replace/append.")
                return
            
            # Show what will happen
            if action == "create_new":
                st.info(f"📋 **Action:** Create new table '{table_name}' with {len(df)} rows")
            elif action == "replace_existing":
                st.warning(f"⚠️ **Action:** Replace table '{table_name}' (existing data will be lost)")
            else:
                st.info(f"➕ **Action:** Append {len(df)} rows to existing table '{table_name}'")
            
            # Final upload button
            if st.button("🚀 Upload Dataset", type="primary"):
                with st.spinner("📝 Creating table and uploading data..."):
                    
                    try:
                        # Create or prepare table
                        if action in ["create_new", "replace_existing"]:
                            # Drop table if replacing
                            if action == "replace_existing":
                                self.db_manager.execute_query(f'DROP TABLE IF EXISTS "{table_name}"')
                            
                            # Create new table
                            create_sql = self.create_table_from_analysis(table_name, column_analysis)
                            success = self.db_manager.execute_query(create_sql)
                            
                            if not success:
                                st.error("❌ Failed to create table")
                                return
                        
                        # Insert data
                        success, message = self.insert_data_to_table(df, table_name, column_analysis)
                        
                        if success:
                            st.success(f"🎉 {message}")
                            st.balloons()
                            
                            # Show next steps
                            st.markdown("### 🎯 Next Steps")
                            st.info(f"💡 **Your dataset '{table_name}' is now ready for AI analysis!** You can ask questions like:")
                            
                            # Generate sample questions based on columns
                            sample_questions = self._generate_sample_questions(table_name, column_analysis)
                            for i, question in enumerate(sample_questions[:3]):
                                st.markdown(f"• *{question}*")
                            
                            # Refresh button
                            if st.button("🔄 Refresh App to Start Analyzing"):
                                st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    
                    except Exception as e:
                        st.error(f"❌ Upload failed: {str(e)}")
    
    def _generate_sample_questions(self, table_name: str, column_analysis: Dict[str, Dict]) -> List[str]:
        """Generate sample questions based on the dataset structure."""
        questions = []
        
        # Get column types
        numeric_cols = [col for col, analysis in column_analysis.items() if analysis['is_numeric']]
        text_cols = [col for col, analysis in column_analysis.items() if analysis['is_categorical']]
        date_cols = [col for col, analysis in column_analysis.items() if analysis['is_datetime']]
        
        # General questions
        questions.append(f"Show me a summary of the {table_name} data")
        questions.append(f"What are the column names and types in {table_name}?")
        
        # Numeric analysis
        if numeric_cols:
            questions.append(f"What is the average {numeric_cols[0]} in {table_name}?")
            if len(numeric_cols) > 1:
                questions.append(f"Show me the correlation between {numeric_cols[0]} and {numeric_cols[1]}")
        
        # Categorical analysis
        if text_cols:
            questions.append(f"What are the unique values in {text_cols[0]}?")
            if numeric_cols:
                questions.append(f"Show me {numeric_cols[0]} by {text_cols[0]}")
        
        # Time series analysis
        if date_cols and numeric_cols:
            questions.append(f"Show me the trend of {numeric_cols[0]} over time")
        
        return questions
