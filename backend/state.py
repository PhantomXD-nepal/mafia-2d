import redis
import json
from typing import Dict, List, Optional
from game import Player, GamePhase, initialize_game_state

class GameStateManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.game_key = "mafia_game_state"

    def get_game_state(self) -> Dict:
        """Get current game state from Redis"""
        state_json = self.redis.get(self.game_key)
        if state_json:
            state = json.loads(state_json)
            # Reconstruct Player objects
            state['players'] = [Player(**p) for p in state['players']]
            return state
        return initialize_game_state()

    def save_game_state(self, state: Dict) -> None:
        """Save game state to Redis"""
        # Convert Player objects to dicts
        state_copy = state.copy()
        state_copy['players'] = [p.to_dict() for p in state['players']]
        self.redis.set(self.game_key, json.dumps(state_copy))

    def add_player(self, sid: str, name: str) -> None:
        """Add a player to the game"""
        state = self.get_game_state()
        if len(state['players']) < 7:
            player = Player(sid, name)
            state['players'].append(player)
            self.save_game_state(state)

    def remove_player(self, sid: str) -> None:
        """Remove a player from the game"""
        state = self.get_game_state()
        state['players'] = [p for p in state['players'] if p.sid != sid]
        self.save_game_state(state)

    def get_player(self, sid: str) -> Optional[Player]:
        """Get a specific player by SID"""
        state = self.get_game_state()
        return next((p for p in state['players'] if p.sid == sid), None)

    def get_alive_players(self) -> List[Player]:
        """Get list of alive players"""
        state = self.get_game_state()
        return [p for p in state['players'] if p.alive]

    def get_players_dict(self) -> List[Dict]:
        """Get players as dictionaries for API responses"""
        state = self.get_game_state()
        return [p.to_dict() for p in state['players']]

    def update_phase(self, phase: GamePhase) -> None:
        """Update game phase"""
        state = self.get_game_state()
        state['phase'] = phase.value
        self.save_game_state(state)

    def record_night_action(self, action_type: str, player_sid: str, target_sid: Optional[str] = None) -> None:
        """Record a night action"""
        state = self.get_game_state()
        if 'night_actions' not in state:
            state['night_actions'] = {}

        if action_type == 'witch_inspect':
            state['night_actions']['witch_inspection'] = target_sid
        elif action_type == 'detective_inspect':
            state['night_actions']['detective_inspection'] = target_sid
        elif action_type == 'duant_link':
            state['night_actions']['duant_target'] = target_sid
        elif action_type == 'kill':
            state['night_actions']['kill_target'] = target_sid

        self.save_game_state(state)

    def clear_night_actions(self) -> None:
        """Clear night actions after processing"""
        state = self.get_game_state()
        state['night_actions'] = {}
        self.save_game_state(state)

    def reset_game(self) -> None:
        """Reset game state for a new game"""
        self.redis.delete(self.game_key)

# Global instance for easy access
game_state_manager = GameStateManager()

# Fallback in-memory storage if Redis is not available
class InMemoryGameStateManager:
    def __init__(self):
        self._state = initialize_game_state()

    def get_game_state(self) -> Dict:
        return self._state

    def save_game_state(self, state: Dict) -> None:
        self._state = state

    def add_player(self, sid: str, name: str) -> None:
        if len(self._state['players']) < 7:
            player = Player(sid, name)
            self._state['players'].append(player)

    def remove_player(self, sid: str) -> None:
        self._state['players'] = [p for p in self._state['players'] if p.sid != sid]

    def get_player(self, sid: str) -> Optional[Player]:
        return next((p for p in self._state['players'] if p.sid == sid), None)

    def get_alive_players(self) -> List[Player]:
        return [p for p in self._state['players'] if p.alive]

    def get_players_dict(self) -> List[Dict]:
        return [p.to_dict() for p in self._state['players']]

    def update_phase(self, phase: GamePhase) -> None:
        self._state['phase'] = phase.value

    def record_night_action(self, action_type: str, player_sid: str, target_sid: Optional[str] = None) -> None:
        if 'night_actions' not in self._state:
            self._state['night_actions'] = {}

        if action_type == 'witch_inspect':
            self._state['night_actions']['witch_inspection'] = target_sid
        elif action_type == 'detective_inspect':
            self._state['night_actions']['detective_inspection'] = target_sid
        elif action_type == 'duant_link':
            self._state['night_actions']['duant_target'] = target_sid
        elif action_type == 'kill':
            self._state['night_actions']['kill_target'] = target_sid

    def clear_night_actions(self) -> None:
        self._state['night_actions'] = {}

    def reset_game(self) -> None:
        self._state = initialize_game_state()

# Try to use Redis, fallback to in-memory
try:
    game_state_manager = GameStateManager()
except Exception as e:
    print(f"Redis not available, using in-memory storage: {e}")
    game_state_manager = InMemoryGameStateManager()
