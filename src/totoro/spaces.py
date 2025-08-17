import os
import typer
import boto3
import click

from totoro.validations import validate
from totoro.settings import load_settings


app = typer.Typer()
config = load_settings()
spaces = config.get('spaces')

def client():
    session = boto3.session.Session()

    if not all([
        os.environ.get('AWS_ACCESS_KEY_ID'),
        os.environ.get('AWS_SECRET_ACCESS_KEY')]
    ):
        raise typer.BadParameter(
            'AWS credentials are missing.\nEnsure that AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set as environment variables.'
        )

    return session.client(
        's3',
        region_name = spaces['region_name'],
        endpoint_url = spaces['endpoint_url'],
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

def get_backups(resource: str, limit: int = 15):
    backup_objects = sorted(
        client().list_objects_v2(
            Bucket=spaces['bucket'],
            Prefix=f"{spaces['prefix']}/{resource}",
            StartAfter=spaces.get('start_after', '')
        ).get('Contents', []),
        key=lambda i: i['LastModified'],
        reverse=True
    )
    backups = [
        f'{backup["Key"].split("/")[-1]}'
        for backup in backup_objects
    ]
    return backups[:limit]

@app.callback()
def callback():
    """
    Download database, translations & files backups from Spaces Object Storage
    """

@app.command()
def list(
    resource: str = typer.Argument(..., help='Resource type'),
):
    """
    List backed up resources
    """
    validate('resource', resource)
    backups = get_backups(resource, 10)
    backups_display = '\n'.join(
        [f"[{index+1}]\t{backup}" for index, backup in enumerate(backups)]
    )
    typer.echo(typer.style(backups_display, dim=True, fg='yellow'))

@app.command()
def download(
    resource: str = typer.Argument(..., help='Resource type'),
    filename: str = typer.Argument(..., help='File name'),
):
    """
    Download resource
    """
    validate('resource', resource)
    object_key = f"{spaces['prefix']}/{resource}/{filename}"
    object_length = client().head_object(
        Bucket=spaces['bucket'],
        Key=object_key
    )['ContentLength']
    object_size_in_mb = round(object_length/(1024 ** 2), 2)

    typer.echo(
        typer.style(f'Downloading resource: {resource}/{filename} ({object_size_in_mb}MB)', dim=True, fg='green')
    )

    with click.progressbar(length=object_length, empty_char='░', fill_char='▓') as progress_bar:
        client().download_file(
            spaces['bucket'],
            object_key,
            f"{config.get('spaces')['downloads_dir']}/{filename}",
            Callback=progress_bar.update
        )