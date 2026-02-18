import os
# from pathlib import Path
from fastapi import FastAPI

# import json
from typing import Generator
# from .schema import User
import psycopg
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_USER = os.environ.get("DATABASE_USER")

app = FastAPI()


@contextmanager
def get_db_connection() -> Generator[
    tuple[psycopg.Connection, psycopg.Cursor], None, None
]:
    with psycopg.connect(f"dbname={DATABASE_NAME} user={DATABASE_USER}") as conn:
        with conn.cursor() as cur:
            yield conn, cur


def execute_query(query: str, params: tuple = ()):
    with get_db_connection() as (conn, cur):
        cur.execute(query, params)
        conn.commit()


if __name__ == "__main__":
    app.run(debug=True)
