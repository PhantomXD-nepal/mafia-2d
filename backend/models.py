from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class GameSession(Base):
    __tablename__ = 'game_sessions'

    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    winner = Column(String(20), nullable=True)  # 'good', 'evil', 'joker'
    player_count = Column(Integer, default=7)

class PlayerRecord(Base):
    __tablename__ = 'player_records'

    id = Column(Integer, primary_key=True)
    game_session_id = Column(Integer, nullable=False)
    player_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    is_alive = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

class GameAction(Base):
    __tablename__ = 'game_actions'

    id = Column(Integer, primary_key=True)
    game_session_id = Column(Integer, nullable=False)
    action_type = Column(String(50), nullable=False)  # 'vote', 'kill', 'inspect', etc.
    player_sid = Column(String(50), nullable=False)
    target_sid = Column(String(50), nullable=True)
    phase = Column(String(20), nullable=False)  # 'night', 'day'
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)

# Database setup
DATABASE_URL = "sqlite:///./mafia_game.db"  # For development, use SQLite

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Usage example:
# from models import create_tables, GameSession, PlayerRecord, GameAction, get_db
# create_tables()
# db = get_db()
# new_session = GameSession(session_id="game_123")
# db.add(new_session)
# db.commit()
