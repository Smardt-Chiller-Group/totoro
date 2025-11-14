import sys
import importlib
from pathlib import Path
import typer

from totoro.utils import run
from totoro.settings import load_settings
from totoro import image, compose, server, spaces, login


app = typer.Typer()
config = load_settings()

app.add_typer(image.app, name='image')
app.add_typer(server.app, name='server')
app.add_typer(spaces.app, name='spaces')
app.add_typer(compose.app, name='compose')

# Register login as a top-level command (not under a subgroup)
app.registered_commands.extend(login.app.registered_commands)

@app.callback()
def callback():
    """
    Totoro, your dependable DevOps buddy
    """

@app.command()
def init():
    """
    Set up Docker contexts
    """
    for context, host in config.get('hosts').items():
        run([
            f'docker context create {context} --docker=host=ssh://{host}'
        ])

def load_plugins(dir_name:str):
    plugins_dir = Path.cwd() / dir_name

    if not plugins_dir.exists() or not plugins_dir.is_dir():
        return

    sys.path.insert(0, str(Path.cwd()))

    for file in plugins_dir.glob('*.py'):
        if file.name == '__init__.py' or file.name.startswith('_'):
            continue

        try:
            module = importlib.import_module(f'{dir_name}.{file.stem}')
            if hasattr(module, 'app'):
                app.add_typer(module.app, name=file.stem.replace('_', '-'))
        except Exception as e:
            typer.echo(e)

load_plugins(config.get('plugins_dir_name'))