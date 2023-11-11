from invoke import task


@task
def start(ctx):
    ctx.run('gunicorn --chdir lappupeli "app:create_app()"', pty=True)


@task
def dev(ctx):
    ctx.run("cd lappupeli && flask run", pty=True)


@task
def lint(ctx):
    ctx.run("pylint lappupeli", pty=True)


@task
def initialize_database(ctx):
    ctx.run("python3 lappupeli/initialize_database.py", pty=True)
