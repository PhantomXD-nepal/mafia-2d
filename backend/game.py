import random
from typing import List, Dict, Optional
from enum import Enum

class Role(Enum):
    NIGHTMARE = "nightmare"
    WITCH = "witch"
    DETECTIVE = "detective"
    DUANT = "duant"
    JOKER = "joker"
    KING = "king"
    VILLAGER = "villager"

class GamePhase(Enum):
    LOBBY = "lobby"
    ROLE_ASSIGNMENT = "role_assignment"
    NIGHT = "night"
    DAY = "day"
    GAME_OVER = "game_over"

class Player:
    def __init__(self, sid: str, name: str, is_ai: bool = False):
        self.sid = sid
        self.name = name
        self.role: Optional[Role] = None
        self.alive = True
        self.votes = 0
        self.is_ai = is_ai

    def to_dict(self):
        return {
            "sid": self.sid,
            "name": self.name,
            "role": self.role.value if self.role else None,
            "alive": self.alive,
            "votes": self.votes,
            "is_ai": self.is_ai
        }

def assign_roles(players: List[Player]) -> None:
    """Assign roles to players randomly"""
    if len(players) != 7:
        raise ValueError("Game requires exactly 7 players")

    roles = [
        Role.NIGHTMARE,
        Role.WITCH,
        Role.DETECTIVE,
        Role.DUANT,
        Role.JOKER,
        Role.KING,
        Role.VILLAGER
    ]

    random.shuffle(roles)

    for player, role in zip(players, roles):
        player.role = role

def start_game_with_ai(game_state: Dict) -> None:
    """Fill the game with AI players and start."""
    num_players = len(game_state['players'])
    num_ai_to_add = 7 - num_players

    for i in range(num_ai_to_add):
        ai_sid = f"ai_{i}"
        ai_name = f"AI Player {i + 1}"
        ai_player = Player(ai_sid, ai_name, is_ai=True)
        game_state['players'].append(ai_player)

    assign_roles(game_state['players'])

def start_night_phase(game_state: Dict) -> Dict:
    """Initialize night phase actions"""
    # Reset night actions
    game_state['night_actions'] = {
        'witch_inspection': None,
        'detective_inspection': None,
        'duant_target': None,
        'kill_target': None
    }
    game_state['phase'] = GamePhase.NIGHT.value
    return game_state

def process_night_actions(game_state: Dict) -> Dict:
    """Process all night actions and determine deaths"""
    actions = game_state['night_actions']
    players = game_state['players']
    deaths = []

    # AI Nightmare action
    nightmare = next((p for p in players if p.role == Role.NIGHTMARE and p.is_ai and p.alive), None)
    if nightmare and not actions.get('kill_target'):
        possible_targets = [p for p in players if p.alive and p.role not in {Role.NIGHTMARE, Role.WITCH}]
        if possible_targets:
            target = random.choice(possible_targets)
            actions['kill_target'] = target.sid

    # Witch inspects and shares with Nightmare
    if actions['witch_inspection']:
        # Logic for witch action
        pass

    # Detective inspects
    if actions['detective_inspection']:
        # Logic for detective action
        pass

    # Duant links
    if actions['duant_target']:
        # Logic for duant action
        pass

    # Process kill
    if actions['kill_target']:
        target_player = next((p for p in game_state['players'] if p.sid == actions['kill_target']), None)
        if target_player:
            if target_player.role == Role.KING:
                # King has 2 lives
                target_player.votes += 1  # Use votes as life counter
                if target_player.votes >= 2:
                    target_player.alive = False
                    deaths.append(target_player.sid)
            else:
                target_player.alive = False
                deaths.append(target_player.sid)

            # Check Duant link
            duant = next((p for p in game_state['players'] if p.role == Role.DUANT and p.alive), None)
            if duant and actions.get('duant_target') == target_player.sid:
                duant.alive = False
                deaths.append(duant.sid)

    game_state['deaths'] = deaths
    return game_state

def process_votes(game_state: Dict, votes: Dict[str, str]) -> Dict:
    """Process day phase voting"""
    # Reset votes
    for player in game_state['players']:
        if player.alive:
            player.votes = 0

    # Count votes
    for voter_sid, target_sid in votes.items():
        target = next((p for p in game_state['players'] if p.sid == target_sid), None)
        if target and target.alive:
            target.votes += 1

    # Find player with most votes
    alive_players = [p for p in game_state['players'] if p.alive]
    if alive_players:
        eliminated = max(alive_players, key=lambda p: p.votes)
        eliminated.alive = False
        game_state['eliminated'] = eliminated.sid

        # Check Joker win condition
        if eliminated.role == Role.JOKER:
            game_state['winner'] = 'joker'
            game_state['phase'] = GamePhase.GAME_OVER.value

    return game_state

def check_win_conditions(game_state: Dict) -> Dict:
    """Check if game has ended and who won"""
    alive_players = [p for p in game_state['players'] if p.alive]
    evil_roles = {Role.NIGHTMARE, Role.WITCH}

    alive_evil = [p for p in alive_players if p.role in evil_roles]
    alive_good = [p for p in alive_players if p.role not in evil_roles]

    if not alive_evil:
        game_state['winner'] = 'good'
        game_state['phase'] = GamePhase.GAME_OVER.value
    elif len(alive_evil) >= len(alive_good):
        game_state['winner'] = 'evil'
        game_state['phase'] = GamePhase.GAME_OVER.value

    return game_state

def initialize_game_state() -> Dict:
    """Create initial game state"""
    return {
        'players': [],
        'phase': GamePhase.LOBBY.value,
        'night_actions': {},
        'deaths': [],
        'eliminated': None,
        'winner': None
    }
