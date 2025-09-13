import React, { useEffect, useRef } from 'react';
import Phaser from 'phaser';

const GameCanvas = ({ players, currentPhase, onAction, myRole }) => {
  const gameRef = useRef(null);

  useEffect(() => {
    if (!gameRef.current) {
      const config = {
        type: Phaser.AUTO,
        width: 800,
        height: 600,
        parent: 'game-canvas',
        backgroundColor: '#1a1a1a',
        scene: {
          preload: preload,
          create: create,
          update: update
        }
      };

      gameRef.current = new Phaser.Game(config);
    }

    function preload() {
      // More distinct player sprites
      this.load.image('villager', 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIyMCIgZmlsbD0iIzI3YWU2MCIvPjxwYXRoIGQ9Ik0yMCAyNUMxNy4yMzg2IDI1IDE1IDIyLjc2MTQgMTUgMjBDMTUgMTcuMjM4NiAxNy4yMzg2IDE1IDIwIDE1QzIyLjc2MTQgMTUgMjUgMTcuMjM4NiAyNSAyMEMyNSAyMi4zMDYxIDIyLjU0NzcgMjQuNjM1NSAyMCAyNSIgZmlsbD0id2hpdGUiLz48L3N2Zz4=');
      this.load.image('nightmare', 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIyMCIgZmlsbD0iI2M0MWMwYyIvPjxwYXRoIGQ9Ik0xNSA MjUgTDI1IDE1IE0xNSAxNSBMMjUgMjUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIvPjwvc3ZnPg==');
      this.load.image('witch', 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIyMCIgZmlsbD0iIzhFNTRFNyIvPjxwYXRoIGQ9Ik0yMCAxMEwxNSAyMEwyMCAzMEwyNSAyMFoiIGZpbGw9IndoaXRlIi8+PC9zdmc+');
      this.load.image('detective', 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIyMCIgZmlsbD0iIzM0OTRkYiIvPjxwYXRoIGQ9Ik0yMCAyMEwxNSA1TDI1IDVMMjAgMjBaIiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==');
      this.load.image('duant', 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIyMCIgZmlsbD0iI2YxYzQwZiIvPjxwYXRoIGQ9Ik0xNSAxNUgyNVYyNUgxNVYxNVoiIGZpbGw9IndoaXRlIi8+PC9zdmc+');
      this.load.image('joker', 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIyMCIgZmlsbD0iIzk5NTFDRiIvPjxwYXRoIGQ9Ik0xNSAyMEEyLjUgMi41IDAgMSAxIDIwIDIwQTIuNSAyLjUgMCAwIDEgMTUgMjBaTTI1IDIwQTIuNSAyLjUgMCAxIDEgMzAgMjBBMi41IDIuNSAwIDAgMSAyNSAyMFoiIGZpbGw9IndoaXRlIi8+PC9zdmc+');
      this.load.image('king', 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIyMCIgZmlsbD0iI2U2N2UyMiIvPjxwYXRoIGQ9Ik0xMCAxNUwyMCAxMEwyNSAxNUwyMCAyMEwxMCAxNVoiIGZpbGw9IndoaXRlIi8+PC9zdmc+');
    }

    function create() {
      this.players = this.add.group();
      this.playerTexts = this.add.group();

      this.phaseText = this.add.text(400, 50, `Phase: ${currentPhase}`, {
        fontSize: '24px',
        fill: '#ecf0f1'
      }).setOrigin(0.5);

      this.instructionText = this.add.text(400, 550, 'Waiting for players...', {
        fontSize: '18px',
        fill: '#ecf0f1'
      }).setOrigin(0.5);
    }

    function update() {
      updatePlayers.call(this);
      updateUI.call(this);
    }

    function getPlayerSprite(role) {
      const roleSprites = {
        'nightmare': 'nightmare',
        'witch': 'witch',
        'detective': 'detective',
        'duant': 'duant',
        'joker': 'joker',
        'king': 'king',
        'villager': 'villager'
      };
      return roleSprites[role] || 'villager';
    }

    function updatePlayers() {
      this.players.clear(true, true);
      this.playerTexts.clear(true, true);

      players.forEach((player, index) => {
        const x = 150 + (index % 4) * 150;
        const y = 200 + Math.floor(index / 4) * 150;

        const playerSprite = this.add.sprite(x, y, getPlayerSprite(player.role));
        playerSprite.setData('player', player);
        playerSprite.setInteractive({ useHandCursor: true });

        if (!player.alive) {
          playerSprite.setTint(0x555555);
          playerSprite.disableInteractive();
        } else {
          playerSprite.clearTint();
        }

        this.players.add(playerSprite);

        const playerText = this.add.text(x, y + 40, player.name, {
          fontSize: '14px',
          fill: '#ffffff',
          align: 'center'
        }).setOrigin(0.5);
        this.playerTexts.add(playerText);

        playerSprite.on('pointerdown', () => {
          if (player.alive) {
            handlePlayerClick(player);
          }
        });
      });
    }
    
    function handlePlayerClick(player) {
      if (currentPhase === 'night' && myRole === 'nightmare') {
        onAction('kill', player.sid);
      } else if (currentPhase === 'day') {
        onAction('vote', player.sid);
      }
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
            if (myRole === 'nightmare') {
              instruction = 'Choose a player to eliminate.';
            } else {
              instruction = 'The Nightmare is choosing...';
            }
            break;
          case 'day':
            instruction = 'Vote to eliminate a player.';
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
  }, [players, currentPhase, myRole, onAction]);

  return <div id="game-canvas" style={{ width: '800px', height: '600px', margin: '0 auto' }}></div>;
};

export default GameCanvas;
