import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get the URL
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("❌ ERROR: DATABASE_URL not found in .env file.")
else:
    print(f"Attempting to connect to: {db_url.split('@')[-1]}") # Prints host only for safety
    
    try:
        # Create engine and attempt connection
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row is not None and row[0] == 1:
                print("✅ SUCCESS: Successfully connected to your Azure PostgreSQL database!")
            else:
                print("❌ CONNECTION FAILED!")
    except Exception as e:
        print("❌ CONNECTION FAILED!")
        print(f"Error Details: {e}")
