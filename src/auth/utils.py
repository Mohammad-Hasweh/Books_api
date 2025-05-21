from datetime import datetime,timedelta

import jwt
from passlib.context import CryptContext
from src.config import Config

import logging
import uuid

passwd_context=CryptContext(
    schemes=['bcrypt']
)

REFRESH_TOKEN_EXPIRY=3600

def generate_password_hash(password:str) -> str:
    hash=passwd_context.hash(password)
    return hash

def verify_password(password:str,hash:str) -> bool:
    return passwd_context.verify(password,hash)



def create_acess_token(user_data:dict,expiry:timedelta=None,refresh:bool=False) -> str:
    payload={}
    
    payload['user']=user_data
    payload['exp']=datetime.now()+(expiry if expiry is not None else timedelta(seconds=REFRESH_TOKEN_EXPIRY))
    payload['jti']=str(uuid.uuid4())
    payload['refresh']=refresh  # mark a token as a refresh token or not.
    


    token=jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )

    return token

def decode_token(token: str)-> dict :
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,  
            algorithms=[Config.JWT_ALGORITHM])

        return token_data
    except  jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    
    #This ensures that any errors encountered while decoding the token are captured and logged, helping with debugging and preventing the application from crashing due to unhandled exceptions.
    except Exception as e:
        logging.exception(e)
        return None