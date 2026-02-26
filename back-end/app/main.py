"""
This module defines the main FastAPI application and database connection utilities.

It includes:
- A FastAPI application instance.
- A context manager for database connections.
"""

import os

# import json
from dotenv import load_dotenv

# from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from app.features.signal_generator import new_scope
from app.schema import (
    RootModel,
    ScopeModel,
    ScopeOutputModel,
    UpdateScopeModel,
    User,
    SessionDep,
)

load_dotenv()

FRONTEND_ORIGINS = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    os.getenv("BACKEND_URL", "http://localhost:8000"),
    os.getenv("HOST_URL", "http://localhost"),
    os.getenv("WEBSOCKET_URL", "ws://localhost:8000"),
]

app = FastAPI(
    title="Sniper Game API",
    description="API for the Sniper Game backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class APIEndpointUrls:
    """Class containing API endpoint URLs as class variables."""

    ROOT = "/"
    CREATE_USER = "/create_user"
    GET_USERS = "/users"
    CREATE_SCOPE = "/create_scope"
    GET_SCOPES = "/scopes"
    WEBSOCKET_SCOPE = "/ws/scope/{scope_id}"


@app.get("/")
def read_root(
    session: SessionDep,
    offset: int = 0,
    limit: int = 100,
) -> RootModel:
    """
    Root endpoint that returns a welcome message.

    :return: A RootModel instance with a welcome message.
    :rtype: RootModel
    """
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    if not users:
        return RootModel(message="Welcome to the FastAPI application!")
    return RootModel(
        message="Welcome to the FastAPI application!", username=users[-1].name
    )


@app.post("/create_user", status_code=201)
def create_user(user: User, session: SessionDep) -> User:
    """
    Creates a new user in the database.

    :param user: The user to be created.
    :type user: User
    """
    existing_user = session.exec(
        select(User).where(User.name == user.name)
    ).one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this name already exists"
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users")
def get_users(
    session: SessionDep,
    offset: int = 0,
    limit: int = 100,
) -> list[User]:
    """
    Returns a list of all users in the database.

    :return: A list of User instances.
    :rtype: list[User]
    """
    return session.exec(select(User).offset(offset).limit(limit)).all()


@app.post("/create_scope", status_code=201)
def create_scope(scope: ScopeModel, session: SessionDep) -> ScopeModel:
    """
    Creates a new sniper scope with the given frequency, amplitude and phase.

    :param name: The name of the sniper scope.
    :type name: str
    :param frequency: The frequency of the sine wave in Hz.
    :type frequency: float
    :param amplitude: The amplitude of the sine wave.
    :type amplitude: float
    :param phase: The phase shift of the sine wave in radians (default is 0).
    :type phase: float
    """
    session.add(scope)
    session.commit()
    session.refresh(scope)
    return scope


@app.get("/scopes")
def get_scopes(
    session: SessionDep,
    offset: int = 0,
    limit: int = 100,
) -> list[ScopeModel]:
    """
    Returns a list of all sniper scopes in the database.

    :return: A list of ScopeModel instances.
    :rtype: list[ScopeModel]
    """
    return session.exec(select(ScopeModel).offset(offset).limit(limit)).all()


@app.websocket("/ws/scope/{scope_id}")
async def websocket_endpoint(
    websocket: WebSocket, scope_id: str, session: SessionDep
) -> None:
    """
    WebSocket endpoint for real-time scope updates.

    :param websocket: The WebSocket connection.
    :type websocket: WebSocket
    :param scope_id: The unique identifier for the sniper scope.
    :type scope_id: str
    """
    await websocket.accept()
    try:
        scope = session.exec(
            select(ScopeModel).where(ScopeModel.id == scope_id)
        ).one_or_none()
        if not scope:
            await websocket.send_json({"error": "Scope not found"})
            raise HTTPException(status_code=404, detail="Scope not found")
        frequency, amplitude, phase = (
            scope.frequency,
            scope.amplitude,
            scope.phase,
        )
        with new_scope(amplitude, phase) as generate_signal:
            signal_function = generate_signal(frequency)
            time_points = [0.001 * i for i in range(1000)]
            signal_values = [signal_function(t) for t in time_points]
            while True:
                result: UpdateScopeModel = await websocket.receive_json()
                await websocket.send_json(
                    ScopeOutputModel(
                        message="Real-time signal update",
                        frequency=result.frequency,
                        time_values=time_points,
                        signal_values=signal_values,
                    )
                )
    except HTTPException as e:
        print(f"HTTP error: {e.detail}")
    finally:
        await websocket.close()
