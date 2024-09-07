"""Execute the main logic of the application."""

# %% IMPORTS

import typing as T

from loguru import logger

from bromate import actions, agents, drivers, types

# %% CLASSES


class ExecutionConfig(types.ImmutableData):
    """Config of the execution."""

    stop_actions: list[str] = types.Field(
        default=[actions.done.__name__],
        description="Name of actions that can stop the execution",
    )
    default_message: str = types.Field(
        default=f"Continue the execution if necessary or call the {actions.done.__name__} tool",
        description="Default message to send to the agent when no input is provided by the user",
    )


# %% ALIASES

Execution: T.TypeAlias = T.Generator[agents.Content, str | None, agents.Content]

# %% FUNCTIONS


def execute(
    query: str,
    agent: agents.Agent,
    driver: drivers.Driver,
    config: ExecutionConfig,
    action_config: actions.ActionConfig,
    agent_tools: list[agents.Tool] = actions.TOOLS,
) -> Execution:
    """Execute a query given a config."""
    # contents
    query_content = agents.Content(role=agents.Role.USER.value, parts=[agents.Part(text=query)])
    contents = [query_content]
    # steps
    while True:
        done = False
        # response
        response = agent.generate_content(contents=contents, tools=agent_tools)
        # feedback
        if feedback := response.prompt_feedback:
            logger.warning("Agent feedback: {}", feedback)
        # usage
        if usage := response.usage_metadata:
            logger.debug(
                "Agent usage: total tokens={}, input tokens={}, output tokens={}",
                usage.total_token_count,
                usage.prompt_token_count,
                usage.candidates_token_count,
            )
        # parts
        parts = []
        for i, part in enumerate(response.parts, start=1):
            logger.debug("## Agent response part {}: {}", i, str(part).strip())
            if call := part.function_call:
                name, kwargs = call.name, call.args
                kwargs_text = ", ".join(f"{key}={val}" for key, val in kwargs.items())
                calling_text = f"Calling tool: {name}({kwargs_text})"
                if action := getattr(actions, name):
                    action(driver=driver, config=action_config, **kwargs)
                else:
                    raise ValueError(f"Cannot execute action (unknown action name): {name}!")
                if name in config.stop_actions:
                    done = True  # stop execution
                part = agents.Part(text=calling_text)
                parts.append(part)
            elif text := part.text:
                parts.append(agents.Part(text=text.strip()))
            else:
                raise ValueError(f"Cannot handle agent response (unknown part type): {part}!")
        # output
        agent_content = agents.Content(role=agents.Role.AGENT.value, parts=parts)
        if done is True:
            return agent_content
        contents.append(agent_content)
        user_input = yield agent_content
        user_text = user_input or config.default_message
        # input
        user_content = agents.Content(
            role=agents.Role.USER.value, parts=[agents.Part(text=user_text)]
        )
        contents.append(user_content)
