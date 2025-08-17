import typer

from totoro.settings import load_settings


config = load_settings()

def validate(field: str, value: str):
    match field:
        case 'db':
            valid_options = config.get('dbs')
        case 'context':
            valid_options = [k for k,v in config.get('hosts').items()] + ['default']
        case 'service':
            valid_options = config.get('services')
        case 'profile':
            valid_options = config.get('profiles')
        case 'resource':
            spaces = config.get('spaces')
            valid_options = spaces.get('resources')
        case _:
            raise ValueError(f'Unknown field: {field}')

    if value not in valid_options:
        raise typer.BadParameter(
            f"Invalid {field}: {value}. Choose from {', '.join(valid_options)}"
        )