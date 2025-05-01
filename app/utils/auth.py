from datetime import datetime, timedelta

from jwt import encode as jwt_encode
from passlib.context import CryptContext

from core.config import auth_settings
from schemas.user import User

SECRET_KEY = auth_settings.secret_key
ALGORITHM = auth_settings.algorithm
DEFAULT_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(user_data: User, expires_delta: timedelta = timedelta(minutes=DEFAULT_EXPIRE_MINUTES)):
    to_encode = user_data.dict()
    expire = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire
    # ==============================
    # uuid is not json serializable
    to_encode["user_id"] = str(user_data.user_id)
    # ==============================
    encoded_jwt = jwt_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
