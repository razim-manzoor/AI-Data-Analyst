import pandas as pd
from sqlalchemy import create_engine
import os
from src.config import DB_FILE, CSV_FILE

def create_db_from_csv():
    """
    Creates a SQLite database from a CSV file.
    """
    if os.path.exists(DB_FILE):
        print(f"Database '{DB_FILE}' already exists. Deleting and recreating.")
        os.remove(DB_FILE)
        
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    print(f"Reading data from '{CSV_FILE}'...")
    df = pd.read_csv(CSV_FILE)
    
    print(f"Creating database engine for '{DB_FILE}'...")
    engine = create_engine(f"sqlite:///{DB_FILE}")
    
    print("Writing data to 'sales' table...")
    df.to_sql("sales", engine, index=False)
    
    print("Database creation complete.")
    return engine

if __name__ == "__main__":
    # To run this script, you must be in the root directory of the project
    # and execute it as a module: python -m src.create_database
    create_db_from_csv()
    print(f"Database '{DB_FILE}' created successfully from '{CSV_FILE}'.")
