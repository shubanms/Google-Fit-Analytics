from src.core.configs import create_app

from src.routes.digest import router as digest_router
from src.routes.upload import router as upload_router

app = create_app()

app.include_router(digest_router, prefix="/digest", tags=['Digest'])
app.include_router(upload_router, prefix="/upload", tags=['Upload'])


@app.get("/", tags=['Health Check'])
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
