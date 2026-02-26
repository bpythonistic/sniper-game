# **Nyquist's Sniper:** Full-stack Web Application

Gamifying Digital Signal Processing (DSP) with an unconventional sniper concept.

## Summary / Thought Process

**Nyquist's Sniper** is a web-based strategy shooter that turns **Digital Signal Processing (DSP)** concepts into gameplay mechanics. Players must tune their "virtual oscilloscope" (sampling rate, bit depth, SNR) to detect and eliminate enemy signals before they breach the system.

This project is built to demonstrate full-stack proficiency with **Python**, **FastAPI**, **React**, and **PostgreSQL**, while providing an interactive education on the **Nyquist-Shannon Sampling Theorem**.

## 🎮 The Core Concept

In most games, what you see is what you get. In _Nyquist's Sniper_, what you see is only a **discrete sample** of reality.

- **The Enemy:** Continuous waveforms (Sine, Square, Sawtooth) moving at specific frequencies $f$.
- **The Weapon:** Your Sampling Rate $f_s$.
- **The Mechanic:** If your sampling rate is too low $f_s < 2f$, the enemies **alias**—they appear to move backwards, slow down, or stop entirely. To hit them, you must upgrade your hardware to meet the Nyquist limit.

### Problem Statement

Digital Signal Processing (DSP) concepts—such as the Nyquist-Shannon sampling theorem, quantization error, and Additive White Gaussian Noise (AWGN)—are fundamentally abstract and highly mathematical. Traditional educational tools rely heavily on static graphs or non-interactive MATLAB simulations. The challenge is to build a highly interactive, web-based application that gamifies these concepts, making them intuitive while simultaneously serving as a robust demonstration of modern full-stack engineering architecture.

### Constraints

1. **State Synchronization & Latency:** The server acts as the "continuous physical world" (the truth), while the client acts as the "discrete digital scope" (the sample). Network latency between the FastAPI backend and React frontend must be minimized or mathematically compensated for to ensure accurate hit detection.
2. **Browser Rendering Limits:** The frontend must simulate rendering "poorly" (at low sampling rates) on purpose to demonstrate aliasing, actively fighting against the browser's default 60fps `requestAnimationFrame` loop.
3. **Complex Data Modeling:** The database must efficiently store not just discrete user statistics, but relational data defining continuous mathematical functions (waveforms) and statistical probabilities (noise floors).

### Solution / Approach

The solution is "Nyquist's Sniper," a web application utilizing a Python/FastAPI backend, a React/TypeScript frontend, and a PostgreSQL database. The system separates the "Physics Engine" (server) from the "Renderer" (client) to enforce the core educational mechanic: what the player sees is only a discrete sample of reality.

### Development Roadmap

#### Phase 1: The Signal Engine (Current)

- [x] Implement SignalGenerator class in Python.

- [ ] Build the sampling logic (Discrete vs. Continuous).

- [ ] Add Gaussian Noise (AWGN) simulation.

- [ ] Create GET /scan endpoint for frontend visualization.

#### Phase 2: The Game Loop

- [ ] "Shoot" mechanic with timestamp validation.

- [ ] Hit detection logic (Did the user hit the true signal?).

- [ ] Basic score tracking.

#### Phase 3: RPG Persistence

- [ ] User authentication.

- [ ] Persistent stats (Upgrade Sampling Rate, Bit Depth).

- [ ] Level progression system.

### Frontend Web UI

The frontend acts as an interactive digital oscilloscope. It renders two states: the high-resolution "True Signal" (often hidden) and the "Sampled Signal" based on the player's current hardware stats.

- **Visualizing Aliasing:** If the player's sampling rate ($f_s$) is less than twice the target's frequency ($2f$), the UI visually aliases the target, causing it to appear as a slow-moving "ghost" enemy.
- **Visualizing Noise:** Low Signal-to-Noise Ratio (SNR) is rendered by applying a randomized visual spread to the sampled points, forcing the user to upgrade their virtual hardware (LNA/Filters) to resolve the target.

