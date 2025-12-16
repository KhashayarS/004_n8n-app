from fastapi import FastAPI
import models
from database import engine
from routers import auth, books, user, admin


models.Base.metadata.create_all(bind=engine)


app = FastAPI(version="1.0.0")

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(user.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
