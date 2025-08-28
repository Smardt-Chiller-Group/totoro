import typer
import invoke


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

def run(command: list, stdout=True):
    formatted_command = ' '.join(command).strip()
    if stdout:
        typer.echo(
            typer.style(
                formatted_command,
                dim=True,
                fg='blue',
                italic=True,
            )
        )
    return invoke.run(formatted_command, pty=True)