import os
import typer
import logfire

from totoro.utils import (
    run,
    resolve_docker_tag, resolve_docker_context,
    get_commit_sha, get_git_author, get_image_digest
)
from totoro.settings import load_settings
from totoro.validations import validate


app = typer.Typer()
config = load_settings()
repository = config.get('repository')
logfire.configure(
    service_name='totoro',
    token=os.getenv('LOGFIRE_TOKEN'),
    environment=os.getenv('LOGFIRE_ENVIRONMENT', 'production')
)

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

    git_author = get_git_author()
    commit_sha = get_commit_sha()
    build_command = [
        'docker buildx build',
        '--provenance false',
        '--sbom false',
        f'--label "AUTHOR={git_author}"',
        f'--label "COMMIT={commit_sha}"',
        f'--file dockerfiles/{service}/{service}.Dockerfile',
        f'--tag {repository}/{service}:{tag}',
        '--no-cache' if not use_cache else '',
        '--push .',
    ]

    with logfire.span(f'Docker Build: {service}:{tag}'):
        run(build_command)
        digest = get_image_digest(service, tag)
        # Assume success if we reach here
        logfire.info(
            f'Built and pushed to ACR: {digest}',
            tag=tag,
            digest=digest,
            service=service,
            author=git_author,
            commit=commit_sha,
            command=' '.join(build_command).strip(),
        )

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