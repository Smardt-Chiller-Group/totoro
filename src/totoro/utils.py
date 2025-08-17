import typer
import invoke


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