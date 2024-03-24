from fastapi import APIRouter
from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from voiced.db import get_db
from voiced.model import User, followers_association

router = APIRouter()


@router.get('/me/details')
async def user(Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()

    # Asynchronously fetching the user
    result = await db.execute(select(User).options(selectinload(User.followed)).where(User.username == current_user))
    db_user = result.scalars().first()

    followers_usernames = await get_user_following_usernames(db, db_user.id)

    # The following line assumes that 'followed' is a relationship loaded eagerly
    # If it's lazy-loaded, additional async queries might be required
    return {
        "following_count": len(db_user.followed),
        "following": [user.username for user in db_user.followed],
        "followers_count": len(followers_usernames),
        "followers": followers_usernames
    }


async def get_user_following_usernames(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User.username).join(
            followers_association, followers_association.c.follower_id == User.id
        ).where(followers_association.c.followed_id == user_id)
    )
    following_usernames = result.scalars().all()
    return following_usernames


@router.post('/user/{username}/follow')
async def follow(username: str, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()

    result = await db.execute(select(User).options(selectinload(User.followed)).where(User.username == current_user))
    db_user = result.scalars().first()

    if db_user is None:
        raise HTTPException(status_code=500, detail="Current user is not found")

    result_to_follow = await db.execute(select(User).where(User.username == username))
    user_to_follow = result_to_follow.scalars().first()

    if user_to_follow is None:
        raise HTTPException(status_code=404, detail="User to follow not found")

    # Perform follow operation
    if user_to_follow in db_user.followed:
        raise HTTPException(status_code=400, detail="Already following this user")

    db_user.followed.append(user_to_follow)
    await db.commit()
    await db.refresh(db_user)

    return [user.username for user in db_user.followed]


@router.delete('/user/{username}/unfollow')
async def unfollow(username: str, Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()

    result = await db.execute(select(User).options(selectinload(User.followed)).where(User.username == current_user))
    db_user = result.scalars().first()

    if db_user is None:
        raise HTTPException(status_code=500, detail="Current user is not found")

    result_to_unfollow = await db.execute(select(User).where(User.username == username))
    user_to_unfollow = result_to_unfollow.scalars().first()

    if user_to_unfollow is None:
        raise HTTPException(status_code=404, detail="User to unfollow not found")

    if user_to_unfollow in db_user.followed:
        db_user.followed.remove(user_to_unfollow)
        await db.commit()
        await db.refresh(db_user)

    return [user.username for user in db_user.followed]
