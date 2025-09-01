from time import sleep
import typer

from totoro.utils import run, resolve_docker_tag, resolve_docker_context, resolve_env_file
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
    daemon: bool = typer.Option(True, '--no-daemon', help='Daemon'),
    local: bool = typer.Option(False, '--local', help='Local behaviour for connecting to Docker daemon')
):
    """
    Docker compose up
    """
    validate('profile', profile)
    tag = resolve_docker_tag()
    ctx = resolve_docker_context(tag, local)
    env_file = resolve_env_file(tag, local)
    run([
        f'IMAGE_TAG={tag} NGINX_TAG={ctx} ENV_FILE={env_file} docker --context {ctx} compose',
        f'--profile {profile} up',
        # '--scale certbot=0' if all([context == 'default' , profile == 'all']) else '',
        '-d' if daemon else '',
    ])

@app.command()
def down(
    profile: str = typer.Argument(..., help='Compose profile'),
    local: bool = typer.Option(False, '--local', help='Local behaviour for connecting to Docker daemon')
):
    """
    Docker compose down
    """
    validate('profile', profile)
    tag = resolve_docker_tag()
    ctx = resolve_docker_context(tag, local)
    env_file = resolve_env_file(tag, local)
    run([f'ENV_FILE={env_file} docker --context {ctx} compose --profile {profile} down'])