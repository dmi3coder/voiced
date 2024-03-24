from pydantic import BaseModel

#  In real application we shouldn't store password in plain text, or even better use Oauth2(e.g Firebase SaaS)
class UserCreateDto(BaseModel):
    username: str
    email: str
    password: str

class UserDto(BaseModel):
    username: str
    password: str
