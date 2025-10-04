from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import hashlib  # Add this import

from . import models, schemas

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    try:
        print(f" Creating user: {user.email}")
        
        # MINIMAL HASHING - This cannot fail
        import hashlib
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        print(f" Password hashed: {hashed_password[:20]}...")
        
        # Create user
        db_user = models.User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f" User created: {db_user.id}")
        return db_user
        
    except Exception as e:
        print(f" Error in create_user: {str(e)}")
        db.rollback()
        raise

# ... rest of your crud functions remain the same
def create_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(**category.dict(), user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session, user_id: int):
    return db.query(models.Category).filter(models.Category.user_id == user_id).all()

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, user_id: int, status: Optional[str] = None,
            category_id: Optional[int] = None, due_date: Optional[datetime] = None):
    query = db.query(models.Task).filter(models.Task.user_id == user_id)
    
    if status:
        query = query.filter(models.Task.status == status)
    if category_id:
        query = query.filter(models.Task.category_id == category_id)
    if due_date:
        query = query.filter(models.Task.due_date == due_date)
    
    return query.all()

def get_task(db: Session, task_id: int, user_id: int):
    return db.query(models.Task).filter(
        models.Task.id == task_id, 
        models.Task.user_id == user_id
    ).first()

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if db_task:
        update_data = task.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False