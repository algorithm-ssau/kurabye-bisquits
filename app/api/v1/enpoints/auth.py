from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from core.config import auth_settings

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = auth_settings.secret_key
ALGORITHM = auth_settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = auth_settings.access_token_expire_minutes

DEFAULT_EXPIRE_MINUTES = 15

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

fake_users_db = {
    "johndoe": {
        "user_id": "8fec36b8-7bd7-417d-833a-932cb7a47445",
        "user_name": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$WAoK9tsSsUmLD2RF6smKt.4w9CfRRXE2WsztXzRBlgATIsQTKe.F.",
    }
}


class User(BaseModel):
    user_id: UUID
    user_name: str


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_name: str


# get user credentials
# get user data
async def get_user(user_name: str) -> UserInDB | None:
    if user_name in fake_users_db:
        return UserInDB(**fake_users_db[user_name])
    return None


# check user password
# -> 1. Get hash method
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -> 2. Hash password
def hash_password(password: str):
    return pwd_context.hash(password)


# -> 3. Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# generate JWT
# -> 1. Create new JWT
def create_jwt(user_data: User, expires_delta: timedelta = timedelta(minutes=DEFAULT_EXPIRE_MINUTES)):
    to_encode = user_data.dict()
    expire = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire
    # ==============================
    # uuid is not json serializable
    to_encode["user_id"] = str(user_data.user_id)
    # ==============================
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    user = await get_user(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_jwt(user)
    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name = payload.get("sub")
        if user_name is None:
            raise credentials_exception
        token_data = TokenData(user_name=user_name)
    except InvalidTokenError:
        raise credentials_exception from InvalidTokenError
    user = get_user(user_name=token_data.user_name)
    if user is None:
        raise credentials_exception
    return user


@router.get("/me")
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("Hello world!")
async def hello_world():
    return "hello world!"
