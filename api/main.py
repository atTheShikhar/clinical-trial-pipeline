import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.server:app", port=8000, log_level="info", reload=True)
