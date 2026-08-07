import os
import time
from datetime import datetime

import click
import typer
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceExistsError

from totoro.validations import validate
from totoro.settings import load_settings


app = typer.Typer()
config = load_settings()
blob_config = config.get('blob')
_credential = DefaultAzureCredential()

def client() -> BlobServiceClient:
    return BlobServiceClient(
        account_url=blob_config['endpoint_url'],
        credential=_credential,
        max_page_size=500
    )

def get_backups(resource: str, limit: int = 15) -> list:
    container = client().get_container_client(blob_config['container'])
    blobs = sorted(
        container.list_blobs(name_starts_with=f"{blob_config['prefix']}/{resource}"),
        key=lambda b: b.creation_time, reverse=True
    )[:limit]
    return [os.path.basename(b.name) for b in blobs]

@app.callback()
def callback():
    """
    Download database, translations & files backups from Spaces Object Storage
    """

@app.command(name='list')
def list_resources(
    resource: str = typer.Argument(..., help='Resource type'),
):
    """
    List backed up resources
    """
    validate('resource', resource)
    backups = get_backups(resource)
    backups_display = '\n'.join(
        [f"[{index+1}]\t{backup}" for index, backup in enumerate(backups)]
    )
    typer.secho(backups_display, dim=True, fg='yellow')

@app.command()
def upload(
    resource: str = typer.Argument(..., help='Resource type'),
    filepath: str = typer.Argument(..., help='File path'),
):
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    file_size_in_mb = round(file_size / (1024 ** 2), 2)

    container = client().get_container_client(blob_config['container'])
    blob_client = container.get_blob_client(f"{blob_config['prefix']}/{resource}/{filename}")

    typer.secho(f'Uploading resource: {resource}/{filename} ({file_size_in_mb}MB)', dim=True, fg='green')

    with click.progressbar(length=file_size, empty_char='░', fill_char='▓') as progress_bar:
        last_seen = 0

        def progress_hook(current, total):
            nonlocal last_seen
            progress_bar.update(current - last_seen)
            last_seen = current

        try:
            with open(filepath, 'rb') as file:
                # filenames are timestamped, explictly setting overwrite to false to
                # guards against accidental overwriting
                res = blob_client.upload_blob(file, overwrite=False, progress_hook=progress_hook)
        except ResourceExistsError:
            typer.echo('\n')
            typer.secho(f'✖ Upload failed: {blob_client.url} already exists', fg='red', err=True)
            raise typer.Exit(code=1)


    etag = res['etag'].strip('"')

    typer.echo('')
    typer.secho('✔ Upload complete', dim=True, fg='green', bold=True)
    typer.secho(f'URL: {blob_client.url}', dim=True, fg='white')
    typer.secho(f"ETag: {etag}\nLast modified: {res['last_modified']}", dim=True, fg='white')

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