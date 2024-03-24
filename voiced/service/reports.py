from celery import Celery

from voiced.db import SessionLocal
from voiced.model import User, followers_association

celery = Celery('voiced', broker='memory://')
celery.conf.task_always_eager = True

from celery.schedules import crontab
from celery.task import periodic_task
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


def run_async(task_func):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # If there's no existing event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(task_func)


@periodic_task(run_every=(crontab(minute='*/1')), name="print_user_follow_stats")
def print_user_follow_stats():
    run_async(async_print_user_follow_stats())


async def async_print_user_follow_stats():
    async with SessionLocal() as db:
        result = await db.execute(select(User).options(selectinload(User.followed)))
        users = result.scalars().all()
        for user in users:
            following_nicknames = [followed_user.username for followed_user in user.followed]
            followers = await get_user_following_usernames(db, user.id)
            print(f"User: {user.username}, Following {len(user.followed)} users: {following_nicknames}."
                  f" Followers: {len(followers)} users: {followers}")



async def get_user_following_usernames(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User.username).join(
            followers_association, followers_association.c.follower_id == User.id
        ).where(followers_association.c.followed_id == user_id)
    )
    following_usernames = result.scalars().all()
    return following_usernames
