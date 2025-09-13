from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
import uvicorn
try:
    from .game import assign_roles, start_night_phase, process_night_actions, process_votes, check_win_conditions, GamePhase
    from .state import game_state_manager
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from game import assign_roles, start_night_phase, process_night_actions, process_votes, check_win_conditions, GamePhase
    from state import game_state_manager

import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('mafia.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)

app = FastAPI(title="Mafia Game Server", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SocketIO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=['http://localhost:3000'])
socket_app = socketio.ASGIApp(sio, app)

# WebSocket event handlers
@sio.event
async def connect(sid, environ):
    logging.info(f"Client {sid} connected")
    await sio.emit('message', {'data': 'Connected to Mafia Game Server'}, to=sid)

@sio.event
async def disconnect(sid):
    logging.info(f"Client {sid} disconnected")
    game_state_manager.remove_player(sid)
    await sio.emit('lobby_update', game_state_manager.get_players_dict())

@sio.event
async def join_lobby(sid, data):
    """Handle player joining lobby"""
    name = data.get('name', f'Player_{sid[:4]}')
    logging.info(f"Player {name} joined lobby")

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

    logging.info("Game starting...")
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
    asyncio.create_task(end_night_after_delay(10))

@sio.event
async def start_game_with_ai(sid, data):
    """Handle game start with AI"""
    state = game_state_manager.get_game_state()
    num_players = len(state['players'])
    if num_players < 1:
        await sio.emit('error', {'message': 'At least one human player is required'}, to=sid)
        return

    logging.info("Starting game with AI...")
    from game import start_game_with_ai as start_game_with_ai_func
    start_game_with_ai_func(state)
    game_state_manager.save_game_state(state) # Save state after adding AI
    await sio.emit('lobby_update', game_state_manager.get_players_dict()) # Update lobby
    await sio.sleep(1) # Give frontend time to update

    game_state_manager.update_phase(GamePhase.ROLE_ASSIGNMENT)

    # Send roles to players privately
    for player in state['players']:
        if not player.is_ai:
            await sio.emit('role_assigned', {
                'role': player.role.value if player.role else None,
                'name': player.name
            }, to=player.sid)

    # Start night phase
    start_night_phase(state)
    game_state_manager.save_game_state(state)

    await sio.emit('phase_change', {'phase': 'night', 'message': 'Night phase begins!'})
    asyncio.create_task(end_night_after_delay(10))

@sio.event
async def night_action(sid, data):
    """Handle night actions from players"""
    action_type = data.get('action')
    target_sid = data.get('target')

    game_state_manager.record_night_action(action_type, sid, target_sid)
    await sio.emit('action_received', {'action': action_type}, to=sid)

async def end_night_after_delay(delay: int):
    await asyncio.sleep(delay)
    logging.info("Auto-ending night phase...")
    await sio.emit('end_night', {})

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
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
