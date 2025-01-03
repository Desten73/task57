from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get("/user_id")
async def user_by_id(db: Annotated[Session, Depends(get_db)],
                     user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        return user
    else:
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "transaction": "Not found"
        }


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)], create: CreateUser):
    db.execute(insert(User).values(username=create.username,
                                   firstname=create.firstname,
                                   lastname=create.lastname,
                                   age=create.age,
                                   slug=slugify(create.username)))
    db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)],
                      user_id: int,
                      update_us: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "transaction": "Not found"
        }
    db.execute(update(User).where(User.id == user_id).values(
        firstname=update_us.firstname,
        lastname=update_us.lastname,
        age=update_us.age
    ))
    db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "User update is successful"
    }


@router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)],
                      user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no user found")
    db.execute(delete(User).where(User.id == user_id))
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "User delete is successful"
    }


@router.get("/user_id/tasks")
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)],
                           user_id: int):
    tasks = db.scalars(select(Task).where(Task.user_id == user_id))
    if tasks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no tasks found")
    return tasks.all()
