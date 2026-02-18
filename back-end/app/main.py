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
from fastapi import FastAPI

# import json
import psycopg
from dotenv import load_dotenv
# from .schema import User

load_dotenv()

DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_USER = os.environ.get("DATABASE_USER")

app = FastAPI()


@contextmanager
def get_db_connection() -> Generator[
    tuple[psycopg.Connection, psycopg.Cursor], None, None
]:
    """
    Context manager for database connection.

    :return: A generator yielding a tuple of (Connection, Cursor).
    :rtype: Generator[tuple[psycopg.Connection, psycopg.Cursor], None, None]
    """
    with psycopg.connect(f"dbname={DATABASE_NAME} user={DATABASE_USER}") as conn:
        with conn.cursor() as cur:
            yield conn, cur


def execute_query(query: str, params: tuple = ()):
    """
    Executes a SQL query with the given parameters.

    :param query: The SQL query to execute.
    :type query: str
    :param params: The parameters to pass to the SQL query.
    :type params: tuple
    """
    with get_db_connection() as (conn, cur):
        cur.execute(query, params)
        conn.commit()
