"""Provide agentic features to the application."""

# %% IMPORTS

import enum
import os
import typing as T

import google.generativeai as genai
import pydantic as pdt

from bromate import types

# %% ENUMS


class Role(enum.StrEnum):
    """Content role."""

    AGENT = "model"
    USER = "user"


# %% CLASSES


class AgentConfig(types.ImmutableData):
    """Config for the agent."""

    api_key: pdt.SecretStr | None = types.Field(
        default=pdt.SecretStr(secret_value=os.environ["GOOGLE_API_KEY"])
        if "GOOGLE_API_KEY" in os.environ
        else None,
        description="API key of the agent platform (Google)",
    )
    name: str = types.Field(
        default="gemini-1.5-flash-latest", description="Name of the agent to use"
    )
    temperature: float = types.Field(default=0.0, description="Temperature of the agent")
    candidate_count: pdt.PositiveInt = types.Field(
        default=1, description="Number of candidates to generate"
    )
    max_output_tokens: pdt.PositiveInt = types.Field(
        default=1000, description="Maximum output tokens to generate"
    )
    system_instructions: str = types.Field(
        default="You are a browser automation system. Your goal is to understand the user request and execute actions on its browser using the tools at your disposal. After each step, you will receive a screenshot and the page source of the current browser window."
        "",
        description="System instructions for the agent",
    )


# %% ALIASES

Agent: T.TypeAlias = genai.GenerativeModel
Blob: T.TypeAlias = genai.protos.Blob
Call: T.TypeAlias = genai.protos.FunctionCall
Content: T.TypeAlias = genai.protos.Content
Function: T.TypeAlias = genai.protos.FunctionDeclaration
GenerationConfig: T.TypeAlias = genai.GenerationConfig
Part: T.TypeAlias = genai.protos.Part
Response: T.TypeAlias = genai.types.GenerateContentResponse
Schema: T.TypeAlias = genai.protos.Schema
Structure: T.TypeAlias = genai.protos.FunctionResponse
Tool: T.TypeAlias = genai.protos.Tool
Type: T.TypeAlias = genai.protos.Type

# %% FUNCTIONS


def init_agent_from_config(config: AgentConfig) -> Agent:
    """Initialize a model from config."""
    api_key = config.api_key.get_secret_value() if config.api_key else None
    genai.configure(api_key=api_key)  # global assignment!
    gen_config = GenerationConfig(
        temperature=config.temperature,
        candidate_count=config.candidate_count,
        max_output_tokens=config.max_output_tokens,
    )
    model = Agent(
        model_name=config.name,
        generation_config=gen_config,
        system_instruction=config.system_instructions,
    )
    return model
