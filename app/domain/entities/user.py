from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    user_name: str


class UserWithCreds(User):
    hash_password: str
