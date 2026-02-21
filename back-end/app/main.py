"""
This module defines the main FastAPI application and database connection utilities.

It includes:
- A FastAPI application instance.
- A context manager for database connections.
"""

# import os
from contextlib import contextmanager
from typing import Generator

# import json
import psycopg
from dotenv import load_dotenv

# from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.features.signal_generator import new_scope
from app.schema import (
    RootModel,
    ScopeModel,
    ScopeOutputModel,
    User,
)

load_dotenv()

DATABASE_NAME = "nyquist_db"
DATABASE_USER = "postgres"

app = FastAPI(
    title="Sniper Game API",
    description="API for the Sniper Game backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost",
        "ws://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def get_db_connection() -> Generator[
    tuple[psycopg.Connection, psycopg.Cursor], None, None
]:
    """
    Context manager for database connection.

    :return: A generator yielding a tuple of (Connection, Cursor).
    :rtype: Generator[tuple[psycopg.Connection, psycopg.Cursor], None, None]
    """
    with psycopg.connect(
        f"dbname={DATABASE_NAME} user={DATABASE_USER} host=localhost"
    ) as conn:
        with conn.cursor() as cur:
            yield conn, cur


def execute_write_query(query: str, params: tuple = ()):
    """
    Executes a SQL query that modifies data with the given parameters.

    :param query: The SQL query to execute.
    :type query: str
    :param params: The parameters to pass to the SQL query.
    :type params: tuple
    """
    with get_db_connection() as (conn, cur):
        cur.execute(query, params)
        conn.commit()


def execute_fetch_query(
    query: str, params: tuple = ()
) -> Generator[tuple, None, None]:
    """
    Executes a SQL query that retrieves data with the given parameters.

    :param query: The SQL query to execute.
    :type query: str
    :param params: The parameters to pass to the SQL query.
    :type params: tuple
    :return: The fetched results from the database.
    :rtype: list
    """
    with get_db_connection() as (conn, cur):
        cur.execute(query, params)
        yield from cur.fetchall()
        conn.commit()


@app.get("/")
def read_root() -> RootModel:
    """
    Root endpoint that returns a welcome message.

    :return: A RootModel instance with a welcome message.
    :rtype: RootModel
    """
    query = "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT NOT NULL)"
    execute_write_query(query)
    query = "SELECT id, name FROM users"
    users = list(execute_fetch_query(query))
    default_user = (
        User(id=users[-1][0], name=users[-1][1])
        if users
        else User(name="Default User")
    )
    return RootModel(
        message="Welcome to the FastAPI application!", user=default_user
    )


@app.post("/create_user", status_code=201)
def create_user(user: User) -> User:
    """
    Creates a new user in the database.

    :param user: The user to be created.
    :type user: User
    """
    query = "INSERT INTO users (id, name) VALUES (%s, %s)"
    execute_write_query(query, (user.id, user.name))
    query = "SELECT id, name FROM users WHERE id = %s"
    for row in execute_fetch_query(query, (user.id,)):
        if row[0] == user.id:
            return User(id=row[0], name=row[1])
    raise HTTPException(status_code=404, detail="User not found after creation")


@app.get("/users")
def get_users() -> list[User]:
    """
    Returns a list of all users in the database.

    :return: A list of User instances.
    :rtype: list[User]
    """
    query = "SELECT id, name FROM users"
    return [User(id=row[0], name=row[1]) for row in execute_fetch_query(query)]


@app.post("/create_scope", status_code=201)
def create_scope(scope: ScopeModel) -> ScopeModel:
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
    query = (
        "CREATE TABLE IF NOT EXISTS scopes (id TEXT PRIMARY KEY, "
        "(id TEXT NOT NULL, name TEXT NOT NULL), "
        "frequency FLOAT NOT NULL, amplitude FLOAT NOT NULL, "
        "phase FLOAT NOT NULL)"
    )
    execute_write_query(query)
    query = (
        "INSERT INTO scopes (id, (id, name), frequency, "
        "amplitude, phase) VALUES (%s, %s, %s, %s, %s, %s)"
    )
    execute_write_query(
        query,
        (
            scope.id,
            (scope.user.id, scope.user.name),
            scope.frequency,
            scope.amplitude,
            scope.phase,
        ),
    )
    query = (
        "SELECT id, user, frequency, amplitude, phase FROM scopes WHERE id = %s"
    )
    for row in execute_fetch_query(query, (scope.id,)):
        if row[0] == scope.id:
            return ScopeModel(
                id=row[0],
                user=User(id=row[1][0], name=row[1][1]),
                frequency=row[2],
                amplitude=row[3],
                phase=row[4],
            )
    raise HTTPException(
        status_code=404, detail="Scope not found after creation"
    )


@app.get("/scopes")
def get_scopes() -> list[ScopeModel]:
    """
    Returns a list of all sniper scopes in the database.

    :return: A list of ScopeModel instances.
    :rtype: list[ScopeModel]
    """
    query = "SELECT id, user, frequency, amplitude, phase FROM scopes"
    return [
        ScopeModel(
            id=row[0],
            user=User(id=row[1][0], name=row[1][1]),
            frequency=row[2],
            amplitude=row[3],
            phase=row[4],
        )
        for row in execute_fetch_query(query)
    ]


@app.websocket("/ws/scope/{scope_id}")
async def websocket_endpoint(websocket: WebSocket, scope_id: str):
    """
    WebSocket endpoint for real-time scope updates.

    :param websocket: The WebSocket connection.
    :type websocket: WebSocket
    :param scope_id: The unique identifier for the sniper scope.
    :type scope_id: str
    """
    await websocket.accept()
    try:
        query = "SELECT frequency, amplitude, phase FROM scopes WHERE id = %s"
        result = list(execute_fetch_query(query, (scope_id,)))
        if not result:
            await websocket.send_json({"error": "Scope not found"})
            raise HTTPException(status_code=404, detail="Scope not found")
        frequency, amplitude, phase = result[0]
        with new_scope(amplitude, phase) as generate_signal:
            signal_function = generate_signal(frequency)
            time_points = [0.001 * i for i in range(1000)]
            signal_values = [signal_function(t) for t in time_points]
            while True:
                result: dict = await websocket.receive_json()
                await websocket.send_json(
                    ScopeOutputModel(
                        message="Real-time signal update",
                        frequency=result.get("frequency", frequency),
                        time_values=time_points,
                        signal_values=signal_values,
                    )
                )
    except HTTPException as e:
        print(f"HTTP error: {e.detail}")
    finally:
        await websocket.close()
