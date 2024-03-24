from alembic.config import Config
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT

import voiced.controller.auth as auth_controller
import voiced.controller.follow as follow_controller
from alembic import command
from voiced.db.auth import Settings

app = FastAPI(debug=True)


def run_alembic_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@app.on_event("startup")
async def startup_event():
    run_alembic_migrations()


@AuthJWT.load_config
def get_config():
    return Settings()


app.include_router(auth_controller.router)
app.include_router(follow_controller.router)
