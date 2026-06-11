from fastapi import FastAPI
from routers import users, offers

app = FastAPI(title="My Awesome API")


@app.get("/health", tags=["System"])
def get_health():
    return {"message": "Application is healthy"}


app.include_router(users.router)
app.include_router(offers.router)
