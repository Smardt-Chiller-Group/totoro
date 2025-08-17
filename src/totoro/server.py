import typer
import getpass
from fabric import Connection

from totoro.utils import run
from totoro.validations import validate
from totoro.settings import load_settings


app = typer.Typer()
config = load_settings()
hosts = config.get('hosts')
server_setup_script = config.get('server_setup_script', {})

@app.callback()
def callback():
    """
    Server configuration management
    """

@app.command()
def add_sudo_user(
    user: str = typer.Argument(..., help='User name'),
    group: str = typer.Argument(..., help='Group name'),
    context: str = typer.Option('default', '--context', help='Docker context')
):
    """
    Create a new sudo user
    """
    validate('context', context)
    sudo_user_password = getpass.getpass('Enter password for new user: ')

    with Connection(host=hosts[context]) as c:
        c.sudo(f'groupadd -f {group}')
        c.sudo(f'adduser --disabled-password --gecos "" --ingroup {group} {user}')
        c.sudo(f'echo "{user}:{sudo_user_password}" | sudo chpasswd', pty=True)
        c.sudo(f'usermod -aG sudo {user}')
        c.sudo(f'rsync --archive --chown={user}:{group} ~/.ssh /home/{user}')

    typer.echo(
        typer.style(f'{user}:{group} added!', dim=True, fg='green', italic=True)
    )

@app.command()
def scp_setup_script(
    context: str = typer.Option('default', '--context', help='Docker context'),
):
    """
    Secure copy setup script to host. Refer to `server_setup_script` in settings.yaml
    """
    validate('context', context)
    setup_script_path = server_setup_script['dir']
    setup_script_filename = server_setup_script['filename']

    run([f"scp {setup_script_path}/{setup_script_filename} {hosts[context]}:."])

    typer.echo(
        typer.style(f'\nStart a SSH session to run the following command:\nsudo ./{setup_script_filename}\n',
            dim=True,
            fg='green',
            italic=True
        )
    )