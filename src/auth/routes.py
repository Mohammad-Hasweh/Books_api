from fastapi import APIRouter, Depends, status,BackgroundTasks
from .schemas import UserModel, UserCreateModel,UserLoginModel,UserBooksModel,EmailModel,PasswordResetConfirmModel,PasswordResetRequestModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from src.db.main import get_session
from .utils import (create_acess_token,verify_password,create_url_safe_token,decode_url_safe_token,generate_password_hash)
from fastapi.responses import JSONResponse
from datetime import timedelta,datetime
from .dependencies import RefreshTokenBearer,AccessTokenBearer,RoleChecker,get_current_user
from src.db.redis import add_jti_to_blocklist
from src.errors import InvalidCredentials,UserAlreadyExists,UserNotFound

from src.celery_tasks import send_email


from src.config import Config


auth_router = APIRouter()
user_service = UserService()
role_checker=RoleChecker(["admin","user"])

REFRESH_TOKEN_EXPIRY=2

@auth_router.post(
    "/signup",status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel,bg_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()
    
    new_user = await user_service.create_user(user_data, session)

    token=create_url_safe_token(data={"email":email})
    
    link=f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    
    subject="Verify your email"
    recipients=[email]

    send_email.delay(recipients, subject, html)

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token:str,session:AsyncSession=Depends(get_session)):

    token_data=decode_url_safe_token(token)
    user_email=token_data.get("email")

    if user_email:
        user= await user_service.get_user_by_email(email=user_email,session=session)

        if not user:
            raise UserNotFound
        
        await user_service.update_user(user,{"is_verified":True},session)

        return JSONResponse(
            content={"message":"Account verified successfully"},status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@auth_router.post("/login")
async def login_users(
    login_data:UserLoginModel,
    session:AsyncSession=Depends(get_session)
):
    email=login_data.email
    password=login_data.password

    user=await user_service.get_user_by_email(email,session)
    if user is not None:

        #data_dict = user.model_dump()

        password_valid=verify_password(password,user.password_hash)

        if password_valid:
            acess_token=create_acess_token(
                user_data={"email":user.email,"user_uid":str(user.uid),"role":user.role})
            
            refresh_token=create_acess_token(user_data={"email":user.email,"user_uid":str(user.uid)},refresh=True,
                                             expiry=timedelta(days=REFRESH_TOKEN_EXPIRY))
        return JSONResponse(
            content={
                "message":"Login succesful" ,
                "acess_token":acess_token,
                "refresh_token":refresh_token,
                "user":{
                    "email":user.email,
                    "user_uid":str(user.uid)
                }
            }
        )
    raise InvalidCredentials()

@auth_router.get("/refresh_token")
async def get_new_acess_token(token_details:dict=Depends(RefreshTokenBearer())):
    expiry_timestamp=token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp)> datetime.now():
        new_acess_token=create_acess_token(user_data=token_details["user"])

        return JSONResponse(content={"acess_token":new_acess_token})
        
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST
    )



@auth_router.get('/logout')
async def revoke_token(token_details:dict=Depends(AccessTokenBearer())):

    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message":"Logged Out Successfully"
        },
        status_code=status.HTTP_200_OK
    )


@auth_router.get('/me',response_model=UserBooksModel)
async def get_current_user(user=Depends(get_current_user),_:bool=Depends(role_checker)):
    return user


@auth_router.post("/send_mail")
async def send_mail(emails:EmailModel):
    recipients=emails.addresses
    
    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    send_email.delay(recipients, subject, html)
    

    return {"message":"Email sent successfully"}

@auth_router.post("/password-reset")
async def password_reset(data:PasswordResetRequestModel):
    email=data.email

    token=create_url_safe_token({"email":email})

    link=f"http://{Config.DOMAIN}/api/v1/auth/password-reset/{token}"

    html = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"
    recipients=[email]
    
    send_email.delay(recipients, subject, html)

    return JSONResponse(
            content={
                "message": "Please check your email for instructions to reset your password",
            },
            status_code=status.HTTP_200_OK,
        )

@auth_router.post("/password-reset/{token}")
async def reset_password(token:str,passwords:PasswordResetConfirmModel,session:AsyncSession=Depends(get_session)):
    new_password=passwords.new_password
    confirm_password=passwords.confirm_new_password

    if new_password!=confirm_password:
        raise HTTPException(
            detail="Passwords do not match",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    token_data=decode_url_safe_token(token)

    user_email=token_data.get("email")

    if user_email:
        user =await user_service.get_user_by_email(email=user_email,session=session)

        if not user:
            raise UserNotFound
        
        password_hash=generate_password_hash(new_password)
        
        await user_service.update_user(user=user,user_data={"password_hash":password_hash},session=session)

        return JSONResponse(
            content={"message":"password reset successfully"},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message":"Error occured during password reset"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )