from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
import hashlib

# Import from modules
from app.database import get_db, engine, SessionLocal
from app.models import Base, User, Category, Task
from app import schemas

# Create tables
Base.metadata.create_all(bind=engine)

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
security = HTTPBearer()

app = FastAPI(
    title="Task Management API",
    description="A simplified Trello/Asana-like REST API",
    version="1.0.0"
)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: str = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/")
def root():
    return {"message": "Task Management API"}

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        print(f" Registering: {user.email}")
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # hashing
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        print(f" Password hashed: {hashed_password[:20]}...")
        
        # Create user
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f" User created: {db_user.id}")
        return {
            "email": db_user.email,
            "id": db_user.id,
            "created_at": db_user.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        print(f" Login attempt: {user.email}")
        
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        test_hash = hashlib.sha256(user.password.encode()).hexdigest()
        if test_hash != db_user.hashed_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create JWT token
        access_token = create_access_token(data={"sub": db_user.email})
        print(f" Login successful: {db_user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "email": db_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# Protected endpoints
@app.post("/categories")
def create_category(
    category: schemas.CategoryCreate,  
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        db_category = Category(name=category.name, user_id=current_user.id)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return {"id": db_category.id, "name": db_category.name, "user_id": db_category.user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return [{"id": cat.id, "name": cat.name} for cat in categories]

@app.post("/tasks")
def create_task(
    task: schemas.TaskCreate,  
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"Creating task: {task.title}")
        db_task = Task(
            title=task.title,
            description=task.description,
            status=task.status,
            category_id=task.category_id,
            user_id=current_user.id
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return {
            "id": db_task.id,
            "title": db_task.title,
            "description": db_task.description,
            "status": db_task.status,
            "category_id": db_task.category_id,
            "user_id": db_task.user_id
        }
    except Exception as e:
        print(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
def list_tasks(
    status: str = None,
    category_id: int = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    if category_id:
        query = query.filter(Task.category_id == category_id)
    
    tasks = query.all()
    return [{
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "category_id": task.category_id
    } for task in tasks]

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "category_id": task.category_id
    }

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,  
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.category_id is not None:
        task.category_id = task_update.category_id
        
    db.commit()
    return {
        "message": "Task updated", 
        "task_id": task.id,
        "title": task.title,
        "status": task.status
    }


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)