from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.config import auth_settings
from schemas.token import Token
from schemas.user import User, UserAuth
from utils.auth import create_jwt, verify_password

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


# get user data
async def get_user(user_name: str) -> UserAuth | None:
    if user_name in fake_users_db:
        return UserAuth(**fake_users_db[user_name])
    return None


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    user = await get_user(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user_without_password = User(**user.model_dump())
    access_token = create_jwt(user_without_password)
    return Token(access_token=access_token, token_type="bearer")


# registration:
# -> 1. Get user credentionals.
# -> 2. Check that not user with this login/email/phone/etc.
# -> 3. Make sure that password is complex enough.
# -> 4. Save user creds in the DB (with hashed password).
# -> 5. Autorize user with this creds.


@router.get("/protected")
async def protected(protected=Depends(oauth2_scheme)):
    return "hello!"
