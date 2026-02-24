from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@auth_router.post("/login")
async def login(username: str, password: str):
    if username == "admin" and password == "admin":
        return {"access_token": "fake-token", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

@auth_router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    if token == "fake-token":
        return {"username": "admin", "role": "administrator"}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")