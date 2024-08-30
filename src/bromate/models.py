"""Models for providing Generative AI capacities."""

# %% IMPORTS

import enum
import typing as T

import google.generativeai as genai

# %% ENUMS


class ContentRole(enum.StrEnum):
    """Role for the content."""

    USER = "user"
    MODEL = "model"


# %% ALIASES

# - Classes
Model: T.TypeAlias = genai.GenerativeModel
Config: T.TypeAlias = genai.GenerationConfig
Response: T.TypeAlias = genai.types.GenerateContentResponse
Function: T.TypeAlias = genai.protos.FunctionDeclaration
FunctionCall: T.TypeAlias = genai.protos.FunctionCall
FunctionType: T.TypeAlias = genai.protos.Type
FunctionParameter: T.TypeAlias = genai.protos.Schema
Part: T.TypeAlias = genai.protos.Part
Tool: T.TypeAlias = genai.protos.Tool
Content: T.TypeAlias = genai.protos.Content
# - Functions
configure = genai.configure
