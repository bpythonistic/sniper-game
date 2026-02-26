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
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from yaml import safe_load

import app.schema as sch
from app.main import (
    APIEndpointUrls,
    app,
)

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


class DataPair(BaseModel):
    """Class representing a pair of input data and expected output for testing API endpoints.

    :param expected_code: The expected HTTP status code from the API endpoint test.
    :type expected_code: int
    """

    expected_code: int = status.HTTP_201_CREATED


class UserPair(DataPair):
    """Class representing a pair of input data and expected output for testing user-related API endpoints.

    :param input_data: The input data for the user-related API endpoint test, containing a User instance.
    :type input_data: dict
    :param expected_code: The expected HTTP status code from the user-related API endpoint test.
    :type expected_code: int
    """

    input_data: sch.User


class ScopePair(DataPair):
    """Class representing a pair of input data and expected output for testing scope-related API endpoints.

    :param input_data: The input data for the scope-related API endpoint test, containing a ScopeModel instance.
    :type input_data: dict
    :param expected_code: The expected HTTP status code from the scope-related API endpoint test.
    :type expected_code: int
    """

    input_data: sch.ScopeModel


class DataModel(BaseModel):
    """Class representing the test data for API endpoint tests.

    :param users: A list of User instances to be added to the database for testing.
    :type users: list[sch.User]
    :param scopes: A list of ScopeModel instances to be added to the database for testing
    :type scopes: list[sch.ScopeModel]
    :param expected_status: An instance of ExpectedStatus containing the expected status codes for API responses
    :type expected_status: ExpectedStatus
    """

    users: list[UserPair] = []
    scopes: list[ScopePair] = []


@pytest.fixture(scope="function")
def database_setup(client: TestClient, request: pytest.FixtureRequest) -> DataModel:
    """
    Fixture for returning a database state based on the data fixture.
    """
    data: DataModel = request.param
    users_in, scopes_in = data.users, data.scopes

    def add_users(users_arg: list[UserPair]):
        for user in users_arg:
            response = client.post(
                APIEndpointUrls.CREATE_USER,
                json={
                    "id": user.input_data.id,
                    "name": user.input_data.name,
                },
            )
            assert response.status_code == user.expected_code

    def add_scopes(scopes_arg: list[ScopePair]):
        for scope in scopes_arg:
            response = client.post(
                APIEndpointUrls.CREATE_SCOPE,
                json={
                    "id": scope.input_data.id,
                    "user_id": scope.input_data.user_id,
                    "frequency": scope.input_data.frequency,
                    "amplitude": scope.input_data.amplitude,
                    "phase": scope.input_data.phase,
                },
            )
            assert response.status_code == scope.expected_code

    add_users(users_in)
    add_scopes(scopes_in)
    return data


class TestEndpoints:
    """
    Test class for API endpoints.

    This class contains tests for the API endpoints defined in the FastAPI application.
    Each test method corresponds to a specific endpoint and checks the expected behavior of that endpoint.
    """

    @pytest.mark.parametrize(
        "database_setup,output_message",
        [
            (
                DataModel(users=[], scopes=[]),
                "Welcome to the FastAPI application!",
            ),
            (
                DataModel(
                    users=[UserPair(input_data=sch.User(name="Test User"))],
                    scopes=[],
                ),
                "Welcome to the FastAPI application!",
            ),
        ],
        indirect=["database_setup"],
    )
    def test_root_endpoint(
        self,
        client: TestClient,
        database_setup: DataModel,
        output_message: str,
    ) -> None:
        """
        Test the root endpoint of the API.

        :param client: The TestClient instance for making requests to the API.
        :type client: TestClient
        :param database_setup: The current state of the database after setup.
        :type database_setup: DataModel
        :param output_message: The expected message in the API response.
        :type output_message: str
        """
        response = client.get(APIEndpointUrls.ROOT)
        assert response.status_code == status.HTTP_200_OK
        output = response.json()
        output = sch.RootModel(**output)
        assert output.message == output_message
        assert output.username == (
            database_setup.users[-1].input_data.name
            if database_setup.users
            else "Default User"
        )

    @pytest.mark.parametrize(
        "database_setup",
        [
            DataModel(
                users=[UserPair(input_data=sch.User(name="John Doe"))],
                scopes=[],
            ),
            DataModel(
                users=[
                    UserPair(input_data=sch.User(name="Sally Mae")),
                    UserPair(
                        input_data=sch.User(name="Sally Mae"),
                        expected_code=status.HTTP_400_BAD_REQUEST,
                    ),
                ],
                scopes=[],
            ),
            DataModel(
                users=[
                    UserPair(input_data=sch.User(name="John Doe")),
                    UserPair(input_data=sch.User(name="Jane Smith")),
                    UserPair(input_data=sch.User(name="Sally Mae")),
                ],
                scopes=[],
            ),
        ],
        indirect=True,
    )
    def test_create_user_endpoint(
        self, client: TestClient, database_setup: DataModel
    ) -> None:
        """Test the create_user endpoint of the API.

        :param client: The TestClient instance for making requests to the API.
        :type client: TestClient
        :param database_setup: The current state of the database after setup.
        :type database_setup: DataModel
        """
        response = client.get(APIEndpointUrls.GET_USERS)
        assert response.status_code == status.HTTP_200_OK
        output = response.json()
        output = [sch.User(**user) for user in output]
        expected_users = [
            user.input_data
            for user in database_setup.users
            if user.expected_code == status.HTTP_201_CREATED
        ]
        assert len(output) == len(expected_users)
        for user in expected_users:
            assert any(user.name == output_user.name for output_user in output)
