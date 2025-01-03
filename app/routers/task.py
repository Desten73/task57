from fastapi import APIRouter, Depends, status, Path, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get("/task_id")
async def task_by_id(db: Annotated[Session, Depends(get_db)],
                     task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task:
        return task
    else:
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "transaction": "Not found"
        }


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], create: CreateTask, user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "transaction": "User was not found"
        }
    db.execute(insert(Task).values(title=create.title,
                                   content=create.content,
                                   priority=create.priority,
                                   user_id=user_id,
                                   slug=slugify(create.title)))
    db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


@router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int,
                      update_us: UpdateTask):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "transaction": "Not found"
        }
    db.execute(update(Task).where(Task.id == task_id).values(
        title=update_us.title,
        content=update_us.content,
        priority=update_us.priority
    ))
    db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Task update is successful"
    }


@router.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no task found")
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Task delete is successful"
    }
