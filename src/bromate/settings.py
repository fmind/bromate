"""Configure the application with settings."""

# %% IMPORTS

import pydantic_settings as pdts

from bromate import actions, agents, drivers, executions, interactions, types

# %% CLASSES


class Setting(pdts.BaseSettings, env_prefix="bromate", cli_parse_args=True):
    """Base class for setting."""


class ApplicationSetting(Setting):
    """Execution actions on a web browser using agentic workflows."""

    query: pdts.CliPositionalArg[str] = types.Field(description="User query to execute")
    agent: agents.AgentConfig = types.Field(
        default=agents.AgentConfig(), description="Configuration of the agent"
    )
    action: actions.ActionConfig = types.Field(
        default=actions.ActionConfig(), description="Configuration for all actions"
    )
    driver: drivers.DriverConfig = types.Field(
        default=drivers.DriverConfig(), description="Configuration of the web driver"
    )
    execution: executions.ExecutionConfig = types.Field(
        default=executions.ExecutionConfig(), description="Configuration of the execution"
    )
    interaction: interactions.InteractionConfig = types.Field(
        default=interactions.InteractionConfig(), description="Configuration of the interaction"
    )
