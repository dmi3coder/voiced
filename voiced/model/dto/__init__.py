import re

from pydantic import BaseModel, EmailStr, constr, validator


#  In real application we shouldn't store password in plain text, or even better use Oauth2(e.g Firebase SaaS)
class UserCreateDto(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8, max_length=100)

    @validator('username')
    def username_alphanumeric(cls, v):
        assert re.match('^[a-zA-Z0-9_]*$', v), 'Username must be alphanumeric'
        return v

    @validator('password')
    def password_strength(cls, v):
        assert re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,100}$',
                        v), 'Password must be strong'
        return v


class UserDto(BaseModel):
    username: str
    password: str
