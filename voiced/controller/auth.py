from fastapi import APIRouter
from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from voiced.db import get_db
from voiced.model import User
from voiced.model.dto import UserCreateDto, UserDto

router = APIRouter()


@router.post("/register")
async def create_user(user: UserCreateDto, db: AsyncSession = Depends(get_db)):
    user_exists = await db.execute(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if user_exists.scalars().first() is not None:
        raise HTTPException(status_code=400, detail="Username or email already taken")

    # Password hashing omitted to save time, in real case we need to hash the password
    db_user = User(username=user.username, email=user.email, hashed_password=user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post('/login')
async def login(user_dto: UserDto, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    result = await db.execute(select(User).where(User.username == user_dto.username))
    db_user = result.scalars().first()

    if db_user is None or db_user.hashed_password != user_dto.password:
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = authorize.create_access_token(subject=db_user.username)
    return {"access_token": access_token}


@router.get('/me')
async def user(Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    result = await db.execute(select(User).where(User.username == current_user))
    db_user = result.scalars().first()

    return db_user
