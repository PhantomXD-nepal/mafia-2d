import React, { useState, useEffect } from 'react';
import socket from './sockets';
import GameCanvas from './GameCanvas';
import './App.css';

function App() {
  const [playerName, setPlayerName] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [players, setPlayers] = useState([]);
  const [currentPhase, setCurrentPhase] = useState('lobby');
  const [myRole, setMyRole] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Socket event listeners
    socket.on('connect', () => {
      setIsConnected(true);
      addMessage('Connected to server');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      addMessage('Disconnected from server');
    });

    socket.on('message', (data) => {
      addMessage(data.data);
    });

    socket.on('lobby_update', (data) => {
      setPlayers(data);
    });

    socket.on('ready_to_start', (data) => {
      addMessage(data.message);
    });

    socket.on('role_assigned', (data) => {
      setMyRole(data.role);
      setGameStarted(true);
      addMessage(`Your role: ${data.role}`);
    });

    socket.on('phase_change', (data) => {
      setCurrentPhase(data.phase);
      addMessage(data.message);
    });

    socket.on('night_results', (data) => {
      addMessage(data.message);
    });

    socket.on('game_over', (data) => {
      addMessage(`Game Over! Winner: ${data.winner}`);
      setCurrentPhase('game_over');
    });

    socket.on('error', (data) => {
      addMessage(`Error: ${data.message}`);
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('message');
      socket.off('lobby_update');
      socket.off('ready_to_start');
      socket.off('role_assigned');
      socket.off('phase_change');
      socket.off('night_results');
      socket.off('game_over');
      socket.off('error');
    };
  }, []);

  const addMessage = (message) => {
    setMessages(prev => [...prev, { text: message, timestamp: new Date() }]);
  };

  const handleJoinLobby = () => {
    if (playerName.trim()) {
      socket.emit('join_lobby', { name: playerName.trim() });
    }
  };

  const handleStartGame = () => {
    socket.emit('start_game', {});
  };

  const handleStartGameWithAI = () => {
    socket.emit('start_game_with_ai', {});
  };

  const handleNightAction = (action, target) => {
    socket.emit('night_action', { action, target });
  };

  const handleVote = (target) => {
    socket.emit('vote', { target });
  };

  const handleEndNight = () => {
    socket.emit('end_night', {});
  };

  const handleEndDay = () => {
    socket.emit('end_day', {});
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎮 Mafia Game</h1>
        <div className="connection-status">
          Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </header>

      <main className="game-container">
        {!gameStarted ? (
          <div className="lobby">
            <h2>Join the Game</h2>
            <div className="join-form">
              <input
                type="text"
                placeholder="Enter your name"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleJoinLobby()}
              />
              <button onClick={handleJoinLobby} disabled={!playerName.trim()}>
                Join Lobby
              </button>
            </div>

            {players.length < 7 && (
              <button onClick={handleStartGameWithAI} className="start-button ai-button">
                Play with AI
              </button>
            )}

            {players.length >= 7 && (
              <button onClick={handleStartGame} className="start-button">
                Start Game
              </button>
            )}

            <div className="players-list">
              <h3>Players ({players.length}/7):</h3>
              <ul>
                {players.map((player, index) => (
                  <li key={index}>{player.name}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          <div className="game">
            <div className="game-info">
              <div className="phase-info">
                <h3>Current Phase: {currentPhase}</h3>
                {myRole && <p>Your Role: {myRole}</p>}
              </div>

              {currentPhase === 'night' && (
                <div className="night-actions">
                  <h4>Night Actions</h4>
                  <button onClick={handleEndNight}>End Night</button>
                </div>
              )}

              {currentPhase === 'day' && (
                <div className="day-actions">
                  <h4>Day Phase - Vote to Eliminate</h4>
                  <button onClick={handleEndDay}>End Day</button>
                </div>
              )}
            </div>

            <GameCanvas
              players={players}
              currentPhase={currentPhase}
              myRole={myRole}
              onAction={currentPhase === 'night' ? handleNightAction : handleVote}
            />
          </div>
        )}

        <div className="messages">
          <h3>Game Messages</h3>
          <div className="messages-list">
            {messages.map((msg, index) => (
              <div key={index} className="message">
                <span className="timestamp">
                  {msg.timestamp.toLocaleTimeString()}
                </span>
                <span className="text">{msg.text}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
