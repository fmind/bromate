"""Define core types for the application."""

# %% IMPORTS

import pydantic as pdt

# %% CLASSES


class Data(pdt.BaseModel, extra="forbid", validate_assignment=True):
    """Base class for data."""


class MutableData(Data, frozen=False):
    """Base class for mutable data."""


class ImmutableData(Data, frozen=True):
    """Base class for immutable data."""


# %% ALIASES

Field = pdt.Field
