from fastapi import Depends
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.postgres import db_helper
from domain.entities.user import CreateUser, User, UserWithCreds
from repository.abstractRepositroies import AbstractUserRepository
from repository.sql.cartQueries import CREATE_CART
from repository.sql.user_queries import CREATE_USER, SELECT_USER, SELECT_USER_CREDS


class UserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.__session: AsyncSession = session

    async def get_user(self, user_login: str) -> User | None:
        async with self.__session as session:
            user_db = await session.execute(SELECT_USER, params={"user": user_login})

            user_db = user_db.mappings().fetchone()
            if user_db:
                return User(**user_db)

    async def get_user_creds(self, user_login: str) -> UserWithCreds | None:
        async with self.__session as session:
            user_db = await session.execute(SELECT_USER_CREDS, params={"user": user_login})
            user_db = user_db.mappings().fetchone()

            if user_db:
                user = UserWithCreds(**user_db)
                return user
            return None

    async def add_user(self, user_data: CreateUser) -> User | None:
        async with self.__session as session:
            try:
                user = await session.execute(
                    CREATE_USER,
                    params={
                        "login": user_data.login,
                        "password": user_data.password,
                        "name": user_data.name,
                        "surname": user_data.last_name,
                        "phone": user_data.phone,
                        "role_id": user_data.role_id,
                    },
                )

                user = user.mappings().fetchone()
                if user:
                    # TODO: Refmat this code
                    # ==========================
                    # Add cart
                    await session.execute(CREATE_CART, params={"cart_id": user["user_id"]})
                    # ==========================
                    await session.commit()
                    return User(last_name=user["surname"], **user)

                return None
            except DBAPIError:
                return None


def get_user_repo(session: AsyncSession = Depends(db_helper.get_session_dependency)) -> AbstractUserRepository:
    return UserRepository(session=session)
