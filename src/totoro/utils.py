import typer
import invoke

from totoro.validations import validate
from totoro.settings import load_settings


config = load_settings()

def get_commit_sha() -> str:
    return invoke.run('git rev-parse HEAD', hide=True).stdout.strip()

def get_git_author() -> str:
    return invoke.run('git config user.name', hide=True).stdout.strip()

def get_image_digest(service: str, tag: str) -> str:
    """
    Get Docker image digest from ACR
    """
    return invoke.run(f"docker buildx imagetools inspect {config['repository']}/{service}:{tag} | grep '^Digest:' | awk '{{print $2}}'", hide=True).stdout.strip()

def resolve_docker_tag() -> str:
    """
    Generate a Docker image tag based on current git branch.

    - Retrieves the current git branch name.
    - Converts it to lowercase.
    - Replaces any slashes (/) with hyphens (-).
    """
    return (
        invoke
            .run('git branch --show-current', hide=True)
            .stdout
            .strip()
            .lower()
            .replace('/', '-')
    )

def resolve_docker_context(tag: str, local: bool) -> str:
    """
    Returns Docker context
    """
    if local: tag = 'local'
    try:
        ctx = config['deployment_targets'][tag]['host']
        validate('context', ctx)
        return ctx
    except KeyError:
        return tag

def resolve_env_file(tag: str, local: bool) -> str:
    if local: tag = 'local'
    return config['deployment_targets'][tag]['env_file']

def run(command: list, stdout=True):
    formatted_command = ' '.join(command).strip()
    if stdout:
        typer.echo(
            typer.style(
                formatted_command+'\n',
                dim=True,
                fg='blue',
                italic=True,
            )
        )
    return invoke.run(formatted_command, pty=True)