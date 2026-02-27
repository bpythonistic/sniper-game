"""
This module defines the data models for the application using Pydantic.

It includes:
- A User model with an auto-generated UUID and a name field.
"""

import os
from uuid import uuid4
from typing import Annotated, Generator

# from typing import Optional
from fastapi.params import Depends
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine

DEFAULT_CONNECTION_STRING = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres@localhost:5432/nyquist_db"
)


class User(SQLModel, table=True):
    """
    Docstring for User SQL model.

    :param id: The unique identifier for the user, auto-generated as a UUID.
    :type id: str
    :param name: The name of the user. This field is required.
    :type name: str
    """

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(default="Default User", index=True)


class RootModel(BaseModel):
    """
    Docstring for RootModel.

    :param message: A welcome message for the API.
        This is set to "Welcome to the FastAPI application!" by default.
    :type message: str
    :param username: The username of the default user.
        This is set to "Default User" if no users are found in the database.
    :type username: str
    """

    message: str = "Welcome to the FastAPI application!"
    username: str = "Default User"


class ScopeModel(SQLModel, table=True):
    """
    Docstring for ScopeModel.

    :param id: The unique identifier for the sniper scope.
    :type id: str
    :param name: The name of the sniper scope. This field is required.
    :type name: str
    :param frequency: The frequency of the sine wave in Hz.
    :type frequency: float
    :param amplitude: The amplitude of the sine wave.
    :type amplitude: float
    :param phase: The phase shift of the sine wave in radians (default is 0).
    :type phase: float
    """

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    frequency: float = Field(..., index=True)
    amplitude: float = Field(..., index=True)
    phase: float = Field(default=0.0, index=True)


class UpdateScopeModel(BaseModel):
    """
    Docstring for UpdateScopeModel.

    :param scope_id: The unique identifier for the sniper scope to be updated.
    :type scope_id: str
    :param frequency: The new frequency of the sine wave in Hz.
    :type frequency: float
    """

    scope_id: str
    frequency: float


class ScopeOutputModel(BaseModel):
    """
    Docstring for ScopeOutputModel.

    :param message: A message indicating
        the status of the sniper scope signal generation.
    :type message: str
    :param frequency: The frequency of the sine wave in Hz.
    :type frequency: float
    :param time_values: A list of time values
        corresponding to the generated sniper scope signal.
    :type time_values: list[float]
    :param signal_values: The generated sniper scope signal as a list of float values.
    :type signal_values: list[float]
    """

    message: str
    frequency: float
    time_values: list[float]
    signal_values: list[float]


def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database connection.

    This function creates a connection to the database and yields a session object for executing queries.
    It ensures that the connection is properly closed after use.

    :yield: A tuple containing the database session and the session object itself.
    :rtype: Generator[tuple[Session, Session], None, None]
    """
    engine = create_engine(DEFAULT_CONNECTION_STRING)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
