from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
from .game import assign_roles, start_night_phase, process_night_actions, process_votes, check_win_conditions, GamePhase
from .state import game_state_manager

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
    game_state_manager.remove_player(sid)
    await sio.emit('lobby_update', game_state_manager.get_players_dict())

@sio.event
async def join_lobby(sid, data):
    """Handle player joining lobby"""
    name = data.get('name', f'Player_{sid[:4]}')
    print(f"Player {name} joined lobby")

    game_state_manager.add_player(sid, name)
    players = game_state_manager.get_players_dict()

    await sio.emit('lobby_update', players)

    # Check if we have 7 players to start
    if len(players) == 7:
        await sio.emit('ready_to_start', {'message': 'All players joined! Ready to start game.'})

@sio.event
async def start_game(sid, data):
    """Handle game start"""
    state = game_state_manager.get_game_state()
    if len(state['players']) != 7:
        await sio.emit('error', {'message': 'Need exactly 7 players to start'}, to=sid)
        return

    print("Game starting...")
    assign_roles(state['players'])
    game_state_manager.update_phase(GamePhase.ROLE_ASSIGNMENT)

    # Send roles to players privately
    for player in state['players']:
        await sio.emit('role_assigned', {
            'role': player.role.value if player.role else None,
            'name': player.name
        }, to=player.sid)

    # Start night phase
    start_night_phase(state)
    game_state_manager.save_game_state(state)

    await sio.emit('phase_change', {'phase': 'night', 'message': 'Night phase begins!'})

@sio.event
async def night_action(sid, data):
    """Handle night actions from players"""
    action_type = data.get('action')
    target_sid = data.get('target')

    game_state_manager.record_night_action(action_type, sid, target_sid)
    await sio.emit('action_received', {'action': action_type}, to=sid)

@sio.event
async def end_night(sid, data):
    """Process night actions and move to day"""
    state = game_state_manager.get_game_state()
    process_night_actions(state)
    check_win_conditions(state)
    game_state_manager.save_game_state(state)

    # Notify about deaths
    if state['deaths']:
        await sio.emit('night_results', {
            'deaths': state['deaths'],
            'message': f"Players died: {[p.name for p in state['players'] if p.sid in state['deaths']]}"
        })

    if state.get('winner'):
        await sio.emit('game_over', {'winner': state['winner']})
    else:
        game_state_manager.update_phase(GamePhase.DAY)
        await sio.emit('phase_change', {'phase': 'day', 'message': 'Day phase begins! Time to vote.'})

@sio.event
async def vote(sid, data):
    """Handle voting during day phase"""
    target_sid = data.get('target')
    # TODO: Collect all votes and process after timeout or all voted
    await sio.emit('vote_received', {'message': 'Vote recorded'}, to=sid)

@sio.event
async def end_day(sid, data):
    """Process votes and move to night"""
    # TODO: Process votes
    state = game_state_manager.get_game_state()
    # For now, simulate processing
    check_win_conditions(state)
    game_state_manager.save_game_state(state)

    if state.get('winner'):
        await sio.emit('game_over', {'winner': state['winner']})
    else:
        start_night_phase(state)
        game_state_manager.save_game_state(state)
        await sio.emit('phase_change', {'phase': 'night', 'message': 'Night phase begins!'})

# HTTP routes
@app.get("/")
async def root():
    state = game_state_manager.get_game_state()
    return {
        "message": "Mafia Game Server is running",
        "status": "online",
        "players": len(state['players']),
        "phase": state['phase']
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/reset")
async def reset_game():
    """Reset game state for testing"""
    game_state_manager.reset_game()
    return {"message": "Game reset"}

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, reload=True)
