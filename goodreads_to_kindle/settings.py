from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    email_password: str
    email_smtp_port: int
    email_smtp: str
    email_user: str
    rapid_api_key: str
    zlib_email: str
    zlib_password: str
