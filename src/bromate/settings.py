"""Settings for configuring the application."""

# %% IMPORTS

import pydantic as pdt
import pydantic_settings as pdts

from bromate import actions

# %% SETTINGS


class ModelSettings(pdt.BaseModel, frozen=True, strict=True, extra="forbid"):
    """Define settings for the model."""

    api_key: pdt.SecretStr | None = None
    name: str = "gemini-1.5-flash-latest"
    temperature: float = 0.0
    candidate_count: int = 1
    max_output_tokens: int = 1000
    system_instructions: str = "You are a browser automation bot. Your goal is to understand the user request and execute actions on its browser using the tools at your disposal."


class BrowserSettings(pdt.BaseModel, frozen=True, strict=True, extra="forbid"):
    """Define settings for the browser."""

    keep_alive: bool = True


class ActionsSettings(pdt.BaseModel, frozen=True, strict=True, extra="forbid"):
    """Define settings for all actions."""

    get: actions.get = actions.get()


class SessionSettings(pdt.BaseModel, frozen=True, strict=True, extra="forbid"):
    """Define settings for the session."""

    model: ModelSettings = ModelSettings()
    browser: BrowserSettings = BrowserSettings()
    actions: ActionsSettings = ActionsSettings()
    max_steps: int = 5
    continuation_message: str = "Continue the execution if necessary or return 'DONE'."
    interruption_message: str = "DONE"


class InterfaceSettings(pdt.BaseModel, frozen=True, strict=True, extra="forbid"):
    """Define settings for the interface."""


class ApplicationSettings(pdts.BaseSettings, strict=True, extra="forbid"):
    """Define settings for the application."""

    session: SessionSettings = SessionSettings()
    interface: InterfaceSettings = InterfaceSettings()
    # pydantic
    model_config = pdts.SettingsConfigDict(env_nested_delimiter="__", env_file=".env")
