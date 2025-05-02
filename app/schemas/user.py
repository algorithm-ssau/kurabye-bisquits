from string import punctuation
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator


class UserResponseSchema(BaseModel):
    user_id: UUID
    user_name: str = Field(min_length=1, max_length=255)


class UserCreateSchema(BaseModel):
    user_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)

    @field_validator("user_name")
    @classmethod
    def check_user_name(cls, user_name, chars=punctuation) -> str:
        # spaces also coulndn't be in the user_name
        chars = chars + " " if " " not in chars else chars
        if any(char in user_name for char in chars):
            raise ValueError("'You can't use specific symbols or spaces in the your nickname")
        if not any(char.isalpha() for char in user_name):
            raise ValueError("Your nickname must contains at least one alpha character")
        return user_name

    @field_validator("password")
    @classmethod
    def check_password_complexity(cls, password, requires_chars=punctuation) -> str:
        if not any(char in password for char in requires_chars):
            raise ValueError(
                f"Your password must contains at least one specifick symbol. Specific symbols: {punctuation}"
            )
        return password


class UserAuthSchema(UserResponseSchema):
    hashed_password: str = Field(exclude=True, repr=False)
