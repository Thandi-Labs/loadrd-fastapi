from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/")
def get_users():
    return {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}


@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": "Alice"}
