from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import DEFAULT_USER_ID
from app.database import get_db
from app.models.models import Task
from app.schemas.schemas import TaskOut

router = APIRouter(prefix="/api/tasks", tags=["task"])

USER_ID = DEFAULT_USER_ID


@router.get("/daily", response_model=List[TaskOut])
def get_daily_tasks(
    target_date: Optional[date] = Query(alias="date", default=None),
    db: Session = Depends(get_db),
):
    target_date = target_date if target_date is not None else date.today()
    tasks = (
        db.query(Task)
        .filter(Task.user_id == USER_ID, Task.scheduled_date == target_date)
        .order_by(Task.id.asc())
        .all()
    )
    return tasks


@router.put("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == USER_ID).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    task.completed = True
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == USER_ID).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
    return {"detail": "删除成功"}
