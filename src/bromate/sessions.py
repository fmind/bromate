"""Sessions for running the application."""

# %% IMPORTS

import typing as T

import pydantic as pdt
from loguru import logger

from bromate import actions, browsers, models
from bromate.settings import SessionSettings

# %% SESSIONS


class Session(pdt.BaseModel, arbitrary_types_allowed=True, strict=True, extra="forbid"):
    """Session to run the application."""

    query: str | None = None
    model: models.Model
    browser: browsers.Browser
    actions: dict[str, actions.Action]
    settings: SessionSettings
    contents: list[models.Content] = []

    @classmethod
    def from_settings(cls, session_settings: SessionSettings) -> "Session":
        """Create a session from settings."""
        logger.info("Creating session: {}", session_settings)
        # settings
        model_settings = session_settings.model
        browser_settings = session_settings.browser
        actions_settings = session_settings.actions
        # actions
        session_actions = {
            attr: getattr(actions_settings, attr) for attr in actions_settings.model_fields
        }
        logger.debug("Session actions: {}", list(session_actions.keys()))
        # browser
        browser_options = browsers.Options()
        browser_service = browsers.Service()
        browser = browsers.Browser(
            options=browser_options, service=browser_service, keep_alive=browser_settings.keep_alive
        )
        # model
        if model_settings.api_key is None:
            raise ValueError("Model API key is missing.")
        models.configure(api_key=model_settings.api_key.get_secret_value())  # global assignment
        model_config = models.Config(
            temperature=model_settings.temperature,
            candidate_count=model_settings.candidate_count,
            max_output_tokens=model_settings.max_output_tokens,
        )
        model_tools = [action.tool() for action in session_actions.values()]
        model = models.Model(
            tools=model_tools,
            model_name=model_settings.name,
            generation_config=model_config,
            system_instruction=model_settings.system_instructions,
        )
        # session
        return Session(
            model=model, browser=browser, actions=session_actions, settings=session_settings
        )

    def record(self, role: models.ContentRole, parts: list[models.Part]) -> models.Content:
        """Add a new content to the session."""
        content = models.Content(role=role.value, parts=parts)
        self.contents.append(content)
        return content

    def execute(self, query: str) -> T.Generator[list[models.Content], None, None]:
        """Execute the user query with the session."""
        # preparation
        self.query = query
        logger.info("Executing query: {}", self.query)
        self.record(role=models.ContentRole.USER, parts=[models.Part(text=self.query)])
        # execution
        for step in range(self.settings.max_steps):
            logger.info("- Execution step: {}", step)
            parts = []
            response = self.model.generate_content(contents=self.contents)
            if usage := response.usage_metadata:
                logger.debug(
                    "Model usage: total tokens={}, input tokens={}, output tokens={}",
                    usage.total_token_count,
                    usage.prompt_token_count,
                    usage.candidates_token_count,
                )
            if feedback := response.prompt_feedback:
                logger.warning("Model feedback: {}", feedback)
            for part in response.parts:
                if call := part.function_call:
                    name, kwargs = call.name, call.args
                    args_string = ", ".join(f"{key}={val}" for key, val in kwargs.items())
                    call_string = f"{name}({args_string})"
                    if action := self.actions.get(name):
                        logger.debug("Calling action: {}", call_string)
                        action(browser=self.browser, **kwargs)
                    else:
                        raise ValueError(f"Unknown action name: {name}")
                    part = models.Part(text=f"Calling action: {call_string}")
                    parts.append(part)
                elif part.text:
                    parts.append(part)
                else:
                    raise ValueError(f"Unknown response part: {part}")
            self.record(role=models.ContentRole.MODEL, parts=parts)
            yield self.contents
            if self.settings.interruption_message in parts[-1].text:
                break
            else:
                logger.warning("Continuing the execution: {}", self.settings.continuation_message)
                self.record(
                    role=models.ContentRole.USER,
                    parts=[models.Part(text=self.settings.continuation_message)],
                )
