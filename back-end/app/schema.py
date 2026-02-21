"""
This module defines the data models for the application using Pydantic.

It includes:
- A User model with an auto-generated UUID and a name field.
"""

from uuid import uuid4

# from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """
    Docstring for User model.

    :param id: The unique identifier for the user, auto-generated as a UUID.
    :type id: str
    :param name: The name of the user. This field is required.
    :type name: str
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "Default User"


class RootModel(BaseModel):
    """
    Docstring for RootModel.

    :param message: A welcome message for the API.
    :type message: str
    :param user: A User object representing the default user.
    :type user: User
    """

    message: str = "Welcome to the FastAPI application!"
    user: User


class ScopeModel(BaseModel):
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

    id: str = Field(default_factory=lambda: str(uuid4()))
    user: User
    frequency: float
    amplitude: float
    phase: float = 0.0


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
    Docstring for ScopeOutputWSModel.

    :param message: A message indicating the status of the sniper scope signal generation.
    :type message: str
    :param frequency: The frequency of the sine wave in Hz.
    :type frequency: float
    :param time_values: A list of time values corresponding to the generated sniper scope signal.
    :type time_values: list[float]
    :param signal_values: The generated sniper scope signal as a list of float values.
    :type signal_values: list[float]
    """

    message: str
    frequency: float
    time_values: list[float]
    signal_values: list[float]
