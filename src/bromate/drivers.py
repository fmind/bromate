"""Communicate with web browsers through drivers."""

# %% IMPORTS

import typing as T

import selenium.webdriver as wd

from bromate import types

# %% CLASSES


class DriverConfig(types.ImmutableData):
    """Config for the driver."""

    name: T.Literal["Chrome", "Firefox"] = types.Field(
        default="Chrome", description="Name of the driver to use"
    )
    keep_alive: bool = types.Field(
        default=True, description="Keep the browser open at the end of the execution"
    )


# %% ALIASES

Driver: T.TypeAlias = wd.Chrome | wd.Firefox

# %% FUNCTIONS


def init_driver_from_config(config: DriverConfig) -> Driver:
    """Initialize the driver from config."""
    if config.name == "Chrome":
        return wd.Chrome(
            options=wd.ChromeOptions(),
            service=wd.ChromeService(),
            keep_alive=config.keep_alive,
        )
    elif config.name == "Firefox":
        return wd.Firefox(
            options=wd.FirefoxOptions(),
            service=wd.FirefoxService(),
            keep_alive=config.keep_alive,
        )
    else:
        raise ValueError(
            f"Cannot initialize driver from config (unknown driver name): {config.name}!"
        )
