"""Interact with web drivers using agent tools."""

# %% IMPORTS

import time

import pydantic as pdt

from bromate import agents, drivers, types

# %% CLASSES


class ActionConfig(types.ImmutableData):
    """Config for all actions."""

    sleep_time: pdt.PositiveFloat = types.Field(
        default=1.0, description="Time to sleep after loading a page"
    )


# %% FUNCTIONS


def get(driver: drivers.Driver, config: ActionConfig, url: str) -> None:
    """Load a web page in the current browser tab."""
    driver.get(url=url)  # wait loading
    time.sleep(config.sleep_time)


get_tool = agents.Tool(
    function_declarations=[
        agents.Function(
            name=get.__name__,
            description=get.__doc__,
            parameters=agents.Schema(
                type=agents.Type.OBJECT,
                properties={
                    "url": agents.Schema(
                        type=agents.Type.STRING, description="URL of the web page to load"
                    )
                },
                required=["url"],
            ),
        )
    ]
)


def done(driver: drivers.Driver, config: ActionConfig) -> None:
    """Call this when no further action is required."""
    pass


done_tool = agents.Tool(
    function_declarations=[
        agents.Function(
            name=done.__name__,
            description=done.__doc__,
        )
    ]
)

# %% REGISTERS

TOOLS = [get_tool, done_tool]
