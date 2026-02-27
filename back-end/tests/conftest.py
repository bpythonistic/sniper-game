"""This file contains fixtures for testing the FastAPI application.

It sets up a test database, creates a test client, and provides a fixture for an authenticated user.
The fixtures ensure that each test runs in isolation with a clean database state.
"""

from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from yaml import safe_load

import app.schema as sch
from app.main import app

CONFIG_FILE_PATH = Path(__file__).parent / "testdata" / "testconfig.yaml"


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Creates a fresh, in-memory SQLite database for every single test.
    Using StaticPool ensures all threads share this exact connection.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables fresh
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    # Teardown
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Creates a TestClient that intercepts the API's database calls and
    forces them to use our in-memory test session.
    """

    def get_session_override():
        return session

    # Force the FastAPI app to use our test session
    app.dependency_overrides[sch.get_session] = get_session_override

    client = TestClient(app)
    yield client

    # Clean up overrides after the test
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def config() -> dict:
    """
    Fixture for loading test data from a YAML file.

    :return: A dictionary containing the test data.
    :rtype: dict
    """
    with open(CONFIG_FILE_PATH, "r") as f:
        data = safe_load(f)["data"]
    return data
