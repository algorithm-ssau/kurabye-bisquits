from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    login: str
    name: str
    last_name: str
    phone: str
    role_id: int


class UserWithCreds(User):
    password: str


class CreateUser(BaseModel):
    login: str
    name: str
    last_name: str
    phone: str
    role_id: int
    password: str