### Backend API

The backend serves as the DSP engine and authoritative game state manager.

- It calculates exact analytical positions of continuous waveforms using $y(t) = A \cdot \sin(2\pi f t + \phi) + V_{offset}$.
- When the frontend requests a "scan," the backend mathematically samples the continuous function at the player's specific $f_s$, applies Gaussian noise (`numpy.random.normal`), and returns the discrete payload.
- It handles the core combat logic: when a player "shoots" at a timestamp, the backend compares the shot coordinate to the _true_ continuous coordinate, not the aliased frontend coordinate.

### PostgreSQL Database

The database enforces persistence and the RPG mechanics of the application.

- **`users`:** Stores a table of game users' id and name attributes.
- **`scopes`:** Stores a table of Sniper `scope`s linked with each `user`.

---

## 🛠 Tech Stack

### Backend (The Physics Engine)

- **Language:** Python 3.14
- **Framework:** FastAPI
- **Math Kernel:** NumPy / SciPy (for signal generation and noise simulation)
- **Database:** PostgreSQL (storing user stats, signal configurations, and level presets)
- **ORM:** SQLAlchemy / SQLModel
- **Package Manager:** Pixi (pixi.prefix.dev)

### Frontend (The Scope)

- **Language:** TypeScript 5
- **Framework:** React
- **Build Tool:** Vite
- **Visualization:** HTML5 Canvas / SVG (for rendering waveforms)
- **State Management:** React Hooks / Context API

## 🚀 Getting Started

### Prerequisites

