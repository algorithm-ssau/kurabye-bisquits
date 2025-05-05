from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.config import auth_settings, log_setting
from domain.entities.user import User, UserWithCreds
from schemas.token import TokenResponseSchema
from schemas.user import UserAuthSchema, UserCreateSchema
from utils.auth import create_jwt, hash_password, verify_password

SECRET_KEY = auth_settings.secret_key
ALGORITHM = auth_settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = auth_settings.access_token_expire_minutes

log = log_setting.get_configure_logging(filename=__name__)


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
async def get_user(user_name: str) -> UserAuthSchema | None:
    if user_name in fake_users_db:
        return UserAuthSchema(**fake_users_db[user_name])
    return None


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO: add rate limiting
    user = await get_user(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # create user model

    user_without_password = User(**user.model_dump())
    access_token = create_jwt(user_without_password)
    log.info("User %s successfully get JWT.", user.user_id)
    return TokenResponseSchema(access_token=access_token, token_type="bearer")


@router.post("/registration", response_model=TokenResponseSchema)
async def add_user(user_in: UserCreateSchema):
    try:
        # TODO: Check that not user with this login/email/phone/etc.
        user = UserWithCreds(
            user_id=uuid4(),
            user_name=user_in.user_name,
            hash_password=hash_password(user_in.password),
        )
        # TODO: add user to db

        # Authorize user
        user_without_password = User(**user.model_dump())
        access_token = create_jwt(user_without_password)
        log.info("User %s successfully registered and gets JWT.", user.user_id)
        return TokenResponseSchema(access_token=access_token, token_type="bearer")
    except ValueError as error:
        return HTTPException(detail=error, status_code=403)


@router.get("/protected")
async def protected(protected=Depends(oauth2_scheme)):
    return "hello!"
