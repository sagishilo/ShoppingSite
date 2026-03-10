import redis
from pydantic_settings import BaseSettings

class Config (BaseSettings):
    MYSQL_USER:str = "user"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "main"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_TTL: int = 1800

    DATABASE_URL: str = f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

    @property
    def REDIS_CLIENT(self):
        return redis.Redis(host=self.REDIS_HOST,port=self.REDIS_PORT,decode_responses=True)