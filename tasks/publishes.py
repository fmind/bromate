"""Publish tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

from . import packages

# %% TASKS


@task(pre=[packages.build])
def pypi(ctx: Context) -> None:
    """Publish the package on pypi."""
    ctx.run("poetry publish")


@task(pre=[pypi], default=True)
def all(_: Context) -> None:
    """Run all publish tasks."""
