#!/usr/bin/env python3
import subprocess
import sys

def install_requirements():
    """Install all required packages"""
    packages = [
        "fastapi",
        "uvicorn[standard]", 
        "sqlalchemy",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "pytest",
        "httpx",
        "email-validator"
    ]
    
    print("Installing required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
    
    print("\nAll packages installed!")

def test_imports():
    """Test if all imports work"""
    print("\nTesting imports...")
    try:
        from app.main import app
        from app import models, schemas, auth, crud, database
        print("✓ All imports successful!")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    install_requirements()
    if test_imports():
        print("\n Setup completed successfully!")
        print("\nTo run the server:")
        print("  uvicorn app.main:app --reload")
        print("\nTo run tests:")
        print("  pytest")
    else:
        print("\n Setup failed. Please check the errors above.")