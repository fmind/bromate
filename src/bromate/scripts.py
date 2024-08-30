"""Scripts of the application."""

# %% IMPORTS

import argparse

import bromate
from bromate import interfaces, sessions, settings

# %% PARSERS

parser = argparse.ArgumentParser(description=bromate.__doc__)
parser.add_argument("query", help="Automation query to execute")

# %% SCRIPTS


def main(argv: list[str] | None = None) -> int:
    """Run the main script function."""
    # arguments
    args = parser.parse_args(args=argv)
    query = args.query
    # settings
    app_settings = settings.ApplicationSettings()
    session_settings = app_settings.session
    interface_settings = app_settings.interface
    # session
    session = sessions.Session.from_settings(session_settings=session_settings)
    # interface
    interface = interfaces.Interface.from_settings(interface_settings=interface_settings)
    # execution
    execution = session.execute(query=query)
    # interaction
    interface.interact(execution=execution)
    return 0
