from fastapi import APIRouter

chat_router = APIRouter()

@chat_router.get("/messages/")
async def get_messages():
    return [{"user": "Alice", "message": "Hello"}, {"user": "Bob", "message": "Hi Alice"}]