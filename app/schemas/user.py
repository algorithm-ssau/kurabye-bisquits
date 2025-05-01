from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    user_name: str = Field(min_length=1, max_length=255)


class UserAuth(User):
    hashed_password: str = Field(exclude=True, repr=False)
