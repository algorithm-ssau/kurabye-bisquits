from string import punctuation

from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator


class UserResponseSchema(BaseModel):
    user_id: int
    login: str
    name: str
    last_name: str
    phone: str
    role_id: int


class UserCreateSchema(BaseModel):
    login: str
    name: str
    last_name: str
    phone: str
    password: str
    role_id: int

    @field_validator("name")
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
    password: str = Field(exclude=True, repr=False)
