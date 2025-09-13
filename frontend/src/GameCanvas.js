import React, { useEffect, useRef } from 'react';
import Phaser from 'phaser';

const GameCanvas = ({ players, currentPhase, onAction }) => {
  const gameRef = useRef(null);

  useEffect(() => {
    if (!gameRef.current) {
      const config = {
        type: Phaser.AUTO,
        width: 800,
        height: 600,
        parent: 'game-canvas',
        backgroundColor: '#2c3e50',
        scene: {
          preload: preload,
          create: create,
          update: update
        }
      };

      gameRef.current = new Phaser.Game(config);
    }

    function preload() {
      // Load assets here
      this.load.image('player', 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiMzNDk4ZGIiLz4KPHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHg9IjEwIiB5PSIxMCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+CjxjaXJjbGUgY3g9IjEyIiBjeT0iOCIgcj0iNCIvPgo8cGF0aCBkPSJtMTIgMTMgOCAxOCIvPgo8L3N2Zz4KPC9zdmc+');
    }

    function create() {
      // Create game objects
      this.players = this.add.group();
      this.playerTexts = this.add.group();

      // Add UI text
      this.phaseText = this.add.text(400, 50, `Phase: ${currentPhase}`, {
        fontSize: '24px',
        fill: '#ffffff'
      }).setOrigin(0.5);

      // Add instruction text
      this.instructionText = this.add.text(400, 550, 'Waiting for players...', {
        fontSize: '18px',
        fill: '#ffffff'
      }).setOrigin(0.5);
    }

    function update() {
      // Update game objects
      updatePlayers.call(this);
      updateUI.call(this);
    }

    function updatePlayers() {
      // Clear existing players
      this.players.clear(true, true);
      this.playerTexts.clear(true, true);

      // Add current players
      players.forEach((player, index) => {
        const x = 100 + (index % 4) * 150;
        const y = 150 + Math.floor(index / 4) * 100;

        const playerSprite = this.add.sprite(x, y, 'player');
        playerSprite.setTint(player.alive ? 0x3498db : 0xe74c3c);
        this.players.add(playerSprite);

        const playerText = this.add.text(x, y + 30, `${player.name}\n${player.role || 'Unknown'}`, {
          fontSize: '14px',
          fill: '#ffffff',
          align: 'center'
        }).setOrigin(0.5);
        this.playerTexts.add(playerText);
      });
    }

    function updateUI() {
      if (this.phaseText) {
        this.phaseText.setText(`Phase: ${currentPhase}`);
      }

      if (this.instructionText) {
        let instruction = '';
        switch (currentPhase) {
          case 'lobby':
            instruction = `Players: ${players.length}/7`;
            break;
          case 'night':
            instruction = 'Night phase: Make your actions!';
            break;
          case 'day':
            instruction = 'Day phase: Vote to eliminate!';
            break;
          default:
            instruction = 'Game in progress...';
        }
        this.instructionText.setText(instruction);
      }
    }

    return () => {
      if (gameRef.current) {
        gameRef.current.destroy(true);
        gameRef.current = null;
      }
    };
  }, [players, currentPhase]);

  return <div id="game-canvas" style={{ width: '800px', height: '600px', margin: '0 auto' }}></div>;
};

export default GameCanvas;
