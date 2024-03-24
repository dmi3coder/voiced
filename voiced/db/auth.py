from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