- [Pixi](https://pixi.prefix.dev/latest/#installation)

### Backend Setup

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

### Frontend Setup

Once the API server is running, open a new terminal before proceeding.

```bash
# Install dependencies
pixi run update-nodejs
```

The game client will be available at [http://localhost:5173](http://localhost:5173)

### Database Setup

Ensure PostgreSQL is not already globally installed and running before proceeding.

```bash
pixi run init-db
pixi run start-db-server
pixi run create-db
```

### Launch Development Application

```bash
# Run the API server
pixi run launch-backend
# Start the development client
pixi run start-dev
```

### Run Pytest

```bash
pixi run backend-tests
```

### Account for Schema Updates

```bash
# Clear the contents of an outdated database
pixi run clear-db
```

### View PostgreSQL Logfile (for debugging)

```bash
# Read the contents of the PostgreSQL server's logfile
pixi run read-db-logs
```

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Ensure that the GitHub Actions pass
6. Open a Pull Request

---

## Project Code Dive

### Python code (FastAPI backend)

The backend leverages Python's scientific ecosystem alongside asynchronous web routing to handle both standard CRUD operations and real-time DSP data streaming.

- **Database Connection Management:** Instead of a heavy ORM, the project utilizes raw `psycopg` with a custom context manager (`get_db_connection`) to handle lightweight, efficient PostgreSQL connections and cursor yields. Wrapper functions like `execute_write_query` manage transactional commits seamlessly.
- **Continuous Signal Modeling:** The core math is isolated in `signal_generator.py`. It uses `numpy.sin` to generate continuous waveforms and employs a `new_scope` context manager to safely yield functions that update signal frequencies on the fly.
- **Real-time Synchronization (WebSockets):** The application relies on a WebSocket endpoint (`/ws/scope/{scope_id}`) to push continuous signal updates to the client. This endpoint calculates 1000 time-points per update and streams them using strictly typed Pydantic structures.
- **Strict Typing:** All data boundaries are enforced using Pydantic in `schema.py`, ensuring payloads like `ScopeOutputModel` always contain validated time and signal coordinate arrays.

### TypeScript code (React + Vite frontend)

The frontend uses React with optimized state management to handle the rendering of high-frequency data points without blocking the main UI thread.

- **Network Layer:** The `api.tsx` module acts as a unified gateway, handling standard HTTP `fetch` requests for user/scope creation alongside a robust `renderScopeWebSocket` handler that manages the real-time data ingestion and parsing.
- **DSP Visualization:** The `WaveformVisualizer.tsx` component is the visual engine. It leverages React's `useMemo` hook to heavily optimize the coordinate calculations. It calculates two distinct datasets:
    1. A "True Signal" array (simulated at a high resolution of 1000 samples to mimic analog reality).
    2. A "Sampled Signal" array derived dynamically from the player's selected sampling rate.
- **Dynamic Aliasing Logic:** The UI explicitly checks the Nyquist Condition (`samplingRate < 2 * frequency`). If violated, the UI dynamically alerts the user and renders the "ghost" aliased path using SVG overlays.

### Pixi implementation (dependencies / dev environment ecosystem)

Dependency management and environment isolation are handled via **Pixi** (`prefix.dev`), ensuring a deterministic, cross-platform build without the overhead of Docker during rapid local development.

- **Environment Setup:** The environment pulls `fastapi`, `uvicorn`, `numpy`, and `psycopg` from the conda-forge ecosystem, guaranteeing that compiled C-extensions (essential for fast DSP math via NumPy and efficient Postgres drivers) work identically across macOS, Linux, and Windows.
- **Custom Tasks:** Custom Pixi tasks are configured to spin up the Uvicorn server, execute Pytest suites, and run database table initializations with a single command.

### Project Configuration (package.json, tsconfig.json, etc.)

- **`tsconfig.json`:** Configured with `"strict": true` and `"noImplicitAny": true` to catch edge cases in the visualization logic, ensuring all arrays mapping to the HTML5 Canvas/SVG elements are strongly typed.

- **Vite Configuration:** Set up for rapid Hot Module Replacement (HMR) during development. The build process is optimized to chunk the heavy graphing and React logic separately from the lightweight API wrappers.
- **CORS & Network Config:** The backend is explicitly configured via FastAPI's `CORSMiddleware` to allow cross-origin requests and WebSocket upgrades specifically from Vite's default dev server (`localhost:5173`).

### GitHub Workflows and Pre-commit tasks

CI/CD is automated to maintain a high code standard across the repository.

- **Pre-commit Hooks:** Enforces Ruff for Python formatting and Prettier for the React codebase. This ensures the math-heavy Python files remain highly readable.
- **GitHub Actions:** Workflows are designed to automatically run on pushes and pull requests. There are currently two (functional) GitHub Actions: `Ruff` and `ESLint`, that automatically check `*.py` files and `*.js/*.ts/*.tsx` files respectively for syntax errors and code-style compliance.

## Findings

1. **Prototype UI Latency:** While trying to connect the `WaveformVisualizer.tsx` component to the backend API, it was clear that performing a `Fetch` from an API endpoint every time the `frequency` slider was moved created far too many requests, adversely affecting the latency of the prototype UI. A planned WebSocket implementation should fix that.
2. **ESLint Workflow performance:** With the initial implementation of an ESLint GitHub Workflow, each push or pull request needed to build the Node.js dependencies from scratch, which meant that the entire task took over a minute. After configuring the workflow to automatically cache `node_modules/` for later retrieval (if `package.json` is not modified), this Action now completes in less than 25 seconds.

## Recommendations

1. **WebSocket Integration:** Implement the `/ws/scope/` WebSocket interface so that the frontend can simply connect to the backend to retrieve updates whenever the `frequency` slider is moved in the prototype UI.
2. **Expand to the Complex Plane:** Introduce a "Constellation Mode" utilizing In-Phase and Quadrature (I/Q) mapping, allowing players to visualize and fight against Phase Noise and AWGN in 2D space.
3. **WebAssembly (Wasm) Porting:** If the signal generation logic becomes overly complex (e.g., adding multiple overlapping FFT layers), compile the Python/NumPy logic to Wasm for client-side execution to completely eliminate network latency for hit detection.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
