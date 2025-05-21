from pydantic_settings import BaseSettings,SettingsConfigDict


# these will be applied to all the pydantic models
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET:str
    JWT_ALGORITHM:str
    REDIS_HOST:str="localhost"
    REDIS_PORT:int=6379
    
    #help us to find where our env file is located
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    #extra argument and given it a value of ignore as we may want to ignore any extra attributes provided within our Settings class.
    
Config=Settings()


