from time import sleep
import typer

from totoro.utils import run
from totoro.validations import validate


app = typer.Typer()

@app.callback()
def callback():
    """
    Container orchestration
    """

@app.command()
def up(
    profile: str = typer.Argument(..., help='Compose profile'),
    context: str = typer.Option('default', '--context', help='Docker context'),
    daemon: bool = typer.Option(True, '--no-daemon', help='Daemon')
):
    """
    Docker compose up

    TODO:
    - Additional environment variables via inline assignment
    """
    validate('context', context)
    validate('profile', profile)
    run([
        f'NGINX_TAG={context} ENV_FILE={env_file(context)} docker --context {context} compose',
        f'--profile {profile} up',
        # '--scale certbot=0' if all([context == 'default' , profile == 'all']) else '',
        '-d' if daemon else '',
    ])

@app.command()
def down(
    profile: str = typer.Argument(..., help='Compose profile'),
    context: str = typer.Option('default', '--context', help='Docker context')
):
    """
    Docker compose down
    """
    validate('context', context)
    validate('profile', profile)
    run([f'ENV_FILE={env_file(context)} docker --context {context} compose --profile {profile} down'])

@app.command()
def exec(
    profile: str = typer.Argument(..., help='Compose profile'),
    command: str = typer.Argument(..., help='Command to execute'),
    context: str = typer.Option('default', '--context', help='Docker context')
):
    """
    Docker compose exec
    """
    validate('context', context)
    validate('profile', profile)
    run([f'ENV_FILE={env_file(context)} docker --context {context} compose exec {profile} {command}'])

def env_file(context: str):
    return {
        'default': '.env-dev',
        'production': '.env-production',
    }.get(context, '.env-staging')