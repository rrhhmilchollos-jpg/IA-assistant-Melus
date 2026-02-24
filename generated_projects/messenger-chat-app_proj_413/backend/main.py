from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data from client #{client_id}: {data}")  # Additional logging for debug
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print(f"Client #{client_id} disconnected")