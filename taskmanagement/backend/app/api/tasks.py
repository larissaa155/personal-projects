from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Task).options(
        joinedload(Task.created_by),
        joinedload(Task.assigned_to)
    )
    
    #Filter by user role/team
    if current_user.role.value in ["member"]:
        query = query.filter(
            (Task.created_by_id == current_user.id) | 
            (Task.assigned_to_id == current_user.id)
        )
    
    if status:
        query = query.filter(Task.status == status)
    
    if assigned_to:
        query = query.filter(Task.assigned_to_id == assigned_to)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_task = Task(
        **task_data.dict(),
        created_by_id=current_user.id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    #Load relationships for response
    task = db.query(Task).options(
        joinedload(Task.created_by),
        joinedload(Task.assigned_to)
    ).filter(Task.id == new_task.id).first()
    
    return task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).options(
        joinedload(Task.created_by),
        joinedload(Task.assigned_to)
    ).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    #Check permissions
    if current_user.role.value == "member" and \
       task.created_by_id != current_user.id and \
       task.assigned_to_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    #Check permissions
    if current_user.role.value == "member" and task.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    #Update fields
    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    #If task is marked as done
    if task_data.status == TaskStatus.DONE and task.completed_at is None:
        task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    #Load relationships
    task = db.query(Task).options(
        joinedload(Task.created_by),
        joinedload(Task.assigned_to)
    ).filter(Task.id == task_id).first()
    
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    #Check permissions (only admin or creator can delete)
    if current_user.role.value not in ["admin", "manager"] and \
       task.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(task)
    db.commit()

@router.post("/{task_id}/assign/{user_id}")
async def assign_task(
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #Check if current user can assign tasks
    if current_user.role.value not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    task.assigned_to_id = user_id
    db.commit()
    
    return {"message": "Task assigned successfully"}