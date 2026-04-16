from invoke.context import Context
from invoke.tasks import task


@task
def start(ctx: Context) -> None:
    ctx.run('gunicorn --chdir lappupeli "app:create_app()"', pty=True)


@task
def dev(ctx: Context) -> None:
    ctx.run("cd lappupeli && flask run", pty=True)


@task
def lint(ctx: Context) -> None:
    ctx.run("pylint lappupeli", pty=True)


@task
def initialize_database(ctx: Context) -> None:
    ctx.run("python3 lappupeli/initialize_database.py", pty=True)
