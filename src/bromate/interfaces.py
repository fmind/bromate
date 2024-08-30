"""Interfaces for interacting with the application."""

# %% IMPORTS

import typing as T

import pydantic as pdt
from loguru import logger

from bromate import models
from bromate.settings import InterfaceSettings

# %% INTERFACES


class Interface(pdt.BaseModel, arbitrary_types_allowed=True, strict=True, extra="forbid"):
    """Interface for displaying the application"""

    settings: InterfaceSettings

    @classmethod
    def from_settings(cls, interface_settings: InterfaceSettings) -> "Interface":
        """Create an interface from settings."""
        logger.info("Creating interface: {}", interface_settings)
        return Interface(settings=interface_settings)

    def interact(self, execution: T.Generator[list[models.Content], None, None]) -> None:
        """Interact with the user given a session and query."""
        for contents in execution:
            user_content, model_content = contents[-2], contents[-1]
            print(f"- {user_content.role.upper()}: {user_content.parts[0].text}")
            print(f"- {model_content.role.upper()}: {model_content.parts[0].text}")
