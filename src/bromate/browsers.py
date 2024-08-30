"""Browsers for communicating through web drivers."""

# %% IMPORTS

import typing as T

import selenium.webdriver as wd

# %% ALIASES

Browser: T.TypeAlias = wd.Chrome
Options: T.TypeAlias = wd.ChromeOptions
Service: T.TypeAlias = wd.ChromeService
