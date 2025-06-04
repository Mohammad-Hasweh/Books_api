from pydantic_settings import BaseSettings,SettingsConfigDict


# these will be applied to all the pydantic models
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET:str
    JWT_ALGORITHM:str

    REDIS_URL: str = "redis://localhost:6379/0"

    MAIL_USERNAME:str
    MAIL_PASSWORD:str
    MAIL_FROM:str
    MAIL_SERVER:str
    MAIL_FROM_NAME:str
    MAIL_PORT:int
    MAIL_STARTTLS:bool=True
    MAIL_SSL_TLS:bool=False
    USE_CREDENTIALS:bool=True
    VALIDATE_CERTS:bool=True

    URL_VERIFY_SECRET:str

    DOMAIN:str


    
    #help us to find where our env file is located
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    #extra argument and given it a value of ignore as we may want to ignore any extra attributes provided within our Settings class.
    
Config=Settings()


