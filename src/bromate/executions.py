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
        default=f"Continue the execution if necessary or call the {actions.done.__name__} tool if you are done",
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
    agent_functions: list[agents.Function] = actions.AGENT_FUNCTIONS,
) -> Execution:
    """Execute a query given a config."""
    # contents
    query_content = agents.Content(role=agents.Role.USER.value, parts=[agents.Part(text=query)])
    contents = [query_content]
    # tools
    agent_tool = agents.Tool(function_declarations=agent_functions)
    tools = [agent_tool]
    # steps
    while True:
        done = False
        # response
        response = agent.generate_content(contents=contents, tools=tools)
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
        structures: list[agents.Structure] = []
        for i, part in enumerate(response.parts, start=1):
            logger.debug("## Agent response part {}: {}", i, str(part).strip())
            if call := part.function_call:
                name, kwargs = call.name, call.args
                if name in config.stop_actions:
                    done = True  # stop execution
                if action := getattr(actions, name):
                    try:
                        structure = action(driver=driver, config=action_config, **kwargs)
                    except Exception as error:
                        kwargs_text = ", ".join(f"{key}={val}" for key, val in kwargs.items())
                        logger.error(
                            f"Error while executing action '{name}' with kwargs '{kwargs_text}': {error}"
                        )
                        structure = agents.Structure(name=name, response={"error": str(error)})
                    structures.append(structure)
                else:
                    raise ValueError(f"Cannot execute action (unknown action name): {name}!")
            elif part.text:
                pass
            else:
                raise ValueError(f"Cannot handle agent response (unknown part type): {part}!")
        # output
        agent_content = agents.Content(role=agents.Role.AGENT.value, parts=response.parts)
        if done is True:
            return agent_content
        contents.append(agent_content)
        user_input = yield agent_content
        # input
        message = user_input or config.default_message
        returned = [agents.Part(function_response=s) for s in structures]
        screenshot = agents.Blob(mime_type="image/png", data=driver.get_screenshot_as_png())
        user_content = agents.Content(
            role=agents.Role.USER.value,
            parts=[
                agents.Part(inline_data=screenshot),
                agents.Part(text=message),
            ]
            + returned,  # action calls
        )
        contents.append(user_content)
