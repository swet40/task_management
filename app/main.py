from jose import JWTError, jwt
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
security = HTTPBearer()

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

# Update login to return JWT token
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
from app.models import Category, Task

@app.post("/categories")
def create_category(name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        category = Category(name=name, user_id=current_user.id)
        db.add(category)
        db.commit()
        db.refresh(category)
        return {"id": category.id, "name": category.name, "user_id": category.user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return [{"id": cat.id, "name": cat.name} for cat in categories]

@app.post("/tasks")
def create_task(
    title: str, 
    description: str = None, 
    status: str = "pending",
    category_id: int = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        task = Task(
            title=title,
            description=description,
            status=status,
            category_id=category_id,
            user_id=current_user.id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "user_id": task.user_id
        }
    except Exception as e:
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
    return task

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    title: str = None,
    status: str = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if title:
        task.title = title
    if status:
        task.status = status
        
    db.commit()
    return {"message": "Task updated", "task_id": task.id}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}