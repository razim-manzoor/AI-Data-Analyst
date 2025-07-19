"""
Enhanced Data Upload Component for Streamlit Interface

Handles CSV file upload with strict schema validation, intelligent column mapping,
and seamless database integration for the AI Data Analyst application.
"""

import streamlit as st
import pandas as pd
import os
import io
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import tempfile
import numpy as np

# Import database utilities
try:
    from src.database_manager import DatabaseManager
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.database_manager import DatabaseManager


class SchemaAwareDataUploadComponent:
    """
    Enhanced component for uploading CSV data with strict schema validation.
    Provides intelligent column mapping, validation, and seamless database updates.
    """
    
    def __init__(self):
        """Initialize the schema-aware data upload component."""
        self.db_manager = DatabaseManager()
        self.supported_formats = ['.csv']
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        
        # Define the expected schema (based on current sales table)
        self.expected_schema = {
            'Date': {
                'type': 'TEXT', 
                'required': True, 
                'description': 'Date in YYYY-MM-DD format or similar',
                'sample_values': ['2024-01-05', '2024-12-31'],
                'validation': self._validate_date_column
            },
            'Region': {
                'type': 'TEXT', 
                'required': True, 
                'description': 'Geographic region',
                'sample_values': ['North', 'South', 'East', 'West'],
                'validation': self._validate_text_column
            },
            'Product': {
                'type': 'TEXT', 
                'required': True, 
                'description': 'Product name',
                'sample_values': ['Laptop', 'Monitor', 'Keyboard'],
                'validation': self._validate_text_column
            },
            'Units': {
                'type': 'BIGINT', 
                'required': True, 
                'description': 'Number of units sold (positive integer)',
                'sample_values': [10, 50, 25],
                'validation': self._validate_integer_column
            },
            'Sale': {
                'type': 'BIGINT', 
                'required': True, 
                'description': 'Sales amount in currency units (positive integer)',
                'sample_values': [8000, 1500, 5000],
                'validation': self._validate_integer_column
            }
        }
    
    def _validate_date_column(self, series: pd.Series) -> Tuple[bool, List[str]]:
        """Validate date column format and values."""
        errors = []
        
        # Check for null values
        if series.isnull().any():
            errors.append(f"Date column contains {series.isnull().sum()} null values")
        
        # Try to parse dates
        try:
            pd.to_datetime(series, errors='coerce')
            invalid_dates = pd.to_datetime(series, errors='coerce').isnull().sum()
            if invalid_dates > 0:
                errors.append(f"Date column contains {invalid_dates} invalid date values")
        except Exception as e:
            errors.append(f"Date parsing error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def _validate_text_column(self, series: pd.Series) -> Tuple[bool, List[str]]:
        """Validate text column format and values."""
        errors = []
        
        # Check for excessive null values
        null_pct = (series.isnull().sum() / len(series)) * 100
        if null_pct > 50:
            errors.append(f"Text column has {null_pct:.1f}% null values (too high)")
        
        # Check for empty strings
        empty_strings = (series == '').sum()
        if empty_strings > 0:
            errors.append(f"Text column contains {empty_strings} empty strings")
        
        return len(errors) == 0, errors
    
    def _validate_integer_column(self, series: pd.Series) -> Tuple[bool, List[str]]:
        """Validate integer column format and values."""
        errors = []
        
        # Check for null values
        if series.isnull().any():
            errors.append(f"Integer column contains {series.isnull().sum()} null values")
        
        # Try to convert to integer
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            if numeric_series.isnull().any():
                invalid_count = numeric_series.isnull().sum()
                errors.append(f"Integer column contains {invalid_count} non-numeric values")
            
            # Check for negative values in business context
            if (numeric_series < 0).any():
                negative_count = (numeric_series < 0).sum()
                errors.append(f"Integer column contains {negative_count} negative values (not expected for Units/Sales)")
                
        except Exception as e:
            errors.append(f"Integer validation error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def generate_template_csv(self) -> str:
        """Generate a CSV template based on the expected schema."""
        template_data = []
        
        # Create sample rows
        sample_data = [
            ['2024-01-05', 'North', 'Laptop', 10, 8000],
            ['2024-01-12', 'South', 'Monitor', 15, 3750],
            ['2024-01-19', 'East', 'Keyboard', 50, 1500],
            ['2024-01-26', 'West', 'Mouse', 30, 900]
        ]
        
        df = pd.DataFrame(sample_data, columns=list(self.expected_schema.keys()))
        return df.to_csv(index=False)
    
    def validate_uploaded_file(self, uploaded_file) -> Tuple[bool, Dict[str, Any]]:
        """
        Comprehensive validation of uploaded CSV file against expected schema.
        
        Returns:
            Tuple of (is_valid, validation_results)
        """
        validation_results = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'column_mapping': {},
            'data_preview': None,
            'file_info': {}
        }
        
        try:
            # Basic file validation
            if uploaded_file is None:
                validation_results['errors'].append("No file uploaded")
                return False, validation_results
            
            # File size check
            file_size = len(uploaded_file.getvalue())
            validation_results['file_info']['size_mb'] = file_size / (1024 * 1024)
            
            if file_size > self.max_file_size:
                validation_results['errors'].append(f"File size ({file_size / (1024*1024):.1f}MB) exceeds limit ({self.max_file_size / (1024*1024):.1f}MB)")
                return False, validation_results
            
            # Read CSV
            try:
                df = pd.read_csv(uploaded_file)
                validation_results['data_preview'] = df.head(10)
                validation_results['file_info']['rows'] = len(df)
                validation_results['file_info']['columns'] = len(df.columns)
            except Exception as e:
                validation_results['errors'].append(f"CSV parsing error: {str(e)}")
                return False, validation_results
            
            # Schema validation
            uploaded_columns = set(df.columns.str.strip())
            expected_columns = set(self.expected_schema.keys())
            
            # Check for missing required columns
            missing_columns = expected_columns - uploaded_columns
            if missing_columns:
                validation_results['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Check for extra columns
            extra_columns = uploaded_columns - expected_columns
            if extra_columns:
                validation_results['warnings'].append(f"Extra columns (will be ignored): {', '.join(extra_columns)}")
            
            # Validate individual columns
            column_validations = {}
            for col_name, col_config in self.expected_schema.items():
                if col_name in df.columns:
                    is_valid, errors = col_config['validation'](df[col_name])
                    column_validations[col_name] = {
                        'is_valid': is_valid,
                        'errors': errors
                    }
                    if not is_valid:
                        validation_results['errors'].extend([f"{col_name}: {error}" for error in errors])
            
            validation_results['column_validations'] = column_validations
            
            # Create column mapping for valid columns
            for col in expected_columns:
                if col in uploaded_columns:
                    validation_results['column_mapping'][col] = col
            
            # Overall validation result
            validation_results['is_valid'] = len(validation_results['errors']) == 0
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results['is_valid'], validation_results
    
    def update_database_with_validated_data(self, df: pd.DataFrame, update_mode: str = "replace") -> Tuple[bool, str]:
        """
        Update database with validated data.
        
        Args:
            df: Validated DataFrame with correct schema
            update_mode: "replace" or "append"
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Ensure we only use expected columns in correct order
            expected_columns = list(self.expected_schema.keys())
            df_clean = df[expected_columns].copy()
            
            # Data type conversions
            df_clean['Date'] = pd.to_datetime(df_clean['Date']).dt.strftime('%Y-%m-%d')
            df_clean['Units'] = pd.to_numeric(df_clean['Units']).astype(int)
            df_clean['Sale'] = pd.to_numeric(df_clean['Sale']).astype(int)
            
            # Database update
            if update_mode == "replace":
                # Clear existing data
                success = self.db_manager.execute_query("DELETE FROM sales")
                if not success:
                    return False, "Failed to clear existing data"
            
            # Insert new data
            from sqlalchemy import create_engine
            engine = create_engine(f"sqlite:///{self.db_manager.db_file}")
            
            df_clean.to_sql("sales", engine, if_exists="append", index=False)
            
            return True, f"Successfully {'replaced' if update_mode == 'replace' else 'appended'} {len(df_clean)} records"
            
        except Exception as e:
            return False, f"Database update error: {str(e)}"
    
    def render_upload_interface(self):
        """Render the enhanced schema-aware upload interface."""
        st.markdown("### 📁 Schema-Aware Data Upload")
        
        # Show current schema
        with st.expander("📋 Required Data Schema", expanded=False):
            st.markdown("**Your CSV must match this exact schema:**")
            
            schema_df = pd.DataFrame([
                {
                    'Column': col_name,
                    'Type': col_config['type'],
                    'Required': '✅' if col_config['required'] else '❌',
                    'Description': col_config['description'],
                    'Sample Values': ', '.join(map(str, col_config['sample_values']))
                }
                for col_name, col_config in self.expected_schema.items()
            ])
            
            st.dataframe(schema_df, use_container_width=True, hide_index=True)
        
        # Template download
        col1, col2 = st.columns(2)
        with col1:
            template_csv = self.generate_template_csv()
            st.download_button(
                label="📥 Download CSV Template",
                data=template_csv,
                file_name="sales_data_template.csv",
                mime="text/csv",
                help="Download a template CSV with the correct format and sample data"
            )
        
        with col2:
            st.info("💡 **Tip:** Download the template to ensure your data matches the required format!")
        
        # File upload
        st.markdown("#### 📤 Upload Your CSV File")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help=f"Maximum file size: {self.max_file_size / (1024*1024):.0f}MB"
        )
        
        if uploaded_file is not None:
            # Validate the uploaded file
            with st.spinner("🔍 Validating your data..."):
                is_valid, validation_results = self.validate_uploaded_file(uploaded_file)
            
            # Show validation results
            if is_valid:
                st.success("✅ **File validation passed!** Your data matches the required schema.")
                
                # Show data preview
                if validation_results['data_preview'] is not None:
                    st.markdown("#### 👀 Data Preview")
                    st.dataframe(validation_results['data_preview'], use_container_width=True)
                
                # File info
                file_info = validation_results['file_info']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Rows", file_info['rows'])
                with col2:
                    st.metric("📋 Columns", file_info['columns'])
                with col3:
                    st.metric("💾 Size", f"{file_info['size_mb']:.1f} MB")
                
                # Update options
                st.markdown("#### ⚙️ Upload Options")
                update_mode = st.radio(
                    "How should this data be integrated?",
                    ["replace", "append"],
                    format_func=lambda x: {
                        "replace": "🔄 Replace all existing data",
                        "append": "➕ Add to existing data"
                    }[x],
                    help="Replace will delete all existing records. Append will add new records to existing data."
                )
                
                # Confirmation
                if st.button("🚀 Update Database", type="primary"):
                    with st.spinner("📝 Updating database..."):
                        success, message = self.update_database_with_validated_data(
                            validation_results['data_preview'], 
                            update_mode
                        )
                    
                    if success:
                        st.success(f"🎉 {message}")
                        st.balloons()
                        
                        # Show next steps
                        st.info("💡 **Next Steps:** Your data has been updated! You can now ask the AI to analyze your new data.")
                        
                        # Suggest rerunning to refresh
                        if st.button("🔄 Refresh App"):
                            st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            else:
                # Show validation errors
                st.error("❌ **File validation failed!** Please fix the following issues:")
                
                # Errors
                if validation_results['errors']:
                    st.markdown("**🚨 Errors (must fix):**")
                    for error in validation_results['errors']:
                        st.markdown(f"- {error}")
                
                # Warnings
                if validation_results['warnings']:
                    st.markdown("**⚠️ Warnings:**")
                    for warning in validation_results['warnings']:
                        st.markdown(f"- {warning}")
                
                # Show data preview even if invalid
                if validation_results['data_preview'] is not None:
                    st.markdown("#### 👀 Your Data Preview")
                    st.dataframe(validation_results['data_preview'], use_container_width=True)
                
                # Column validation details
                if 'column_validations' in validation_results:
                    with st.expander("🔍 Detailed Column Validation"):
                        for col_name, col_validation in validation_results['column_validations'].items():
                            if col_validation['is_valid']:
                                st.success(f"✅ {col_name}: Valid")
                            else:
                                st.error(f"❌ {col_name}: {', '.join(col_validation['errors'])}")
