from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.db import connect_db, disconnect_db
from src.routes.query import queryRouter
from src.settings import sm



@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = connect_db()
    app.state.db_conn = conn
    yield
    disconnect_db()


app = FastAPI(lifespan=lifespan, docs_url="/active-docs/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(content=jsonable_encoder({"msg": exc.detail}), status_code=exc.status_code)

@app.exception_handler(500)
async def server_exception_handler(request: Request, exc: Exception):
    return JSONResponse(content=jsonable_encoder({"msg": "Something went wrong!"}), status_code=500)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    try:
        msg = str(exc.args[0][0]["ctx"]["error"])
    except Exception as e:
        msg = "Invalid input data!"
    return JSONResponse(content=jsonable_encoder({"msg": msg}), status_code=422)



app.include_router(queryRouter)



@app.get("/ping")
async def health_check():
    return {"msg": "ok"}


