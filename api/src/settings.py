from pydantic_settings import BaseSettings
from typing import Literal


ACL = {
    "admin": ["/admin/*"], # admin
    "employee": ["/tracker/*"],
}


MAX_UPLOAD_SINCE_MINUTES = 5 # TODO: set to 5 minutes in prod

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
    # jwt_secret: str
    # storage_bucket: str
    storage_bucket: str
    storage_access_id: str
    storage_secret: str
    environment: Literal["prod", "dev"] = "dev"
    refresh_expiry_minutes: int = 24 * 60 * 30 # 30 days
    access_expiry_minutes: int = 60 * 24 # 24 hours TODO: change
    token_algo: str = "HS256" 

    # def get_mysql_uri(self):
    #     dsn = f"mysql+asyncmy://{self.sql_uname}:{self.sql_pass}@{self.sql_host}:3306/{self.sql_db}"
    #     return dsn
        
    class Config:
        extra = "allow"
        env_file = ".env"
        env_file_encoding = "utf-8"



sm = SettingsManager() # type: ignore