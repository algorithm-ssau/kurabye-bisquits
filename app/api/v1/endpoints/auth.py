from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.config import auth_settings, log_setting
from domain.entities.user import CreateUser, User, UserWithCreds
from repository.abstractRepositroies import AbstractUserRepository
from repository.user_repository import get_user_repo
from schemas.token import TokenResponseSchema
from schemas.user import UserAuthSchema, UserCreateSchema
from services.abstractServices import AbstractCartService
from services.cartService import get_cart_service
from utils.auth import create_jwt, hash_password, verify_password

SECRET_KEY = auth_settings.secret_key
ALGORITHM = auth_settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = auth_settings.access_token_expire_minutes

log = log_setting.get_configure_logging(filename=__name__)


router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

fake_users_db = {
    "johndoe": {
        "user_id": 1,
        "user_name": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$WAoK9tsSsUmLD2RF6smKt.4w9CfRRXE2WsztXzRBlgATIsQTKe.F.",
    }
}


# get user data
async def get_user(
    user_name: str,
    user_repo: AbstractUserRepository = Depends(get_user_repo),
) -> UserAuthSchema | None:
    user = await user_repo.get_user(user_login=user_name)
    return UserAuthSchema(**user.model_dump()) if user else None


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: AbstractUserRepository = Depends(get_user_repo),
):
    # TODO: add rate limiting
    user = await user_repo.get_user_creds(user_login=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # create user model

    user_without_password = User(**user.model_dump())
    access_token = create_jwt(user_without_password)
    log.info("User %s successfully get JWT.", user.user_id)
    return TokenResponseSchema(access_token=access_token, token_type="bearer")


@router.post("/registration", response_model=TokenResponseSchema)
async def add_user(
    user_in: UserCreateSchema = Body(),
    user_repo: AbstractUserRepository = Depends(get_user_repo),
):
    try:
        user = CreateUser(
            login=user_in.login,
            last_name=user_in.last_name,
            name=user_in.name,
            phone=user_in.phone,
            role_id=user_in.role_id,
            password=hash_password(user_in.password),
        )
        user_add = await user_repo.add_user(user_data=user)

        if not user_add:
            raise HTTPException(detail="Пользователь с таким логином уже существует", status_code=400)

        # Authorize user
        user_without_password = user_add
        access_token = create_jwt(user_without_password)
        return TokenResponseSchema(access_token=access_token, token_type="bearer")
    except ValueError as error:
        return HTTPException(detail=error, status_code=403)


@router.get("/protected")
async def protected(protected=Depends(oauth2_scheme)):
    return "hello!"


@router.get("/get_user")
async def get_userr(user_login: str, user_repo: AbstractUserRepository = Depends(get_user_repo)):
    return await user_repo.get_user(user_login)
