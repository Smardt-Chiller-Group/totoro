import typer
import invoke, subprocess

from totoro.validations import validate
from totoro.settings import load_settings


config = load_settings()


def check_dirty_build_policy():
    """
    Enforce branch-aware dirty build policies.

    - master: strict — abort immediately on uncommitted changes
    - other branches: soft — warn and prompt for confirmation
    """
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True, text=True, check=True
    )
    has_uncommitted = bool(result.stdout.strip())

    if not has_uncommitted:
        return

    branch_result = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        capture_output=True, text=True, check=True
    )
    branch = branch_result.stdout.strip()

    if branch == 'master':
        typer.echo(
            typer.style(
                f'Error: dirty build detected on `master`. Commit or stash all changes before building.',
                fg='red', bold=True
            )
        )
        raise typer.Exit(code=1)
    else:
        typer.echo(
            typer.style(
                f'Warning: uncommitted changes detected on `{branch}`.',
                fg='yellow', bold=True
            )
        )
        confirmed = typer.confirm('Proceed with dirty build?', default=False)
        if not confirmed:
            raise typer.Exit(code=0)

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

def get_deployment_target(tag: str) -> dict[str, str]:
    try:
        return config['deployment_targets'][tag]
    except KeyError as e:
        raise typer.BadParameter(
            f'No deployment target found for {e} in `totoro.yaml`'
        )

def resolve_docker_context(tag: str) -> str:
    """Returns Docker context"""
    docker_context = get_deployment_target(tag)['host']
    validate('context', docker_context)
    return docker_context

def resolve_env_file(tag: str) -> str:
    """Returns env file specified in a deployment target"""
    return get_deployment_target(tag)['env_file']

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