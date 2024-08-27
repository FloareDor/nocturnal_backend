from os import environ as env

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


class AuthConfig(BaseSettings):
    JWT_ALG: str = env.get("JWT_ALG")
    JWT_SECRET: str = env.get("JWT_SECRET")
    JWT_EXP: int = env.get("JWT_EXP")
    REFRESH_TOKEN_KEY: str = "refreshToken"
    REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 21  # 21 days
    SECURE_COOKIES: bool = True


auth_config = AuthConfig()
