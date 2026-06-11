import typer

from totoro.validations import validate
from totoro.settings import load_settings
from totoro.utils import run, resolve_docker_tag, resolve_docker_context, resolve_env_file


app = typer.Typer()
config = load_settings()

@app.callback()
def callback():
    """
    Container orchestration
    """

@app.command()
def up(
    profile: str = typer.Argument(..., help='Compose profile'),
    daemon: bool = typer.Option(True, '--daemon/--no-daemon', help='Daemon'),
    ctx: str = typer.Option(None, '--context', help='Docker context'),
):
    """
    Docker compose up
    """
    validate('profile', profile)
    tag = resolve_docker_tag()
    ctx = resolve_docker_context(tag)
    env_file = resolve_env_file(tag)

    run([
        f'IMAGE_TAG={tag} ENV_FILE={env_file} docker --context {ctx} compose',
        f'--profile {profile} up',
        # '--scale certbot=0' if all([context == 'default' , profile == 'all']) else '',
        '-d' if daemon else '',
    ])

@app.command()
def down(
    profile: str = typer.Argument(..., help='Compose profile'),
    ctx: str = typer.Option(None, '--context', help='Docker context'),
):
    """
    Docker compose down
    """
    validate('profile', profile)
    tag = resolve_docker_tag()
    ctx = resolve_docker_context(tag)
    env_file = resolve_env_file(tag)
    run([f'ENV_FILE={env_file} docker --context {ctx} compose --profile {profile} down'])