"""
Data Upload Component for Streamlit Interface

Handles CSV file upload, validation, and database integration.
"""

import streamlit as st
import pandas as pd
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import tempfile

# Import utilities - handle both relative and absolute imports
try:
    from ..utils.session import SessionManager
    from ..config.ui_config import SUCCESS_MESSAGES, ERROR_MESSAGES, FILE_CONFIG
except ImportError:
    from utils.session import SessionManager
    from config.ui_config import SUCCESS_MESSAGES, ERROR_MESSAGES, FILE_CONFIG


class DataUploadComponent:
    """Component for handling CSV file uploads and data management."""
    
    def __init__(self):
        """Initialize the data upload component."""
        self.session_manager = SessionManager()
        self.max_file_size_mb = FILE_CONFIG.get("max_file_size_mb", 10)
        
    def validate_csv_file(self, uploaded_file) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Validate uploaded CSV file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, message, dataframe)
        """
        try:
            # Check file size
            if uploaded_file.size > self.max_file_size_mb * 1024 * 1024:
                return False, f"File too large. Maximum size: {self.max_file_size_mb}MB", None
            
            # Check file extension
            if not uploaded_file.name.lower().endswith('.csv'):
                return False, "Please upload a CSV file", None
            
            # Try to read the CSV
            df = pd.read_csv(uploaded_file)
            
            # Basic validation
            if df.empty:
                return False, "CSV file is empty", None
            
            if len(df.columns) < 2:
                return False, "CSV must have at least 2 columns", None
            
            return True, "CSV file is valid", df
            
        except pd.errors.EmptyDataError:
            return False, "CSV file is empty or corrupted", None
        except pd.errors.ParserError as e:
            return False, f"CSV parsing error: {str(e)}", None
        except Exception as e:
            return False, f"Error reading CSV: {str(e)}", None
    
    def suggest_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Suggest column mappings based on column names.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary of suggested mappings
        """
        column_names = [col.lower() for col in df.columns]
        suggestions = {}
        
        # Common patterns for mapping
        mapping_patterns = {
            'date': ['date', 'time', 'timestamp', 'created', 'when'],
            'region': ['region', 'area', 'location', 'territory', 'zone'],
            'product': ['product', 'item', 'name', 'title', 'description'],
            'units': ['units', 'quantity', 'qty', 'amount', 'count'],
            'sale': ['sale', 'sales', 'revenue', 'price', 'value', 'total']
        }
        
        for target_col, patterns in mapping_patterns.items():
            for col_name in column_names:
                if any(pattern in col_name for pattern in patterns):
                    original_col = df.columns[column_names.index(col_name)]
                    suggestions[target_col] = original_col
                    break
        
        return suggestions
    
    def save_uploaded_file(self, uploaded_file, target_path: str) -> bool:
        """
        Save uploaded file to target location.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            target_path: Target file path
            
        Returns:
            Success status
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Save the file
            with open(target_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            return True
            
        except Exception as e:
            st.error(f"Error saving file: {e}")
            return False
    
    def update_database_with_new_data(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                                     operation: str = "replace") -> Tuple[bool, str]:
        """
        Update database with new data.
        
        Args:
            df: DataFrame with new data
            column_mapping: Mapping of CSV columns to database columns
            operation: "replace" or "append"
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Import database utilities
            import sys
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root / "src"))
            
            from database_manager import db_manager
            from sqlalchemy import text
            
            # Prepare the data
            mapped_df = df.rename(columns=column_mapping)
            required_columns = ['Date', 'Region', 'Product', 'Units', 'Sale']
            
            # Check if all required columns are mapped
            missing_columns = [col for col in required_columns if col not in mapped_df.columns]
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}"
            
            # Select only the required columns
            final_df = mapped_df[required_columns].copy()
            
            # Data validation and cleaning
            final_df = final_df.dropna()  # Remove rows with null values
            
            # Validate numeric columns
            try:
                final_df['Units'] = pd.to_numeric(final_df['Units'])
                final_df['Sale'] = pd.to_numeric(final_df['Sale'])
            except ValueError as e:
                return False, f"Error converting numeric columns: {e}"
            
            # Remove invalid data
            final_df = final_df[(final_df['Units'] > 0) & (final_df['Sale'] > 0)]
            
            if final_df.empty:
                return False, "No valid data remaining after cleaning"
            
            # Update database
            with db_manager.get_connection() as conn:
                if operation == "replace":
                    # Clear existing data
                    conn.execute(text("DELETE FROM sales"))
                    message_prefix = "Replaced"
                else:
                    message_prefix = "Added"
                
                # Insert new data
                final_df.to_sql('sales', conn, if_exists='append', index=False)
                conn.commit()
            
            return True, f"{message_prefix} {len(final_df)} rows in database"
            
        except Exception as e:
            return False, f"Database update failed: {str(e)}"
    
    def render_upload_interface(self) -> Optional[Dict[str, Any]]:
        """
        Render the file upload interface.
        
        Returns:
            Upload result information or None
        """
        st.header("📁 Data Upload")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help=f"Maximum file size: {self.max_file_size_mb}MB"
        )
        
        if uploaded_file is not None:
            # Validate file
            is_valid, message, df = self.validate_csv_file(uploaded_file)
            
            if not is_valid:
                st.error(message)
                return None
            
            st.success(message)
            
            # Show preview
            st.subheader("📊 Data Preview")
            st.write(f"**Rows:** {len(df)}, **Columns:** {len(df.columns)}")
            st.dataframe(df.head(), use_container_width=True)
            
            # Column mapping
            st.subheader("🔗 Column Mapping")
            st.write("Map your CSV columns to the required database fields:")
            
            suggestions = self.suggest_column_mapping(df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Required Fields:**")
                date_col = st.selectbox(
                    "Date Column", 
                    options=[''] + list(df.columns),
                    index=list(df.columns).index(suggestions.get('date', '')) + 1 if suggestions.get('date') in df.columns else 0
                )
                region_col = st.selectbox(
                    "Region Column", 
                    options=[''] + list(df.columns),
                    index=list(df.columns).index(suggestions.get('region', '')) + 1 if suggestions.get('region') in df.columns else 0
                )
                product_col = st.selectbox(
                    "Product Column", 
                    options=[''] + list(df.columns),
                    index=list(df.columns).index(suggestions.get('product', '')) + 1 if suggestions.get('product') in df.columns else 0
                )
            
            with col2:
                st.write("**Numeric Fields:**")
                units_col = st.selectbox(
                    "Units Column", 
                    options=[''] + list(df.columns),
                    index=list(df.columns).index(suggestions.get('units', '')) + 1 if suggestions.get('units') in df.columns else 0
                )
                sale_col = st.selectbox(
                    "Sales/Revenue Column", 
                    options=[''] + list(df.columns),
                    index=list(df.columns).index(suggestions.get('sale', '')) + 1 if suggestions.get('sale') in df.columns else 0
                )
            
            # Validate mapping
            column_mapping = {
                'Date': date_col,
                'Region': region_col, 
                'Product': product_col,
                'Units': units_col,
                'Sale': sale_col
            }
            
            missing_mappings = [field for field, col in column_mapping.items() if not col]
            
            if missing_mappings:
                st.warning(f"Please map all required fields: {', '.join(missing_mappings)}")
                return None
            
            # Show mapped preview
            st.subheader("🔄 Mapped Data Preview")
            reverse_mapping = {v: k for k, v in column_mapping.items()}
            preview_df = df[list(reverse_mapping.keys())].rename(columns=reverse_mapping)
            st.dataframe(preview_df.head(), use_container_width=True)
            
            # Upload options
            st.subheader("⚙️ Upload Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                operation = st.radio(
                    "Choose operation:",
                    options=["replace", "append"],
                    format_func=lambda x: "Replace existing data" if x == "replace" else "Add to existing data"
                )
            
            with col2:
                save_file = st.checkbox(
                    "Save CSV to data folder",
                    value=True,
                    help="Save the uploaded file to the project's data folder"
                )
            
            # Upload button
            if st.button("🚀 Upload Data", type="primary", use_container_width=True):
                with st.spinner("Processing upload..."):
                    # Save file if requested
                    if save_file:
                        project_root = Path(__file__).parent.parent.parent
                        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                        target_path = project_root / "data" / f"uploaded_{timestamp}_{uploaded_file.name}"
                        
                        if self.save_uploaded_file(uploaded_file, str(target_path)):
                            st.success(f"File saved to: {target_path}")
                    
                    # Update database
                    success, message = self.update_database_with_new_data(
                        df, reverse_mapping, operation
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        
                        # Update session to trigger refresh
                        self.session_manager.update_session_state('data_updated', True)
                        self.session_manager.update_session_state('last_upload', pd.Timestamp.now())
                        
                        # Show next steps
                        st.info("💡 **Next Steps:** The AI system will use your new data for analysis. You may need to refresh the page to see schema updates.")
                        
                        return {
                            'success': True,
                            'operation': operation,
                            'rows': len(df),
                            'file_saved': save_file,
                            'timestamp': pd.Timestamp.now()
                        }
                    else:
                        st.error(f"❌ {message}")
                        return None
        
        return None
