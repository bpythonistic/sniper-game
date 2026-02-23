"""This file contains tests for the main application functionality.

It includes tests for:
- Database connection - Sniper scope signal generation
- WebSocket communication
- API endpoints
- User authentication and management
"""

from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from yaml import safe_load

import app.schema as sch
from app.main import (
    APIEndpointUrls,
    app,
    get_db_connection,
    execute_write_query,
)

CONFIG_FILE_PATH = Path(__file__).parent / "testdata" / "testconfig.yaml"


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Fixture for creating a TestClient instance for testing the FastAPI application.

    :return: A TestClient instance for the FastAPI application.
    :rtype: TestClient
    """
    with TestClient(app) as client:
        yield client


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


@pytest.fixture(scope="module")
def replace_db_connection(monkeypatch: pytest.MonkeyPatch, postgresql) -> None:
    """
    Monkey patch the get_db_connection function to use a test database connection.

    This fixture replaces the get_db_connection function with a version that connects to a test database.
    It ensures that tests do not affect the production database and allows for isolated testing of database interactions.
    """
    monkeypatch.setattr(
        "app.main.get_db_connection",
        lambda: get_db_connection(cur_override=postgresql.cursor()),
    )


@pytest.fixture(scope="module")
def database(replace_db_connection) -> None:
    """
    Fixture for setting up the test database.

    This fixture ensures that the test database is set up and ready for use in tests that require database interactions.
    It relies on the replace_db_connection fixture to ensure that all database connections during testing are directed to the test database.
    """
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )"""
    execute_write_query(query)
    query = (
        "CREATE TABLE IF NOT EXISTS scopes (id TEXT PRIMARY KEY, "
        "(id TEXT NOT NULL, name TEXT NOT NULL), "
        "frequency FLOAT NOT NULL, amplitude FLOAT NOT NULL, "
        "phase FLOAT NOT NULL)"
    )
    execute_write_query(query)


type DataModel = tuple[list[sch.User], list[sch.ScopeModel]]


@pytest.fixture(scope="module")
def database_contents(client, request, database) -> DataModel:
    """
    Fixture for returning a database state based on the data fixture.
    """
    marker = request.node.get_closest_marker("data")
    if marker is None:
        pytest.fail("No data marker found for database_contents fixture")
    users_in, scopes_in = marker.args[0]

    def add_users(users_arg: list[sch.User]) -> None:
        for user in users_arg:
            response = client.post(
                APIEndpointUrls.USERS,
                json={
                    "id": user.id,
                    "name": user.name,
                },
            )
        assert response.status_code == 201
        assert response.json()["name"] == user.name

    def add_scopes(scopes_arg: list[sch.ScopeModel]) -> None:
        for scope in scopes_arg:
            response = client.post(
                APIEndpointUrls.CREATE_SCOPE,
                json={
                    "id": scope.id,
                    "user": {
                        "id": scope.user.id,
                        "name": scope.user.name,
                    },
                    "frequency": scope.frequency,
                    "amplitude": scope.amplitude,
                    "phase": scope.phase,
                },
            )
        assert response.status_code == 201
        assert response.json()["frequency"] == scope.frequency

    add_users(users_in)
    add_scopes(scopes_in)

    response = client.get(
        APIEndpointUrls.GET_USERS,
    )

    assert response.status_code == 200
    users_out = [sch.User(**user) for user in response.json()]

    response = client.get(
        APIEndpointUrls.GET_SCOPES,
    )
    assert response.status_code == 200
    scopes_out = [sch.ScopeModel(**scope) for scope in response.json()]

    return users_out, scopes_out


def test_db_connection(database) -> None:
    """
    Test the database connection.

    This test checks if a connection to the database can be established successfully.
    It uses the get_db_connection context manager to attempt a connection and asserts that it is successful.
    """
    try:
        with get_db_connection() as (conn, cursor):
            assert conn is not None
            assert cursor is not None
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")


class TestEndpoints:
    """
    Test class for API endpoints.

    This class contains tests for the API endpoints defined in the FastAPI application.
    Each test method corresponds to a specific endpoint and checks the expected behavior of that endpoint.
    """

    @pytest.mark.parametrize(
        "data,output_message,output_user_name",
        [
            (([], []), "Welcome to the FastAPI application!", "Default User"),
            (
                ([sch.User(name="Test User")], []),
                "Welcome to the FastAPI application!",
                "Test User",
            ),
        ],
    )
    @pytest.mark.data("data")
    def test_root_endpoint(
        self,
        client: TestClient,
        database_contents: DataModel,
        output_message: str,
        output_user_name: str,
    ) -> None:
        """
        Test the root endpoint of the API.

        :param client: The TestClient instance for making requests to the API.
        :type client: TestClient
        :param config: The test data loaded from the YAML file.
        :type config: dict
        """
        response = client.get(APIEndpointUrls.ROOT)
        assert response.status_code == 200
        data = response.json()
        data = sch.RootModel(**data)
        assert data.message == output_message
        if database_contents[0]:
            assert database_contents[0][-1].name == output_user_name
        assert data.user.name == output_user_name

    @pytest.mark.parametrize(
        "data",
        [
            ([sch.User(name="John Doe")], []),
            ([sch.User(name="Jane Smith")], []),
            ([sch.User(name="Sally Mae")], []),
            (
                [
                    sch.User(name="John Doe"),
                    sch.User(name="Jane Smith"),
                    sch.User(name="Sally Mae"),
                ],
                [],
            ),
        ],
    )
    @pytest.mark.data("data")
    def test_create_user_endpoint(
        self, database_contents: DataModel, data: DataModel
    ) -> None:
        """Test the create_user endpoint of the API.

        :param database_contents: The current state of the database after setup.
        :type database_contents: DataModel
        :param data: The test data for creating users, provided by the data fixture.
        :type data: DataModel
        """
        assert database_contents[0] == data[0]
