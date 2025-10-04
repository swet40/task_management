from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import models, schemas, auth, crud
from .database import SessionLocal, engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="A simplified Trello/Asana-like REST API",
    version="1.0.0"
)

# Authentication endpoints
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        print(f" Registration attempt for: {user.email}")
        
        # Check if user exists
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            print(" Email already registered")
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
        print(" Email is available, creating user...")
        
        # Create user
        new_user = crud.create_user(db=db, user=user)
        print(f" User created successfully: {new_user.email}")
        
        return new_user
        
    except Exception as e:
        print(f" Registration error: {str(e)}")
        print(f" Error type: {type(e).__name__}")
        import traceback
        print(f" Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    print(f" Login attempt for: {user.email}")
    
    authenticated_user = auth.authenticate_user(db, user.email, user.password)
    if not authenticated_user:
        print(" Login failed: Invalid credentials")
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    print(f" Login successful for: {authenticated_user.email}")
    access_token = auth.create_access_token(data={"sub": authenticated_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Category endpoints
@app.post("/categories", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_category(db=db, category=category, user_id=current_user.id)

@app.get("/categories", response_model=List[schemas.Category])
def list_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_categories(db=db, user_id=current_user.id)

# Task endpoints
@app.post("/tasks", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_task(db=db, task=task, user_id=current_user.id)

@app.get("/tasks", response_model=List[schemas.Task])
def list_tasks(
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    due_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Parse due_date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    return crud.get_tasks(
        db=db, 
        user_id=current_user.id,
        status=status,
        category_id=category_id,
        due_date=parsed_due_date
    )

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    task = crud.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    updated_task = crud.update_task(db=db, task_id=task_id, task=task, user_id=current_user.id)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    success = crud.delete_task(db=db, task_id=task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

@app.get("/")
def read_root():
    return {"message": "Task Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)