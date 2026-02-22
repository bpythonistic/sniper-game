# Nyquist's Sniper

**Nyquist's Sniper** is a web-based strategy shooter that turns **Digital Signal Processing (DSP)** concepts into gameplay mechanics. Players must tune their "virtual oscilloscope" (sampling rate, bit depth, SNR) to detect and eliminate enemy signals before they breach the system.

This project is built to demonstrate full-stack proficiency with **Python**, **FastAPI**, **React**, and **PostgreSQL**, while providing an interactive education on the **Nyquist-Shannon Sampling Theorem**.

## 🎮 The Core Concept

In most games, what you see is what you get. In _Nyquist's Sniper_, what you see is only a **discrete sample** of reality.

- **The Enemy:** Continuous waveforms (Sine, Square, Sawtooth) moving at specific frequencies `f`.
- **The Weapon:** Your Sampling Rate `fs`.
- **The Mechanic:** If your sampling rate is too low `fs < 2f`, the enemies **alias**—they appear to move backwards, slow down, or stop entirely. To hit them, you must upgrade your hardware to meet the Nyquist limit.

## 🛠 Tech Stack

### Backend (The Physics Engine)

- **Language:** Python 3.14
- **Framework:** FastAPI
- **Math Kernel:** NumPy / SciPy (for signal generation and noise simulation)
- **Database:** PostgreSQL (storing user stats, signal configurations, and level presets)
- **ORM:** SQLAlchemy / SQLModel
- **Package Manager:** Pixi (pixi.prefix.dev)

### Frontend (The Scope)

- **Language:** TypeScript
- **Framework:** React
- **Build Tool:** Vite
- **Visualization:** HTML5 Canvas / SVG (for rendering waveforms)
- **State Management:** React Hooks / Context API

## 🚀 Getting Started

### Prerequisites

- [Pixi](https://pixi.prefix.dev/)
- [PostgreSQL 18](https://www.postgresql.org/download/)

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/bpythonistic/sniper-game.git
cd sniper-game

# Initialize the environment and install dependencies
pixi install

# Create .env file
cp back-end/app/.env.example back-end/app/.env
```

The API will be available at [http://localhost:8000](http://localhost:8000).

You can view the interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## 2. Frontend Setup

Once the API server is running, open a new terminal before proceeding.

```bash
# Install dependencies
pixi run update-nodejs
```

The game client will be available at [http://localhost:5173](http://localhost:5173)

## 3. Database Setup

Ensure PostgreSQL is not already globally installed and running before proceeding.

```bash
pixi run init-db
pixi run start-db-server
pixi run create-db
```

## 4. Launch Development Application

```bash
# Run the API server
pixi run launch-backend
# Start the development client
pixi run start-dev
```

## 5. Account for Schema Updates

```bash
# Clear the contents of an outdated database
pixi run clear-db
```

## 6. View PostgreSQL Logfile (for debugging)

```bash
# Read the contents of the PostgreSQL server's logfile
pixi run read-db-logs
```

## 🗓 Development Roadmap

### Phase 1: The Signal Engine (Current)

- [x] Implement SignalGenerator class in Python.

- [ ] Build the sampling logic (Discrete vs. Continuous).

- [ ] Add Gaussian Noise (AWGN) simulation.

- [ ] Create GET /scan endpoint for frontend visualization.

### Phase 2: The Game Loop

- [ ] "Shoot" mechanic with timestamp validation.

- [ ] Hit detection logic (Did the user hit the true signal?).

- [ ] Basic score tracking.

### Phase 3: RPG Persistence

- [ ] User authentication.

- [ ] Persistent stats (Upgrade Sampling Rate, Bit Depth).

- [ ] Level progression system.

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Install pre-commit Git hooks: `pixi run install-git-hooks`
4. Commit your changes (git commit -m 'Add some AmazingFeature')
5. Push to the branch (git push origin feature/AmazingFeature)
6. Open a Pull Request

## 📄 License

Distributed under the MIT License. See LICENSE for more information.
