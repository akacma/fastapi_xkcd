from pydantic import BaseSettings


class Settings(BaseSettings):
    host_address: str
    info: str
    images: str
    rate_limit: str

    class Config:
        env_file = ".env"
