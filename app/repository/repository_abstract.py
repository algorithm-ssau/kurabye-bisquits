from abc import ABC, abstractmethod

from app.schemas.user import UserResponseSchema


class AbstractUserRepository(ABC):
    @abstractmethod
    def create_user(self, user: UserResponseSchema):
        pass
