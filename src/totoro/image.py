import typer

from totoro.utils import run, resolve_docker_tag, resolve_docker_context
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
    tag: str = typer.Option(None, help='Tag for Docker image. If omitted, it will be derived from the current Git branch'),
    use_cache: bool = typer.Option(True, '--cache/--no-cache', help='Use cache')
):
    """
    Build docker image
    """
    validate('service', service)

    tag = tag or resolve_docker_tag()

    if service == 'web':
        engine_branch = config.get('deployment_targets')[tag]['engine']
        typer.echo(
            typer.style(f'Fetch latest changes from `{engine_branch}` for chiller selection engine', dim=True, fg='green')
        )
        run([
            f'cd smardt_portal/smardt_api/calculator && git switch {engine_branch} && git pull'
        ], stdout=False)

    run([
        'docker image build',
        f'-f dockerfiles/{service}/{service}.Dockerfile',
        f'-t {repository}/{service}:{tag} .',
        '' if use_cache else '--no-cache'
    ])

@app.command()
def push(
    service: str = typer.Argument(..., help='Service to push'),
    tag: str = typer.Option(None, help='Tag for Docker image. If omitted, it will be derived from the current Git branch')
):
    """
    Push image to container registry
    """
    validate('service', service)

    tag = tag or resolve_docker_tag()
    run([f'docker push {repository}/{service}:{tag}'])

@app.command()
def pull(
    service: str = typer.Argument(..., help='Service to pull'),
    tag: str = typer.Option(None, help='Tag for Docker image. If omitted, it will be derived from the current Git branch'),
    ctx: str = typer.Option(None, '--context', help='Docker context'),
):
    """
    Pull image from container registry
    """
    validate('service', service)
    if ctx: validate('context', ctx)

    tag = tag or resolve_docker_tag()
    ctx = ctx or resolve_docker_context(tag, ctx=='default')
    run([
        f'docker --context {ctx} pull {repository}/{service}:{tag}'
    ])