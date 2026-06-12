
from fastapi import FastAPI

import models
from database import engine
from routers import users, offers, admin


app = FastAPI(title="Loadrd API documentation")

models.Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["System"])
def get_health():
    return {"message": "Application is healthy"}


app.include_router(users.router)
app.include_router(offers.router)
app.include_router(admin.router)
