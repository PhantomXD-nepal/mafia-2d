from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

app = FastAPI(title="Mafia Game Server", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SocketIO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# WebSocket event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")
    await sio.emit('message', {'data': 'Connected to Mafia Game Server'}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def join_lobby(sid, data):
    """Handle player joining lobby"""
    print(f"Player {data.get('name', 'Unknown')} joined lobby")
    # TODO: Add to game state
    await sio.emit('lobby_update', {'message': f"Player joined: {data.get('name')}"})

@sio.event
async def start_game(sid, data):
    """Handle game start"""
    print("Game starting...")
    # TODO: Assign roles and start game
    await sio.emit('game_started', {'message': 'Game has begun!'})

# HTTP routes
@app.get("/")
async def root():
    return {"message": "Mafia Game Server is running", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, reload=True)
