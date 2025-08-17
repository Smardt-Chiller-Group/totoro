import typer

from totoro.utils import run
from totoro.settings import load_settings
from totoro.validations import validate


app = typer.Typer()
config = load_settings()
repository = config.get('repository')

@app.callback()
def callback():
    """
    Docker image management
    """

@app.command()
def build(
    service: str = typer.Argument(..., help='Service to build'),
    tag: str = typer.Argument(..., help='Tag for the image'),
    no_cache: bool = typer.Option(False, '--no-cache', help='Use cache')
):
    """
    Build docker image
    """
    validate('service', service)
    run([
        'docker image build',
        f'-f dockerfiles/{service}/{service}.Dockerfile',
        f'-t {repository}/{service}:{tag} .',
        '--no-cache' if no_cache else ''
    ])

@app.command()
def push(
    service: str = typer.Argument(...,help='Service to push'),
    tag: str = typer.Argument(..., help='Tag to use')
):
    """
    Push image to container registry
    """
    validate('service', service)
    run([f'docker push {repository}/{service}:{tag}'])

@app.command()
def pull(
    service: str = typer.Argument(..., help='Service to pull'),
    tag: str = typer.Argument(..., help='Tag to use'),
    context: str = typer.Option('default', '--context', help='Docker context')
):
    """
    Pull image from container registry
    """
    validate('context', context)
    run([
        f'docker --context {context} pull {repository}/{service}:{tag}'
    ])