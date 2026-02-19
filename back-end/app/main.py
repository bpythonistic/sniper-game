"""
This module defines the main FastAPI application and database connection utilities.

It includes:
- A FastAPI application instance.
- A context manager for database connections.
"""

import os
from contextlib import contextmanager
from typing import Generator

# from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# import json
import psycopg
from dotenv import load_dotenv
from schema import User, RootModel

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
        f"dbname={DATABASE_NAME} user={DATABASE_USER} password={os.getenv('DATABASE_PASSWORD')}"
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


def execute_fetch_query(query: str, params: tuple = ()) -> Generator[tuple, None, None]:
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
    query = "CREATE TABLE IF NOT EXISTS users (id UUID PRIMARY KEY, name TEXT NOT NULL)"
    execute_write_query(query)
    query = "SELECT id, name FROM users LIMIT 1"
    users = list(execute_fetch_query(query))
    default_user = (
        User(id=users[0][0], name=users[0][1]) if users else User(name="Default User")
    )
    return RootModel(message="Welcome to the FastAPI application!", user=default_user)


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
