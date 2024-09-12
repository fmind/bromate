"""Interact with web drivers using agent functions."""

# %% IMPORTS

import time
import typing as T

import pydantic as pdt

from bromate import agents, drivers, types

# %% CLASSES


class ActionConfig(types.ImmutableData):
    """Config for all actions."""

    sleep_time: pdt.PositiveFloat = types.Field(
        default=0.5, description="Time to sleep after loading a page"
    )


# %% ALIASES


class Action(T.Protocol):
    """Alias for an action."""

    __name__: str
    __doc__: str

    def __call__(
        self, driver: drivers.Driver, config: ActionConfig, *args: T.Any, **kwargs: T.Any
    ) -> agents.Structure: ...


# %% FUNCTIONS

AGENT_FUNCTIONS: list[agents.Function] = []


def declare(schema: agents.Schema | None = None) -> T.Callable[[Action], Action]:
    """Declare an agent function (decorator)."""

    def decorator(action: Action) -> Action:
        function = agents.Function(
            name=action.__name__, description=action.__doc__, parameters=schema
        )
        AGENT_FUNCTIONS.append(function)
        return action

    return decorator


@declare(
    schema=agents.Schema(
        type=agents.Type.OBJECT,
        properties={
            "url": agents.Schema(type=agents.Type.STRING, description="URL of the web page to open")
        },
        required=["url"],
    )
)
def get(driver: drivers.Driver, config: ActionConfig, url: str) -> agents.Structure:
    """Open a web page in the browser window."""
    driver.get(url=url)  # wait loading
    time.sleep(config.sleep_time)
    return agents.Structure(
        name=get.__name__,
        response={
            "title": driver.title,
            "url": driver.current_url,
            "page_source": driver.page_source,
        },
    )


@declare()
def done(driver: drivers.Driver, config: ActionConfig) -> agents.Structure:
    """Call this when no further action is required."""
    return agents.Structure(name=done.__name__, response={"done": True})


@declare()
def back(driver: drivers.Driver, config: ActionConfig) -> agents.Structure:
    """Go back from one page."""
    driver.back()
    time.sleep(config.sleep_time)
    return agents.Structure(
        name=back.__name__,
        response={
            "title": driver.title,
            "url": driver.current_url,
            "page_source": driver.page_source,
        },
    )


@declare()
def forward(driver: drivers.Driver, config: ActionConfig) -> agents.Structure:
    """Go forward from one page."""
    driver.forward()
    time.sleep(config.sleep_time)
    return agents.Structure(
        name=forward.__name__,
        response={
            "title": driver.title,
            "url": driver.current_url,
            "page_source": driver.page_source,
        },
    )


@declare(
    schema=agents.Schema(
        type=agents.Type.OBJECT,
        properties={
            "css_selector": agents.Schema(
                type=agents.Type.STRING, description="CSS selector of the element to click on."
            ),
        },
        required=["css_selector"],
    )
)
def click(driver: drivers.Driver, config: ActionConfig, css_selector: str) -> agents.Structure:
    """Click on an element given its CSS selector."""
    element = driver.find_element(by=drivers.CSS, value=css_selector)
    element.click()
    time.sleep(config.sleep_time)
    return agents.Structure(
        name=click.__name__,
        response={
            "title": driver.title,
            "url": driver.current_url,
            "page_source": driver.page_source,
        },
    )


@declare(
    schema=agents.Schema(
        type=agents.Type.OBJECT,
        properties={
            "css_selector": agents.Schema(
                type=agents.Type.STRING, description="CSS selector of the element to clear."
            ),
        },
        required=["css_selector"],
    )
)
def clear(driver: drivers.Driver, config: ActionConfig, css_selector: str) -> agents.Structure:
    """Clearn an element given its CSS selector."""
    element = driver.find_element(by=drivers.CSS, value=css_selector)
    element.clear()
    return agents.Structure(name=clear.__name__, response={"cleared": True})


@declare(
    schema=agents.Schema(
        type=agents.Type.OBJECT,
        properties={
            "css_selector": agents.Schema(
                type=agents.Type.STRING, description="CSS selector of the element to submit."
            ),
        },
        required=["css_selector"],
    )
)
def submit(driver: drivers.Driver, config: ActionConfig, css_selector: str) -> agents.Structure:
    """Submit an element given its CSS selector."""
    element = driver.find_element(by=drivers.CSS, value=css_selector)
    element.submit()
    time.sleep(config.sleep_time)
    return agents.Structure(
        name=submit.__name__,
        response={
            "title": driver.title,
            "url": driver.current_url,
            "page_source": driver.page_source,
        },
    )


@declare(
    schema=agents.Schema(
        type=agents.Type.OBJECT,
        properties={
            "css_selector": agents.Schema(
                type=agents.Type.STRING, description="CSS selector of the element to send keys."
            ),
            "text": agents.Schema(
                type=agents.Type.STRING, description="text to send to the element."
            ),
        },
        required=["css_selector", "text"],
    )
)
def write(
    driver: drivers.Driver, config: ActionConfig, css_selector: str, text: str
) -> agents.Structure:
    """write text an the element given its CSS selector."""
    element = driver.find_element(by=drivers.CSS, value=css_selector)
    element.send_keys(text)
    return agents.Structure(name=write.__name__, response={"wrote": True})


@declare(
    schema=agents.Schema(
        type=agents.Type.OBJECT,
        properties={
            "css_selector": agents.Schema(
                type=agents.Type.STRING, description="CSS selector of the element to send keys."
            ),
            "values": agents.Schema(
                type=agents.Type.ARRAY,
                items=agents.Schema(
                    type=agents.Type.STRING, description="element value to select."
                ),
            ),
        },
        required=["css_selector", "values"],
    )
)
def select(
    driver: drivers.Driver, config: ActionConfig, css_selector: str, values: list[str]
) -> agents.Structure:
    """Select the values in the element given its CSS selector."""
    element = driver.find_element(by=drivers.CSS, value=css_selector)
    selector = T.cast(drivers.Select, element)
    selector.deselect_all()
    for value in values:
        selector.select_by_value(value=value)
    return agents.Structure(name=select.__name__, response={"selected": True})


@declare()
def accept(driver: drivers.Driver, config: ActionConfig) -> agents.Structure:
    """Accept the alert on the current tab."""
    alert = drivers.Alert(driver)
    alert.accept()
    return agents.Structure(name=accept.__name__, response={"accepted": True})


@declare()
def dismiss(driver: drivers.Driver, config: ActionConfig) -> agents.Structure:
    """Dismiss the alert on the current tab."""
    alert = drivers.Alert(driver)
    alert.dismiss()
    return agents.Structure(name=dismiss.__name__, response={"dismissed": True})


@declare(
    schema=agents.Schema(
        type=agents.Type.OBJECT,
        properties={
            "text": agents.Schema(
                type=agents.Type.STRING, description="Text to send to the alert prompt."
            ),
        },
        required=["text"],
    )
)
def prompt(driver: drivers.Driver, config: ActionConfig, text: str) -> agents.Structure:
    """Write text the alert prompt on the current tab"""
    alert = drivers.Alert(driver)
    alert.send_keys(text)
    return agents.Structure(name=prompt.__name__, response={"prompted": True})
