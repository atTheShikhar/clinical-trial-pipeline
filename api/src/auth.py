from typing import Annotated
from fastapi import Depends, HTTPException, Header, Request
from src.settings import sm


def verify_user_token(request: Request, x_api_token: str = Header(...)):
    if x_api_token != sm.server_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


APIKey = Annotated[str, Depends(verify_user_token)]
