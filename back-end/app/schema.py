"""
This module defines the data models for the application using Pydantic.

It includes:
- A User model with an auto-generated UUID and a name field.
"""

from uuid import uuid4, UUID

# from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """
    Docstring for User model.

    :param id: The unique identifier for the user, auto-generated as a UUID.
    :type id: UUID
    :param name: The name of the user. This field is required.
    :type name: str
    """

    id: UUID = Field(..., default_factory=uuid4)
    name: str


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
