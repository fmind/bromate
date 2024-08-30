"""Actions for models to interact with browsers."""

# %% IMPORTS

import abc
import time
import typing as T

import pydantic as pdt

from bromate import browsers, models

# %% ACTIONS


class Action(pdt.BaseModel, abc.ABC, arbitrary_types_allowed=True, strict=True, extra="forbid"):
    """Base class for an action."""

    @property
    def name(self) -> str:
        """Return the action name."""
        return self.__class__.__name__

    @property
    def doc(self) -> str:
        """Return the action docstring."""
        if not self.__class__.__doc__:  # None or empty
            raise ValueError(f"Action doc is missing: {self.name}")
        return self.__class__.__doc__

    @abc.abstractmethod
    def tool(self) -> models.Tool:
        """Return the model tool declaration."""

    @abc.abstractmethod
    def __call__(self, *args: T.Any, **kwargs: T.Any) -> None:
        """Execute the code associated with the action."""


class get(Action):
    """Load a web page in the browser."""

    sleep_time: float = 1.0

    def tool(self) -> models.Tool:
        return models.Tool(
            function_declarations=[
                models.Function(
                    name=self.name,
                    description=self.doc,
                    parameters=models.FunctionParameter(
                        type=models.FunctionType.OBJECT,
                        properties={
                            "url": models.FunctionParameter(
                                type=models.FunctionType.STRING, description="URL to load"
                            )
                        },
                        required=["url"],
                    ),
                )
            ]
        )

    def __call__(self, browser: browsers.Browser, url: str) -> None:
        browser.get(url=url)  # wait loading
        time.sleep(self.sleep_time)
