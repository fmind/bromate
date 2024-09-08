"""Interact with the user and the application."""

# %% IMPORTS

import typing as T

import pydantic as pdt

from bromate import agents, executions, types

# %% CLASSES


class InteractionConfig(types.ImmutableData):
    """Config for the interaction."""

    stay_open: bool = types.Field(default=True, description="Keep the browser open before exiting")
    interactive: bool = types.Field(
        default=False, description="Ask for user input after every action"
    )
    max_interactions: pdt.PositiveInt = types.Field(
        default=5, description="Maximum number of interactions for the agent"
    )


# %% ALIASES

Interaction: T.TypeAlias = T.Callable[[executions.Execution], None]

# %% FUNCTIONS


def display(content: agents.Content) -> None:
    """Display agent content to the user."""
    texts: list[str] = []
    for part in content.parts:
        if text := part.text:
            texts.append(text)
        elif call := part.function_call:
            name, kwargs = call.name, call.args
            kwargs_text = ", ".join(f"{key}={val}" for key, val in kwargs.items())
            calling_text = f"Calling tool: {name}({kwargs_text})"
            texts.append(calling_text)
        else:
            raise ValueError(f"Cannot display agent content (unknown agent part): {part}!")
    print(f"> AGENT: {' & '.join(texts)}", flush=True)


def interact(execution: executions.Execution, config: InteractionConfig) -> int:
    """Interact with the user given a config."""
    try:
        interaction_count = 0
        # start the execution
        content = next(execution)
        display(content=content)
        # continue the execution
        while interaction_count < config.max_interactions:
            if config.interactive is True:
                input_text = input("< USER: ")
            else:
                input_text = None
            content = execution.send(input_text)
            display(content=content)
            interaction_count += 1
        # stop the execution
    except StopIteration as stop:
        # returned value
        content = stop.value
        display(content=content)
    # leave the browser open?
    if config.stay_open is True:
        input("\nPress enter to exit...")
    return 0
