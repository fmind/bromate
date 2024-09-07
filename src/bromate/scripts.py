"""Run the application scripts."""

# %% IMPORTS

from loguru import logger

from bromate import agents, drivers, executions, interactions, settings

# %% FUNCTIONS


def main(args: list[str] | None = None) -> int:
    """Run the main application script with arguments."""
    # parse
    setting = settings.ApplicationSetting(_cli_parse_args=args)
    logger.debug("Application setting: {}", setting)
    # init
    agent = agents.init_agent_from_config(config=setting.agent)
    driver = drivers.init_driver_from_config(config=setting.driver)
    # run
    execution = executions.execute(
        query=setting.query,
        agent=agent,
        driver=driver,
        config=setting.execution,
        action_config=setting.action,
    )
    # return
    return interactions.interact(execution=execution, config=setting.interaction)
