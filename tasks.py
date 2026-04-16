from invoke.context import Context
from invoke.tasks import task


@task
def start(ctx: Context) -> None:
    ctx.run('gunicorn --chdir src "app:create_app()"', pty=True)


@task
def dev(ctx: Context) -> None:
    ctx.run("cd src && flask run", pty=True)


@task
def initialize_database(ctx: Context) -> None:
    ctx.run("python3 src/initialize_database.py", pty=True)
