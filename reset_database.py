import os
import sys

sys.path.append(os.path.dirname(__file__))
from app.database import engine
from app.models import Base

def reset_database():

    if os.path.exists("task_manager.db"):
        os.remove("task_manager.db")
        print(" Old database removed")

    Base.metadata.create_all(bind=engine)
    print(" New database created with all tables")
    
    print(" Database has been reset. Please restart your server.")

if __name__ == "__main__":
    reset_database()