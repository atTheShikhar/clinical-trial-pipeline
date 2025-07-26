from pydantic_settings import BaseSettings
from typing import Literal


class SettingsManager(BaseSettings):
    """
    Desc: Reads the following properties from the environment variables,
    for easy accesss in a typed format.\n
    NOTE: exported variable names are given preference over `.env` file.
    """
    mysql_user: str
    mysql_pass: str
    mysql_host: str
    mysql_db: str
    storage_bucket: str
    storage_access_id: str
    storage_secret: str
    server_api_key: str
    environment: Literal["prod", "dev"] = "dev"

    def is_prod(self):
        return self.environment == "prod"
        
    class Config:
        extra = "allow"
        env_file = ".env"
        env_file_encoding = "utf-8"



sm = SettingsManager()