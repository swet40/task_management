import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import Base

def test_database():
    print(" Testing database connection...")
    
    try:
        # Test if we can create tables
        Base.metadata.create_all(bind=engine)
        print(" Database tables created successfully")
        
        # Test if we can open a session
        with SessionLocal() as db:
            result = db.execute("SELECT 1")
            print(" Database connection successful")
            print(f" SQLite version: {db.bind.dialect.server_version_info}")
            
        return True
        
    except Exception as e:
        print(f" Database error: {e}")
        return False

if __name__ == "__main__":
    test_database()