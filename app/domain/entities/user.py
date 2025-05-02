from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    user_id: UUID
    user_name: str


class UserWithCreds(User):
    hash_password: str
