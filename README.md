

````markdown
# 🎮 Multiplayer Social Deduction Game - Dev Plan

A 7-player browser-based game inspired by *Among Us* / *Mafia*, built with **FastAPI (Python)** + **React (Frontend)** + **WebSockets**.

---

## 1. Project Setup

### Backend (Python - FastAPI)
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
````

2. Install dependencies:

   ```bash
   pip install fastapi uvicorn[standard] python-socketio[client] redis sqlalchemy
   ```

3. Project structure:

   ```
   backend/
   ├── main.py         # FastAPI app entry
   ├── game.py         # Game logic (roles, turns, actions)
   ├── models.py       # Database models (if using SQLAlchemy)
   ├── state.py        # In-memory/Redis game state
   └── requirements.txt
   ```

### Frontend (React + Phaser.js)

1. Create project:

   ```bash
   npx create-react-app frontend
   cd frontend
   npm install socket.io-client phaser
   ```

2. Project structure:

   ```
   frontend/
   ├── src/
   │   ├── App.js          # Lobby/game UI
   │   ├── GameCanvas.js   # Phaser game rendering
   │   └── sockets.js      # Socket.io client setup
   ```

---

## 2. Core Features

### Roles

* **Nightmare** (evil) – hides as good if inspected.
* **Witch** (evil) – inspects someone’s role, shares with Nightmare.
* **Detective** – inspects one player per night.
* **Duant** – links to a target, if killed → target dies too.
* **Joker** – wins if voted out.
* **King** – has 2 lives.
* **Common Villager(s)** – good, no special powers.

### Game Phases

1. **Lobby** – players join until 7 connected.
2. **Role Assignment** – server secretly assigns roles.
3. **Night Phase**

   * Witch acts → inspects someone.
   * Witch + Nightmare agree → kill one person.
   * Detective inspects → sees "good/evil".
   * Duant selects a target.
4. **Day Phase**

   * Narrator announces who died.
   * Voting happens (majority vote → elimination).
   * Check win conditions.
5. **Repeat** until win condition met:

   * All evil dead → good wins.
   * Evil >= good → evil wins.
   * Joker voted out → Joker wins.

---

## 3. Backend Implementation (FastAPI)

### main.py (entry point)

* Start FastAPI app.
* Setup **WebSocket routes** for:

  * `/ws/lobby/{room_id}` – handle player connections.
  * `/ws/game/{room_id}` – manage game state/events.

### game.py (game logic)

* Functions:

  * `assign_roles(players)`
  * `start_night_phase()`
  * `process_votes()`
  * `check_win_conditions()`

### state.py

* Store game state (players, roles, alive/dead, votes).
* Use **Redis** or in-memory dictionary.

---

## 4. Frontend Implementation (React)

### sockets.js

* Setup **socket.io-client** to connect to FastAPI backend.

### App.js

* Lobby screen → enter name, join room.
* Once 7 players connected → transition to game.

### GameCanvas.js

* Show player avatars, chat, voting UI.
* Render 2D game board (optional, via Phaser.js).

---

## 5. Database (Optional)

* Use **PostgreSQL (Supabase)** for:

  * Persistent accounts.
  * Game history.
* Or skip → just use Redis/memory for faster prototyping.

---

## 6. Hosting

* **Frontend**: Vercel or Netlify (`npm run build`).
* **Backend**: Render, Fly.io, or Railway (`uvicorn main:app --host 0.0.0.0 --port 8000`).
* **Database**: Supabase (Postgres) or Upstash (Redis).

---

## 7. Milestones

1. ✅ Setup FastAPI server + WebSockets.
2. ✅ Setup React frontend + Socket.IO client.
3. ✅ Implement lobby + role assignment.
4. ✅ Implement night phase actions.
5. ✅ Implement day phase + voting.
6. ✅ Add win conditions.
7. ✅ Add animations / UI polish with Phaser.js.
8. 🚀 Deploy to production.

---

## 8. Optional Enhancements

* Voice chat (WebRTC).
* Mobile-friendly UI.
* Authentication (Supabase Auth).
* Ranking/leaderboards.

---

# 🎯 Goal

By following this plan, you’ll have a **fully playable 7-player social deduction game** running in the browser with a **Python backend** and **React frontend**.

```

---
