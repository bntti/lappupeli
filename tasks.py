from invoke import task


@task
def start(ctx):
    ctx.run("cd src && flask run", pty=True)


@task
def lint(ctx):
    ctx.run("pylint src", pty=True)


@task
def initialize_database(ctx):
    ctx.run("python3 src/initialize_database.py", pty=True)
