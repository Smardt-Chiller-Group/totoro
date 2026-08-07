import os

import click
import typer
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

from totoro.validations import validate
from totoro.settings import load_settings


app = typer.Typer()
config = load_settings()
blob = config.get('blob')
_credential = DefaultAzureCredential()

def client() -> BlobServiceClient:
    return BlobServiceClient(
        account_url=blob['endpoint_url'],
        credential=_credential,
        max_page_size=500
    )

def get_backups(resource: str, limit: int = 15) -> list:
    container = client().get_container_client(blob['container'])
    blobs = sorted(
        container.list_blobs(name_starts_with=f"{blob['prefix']}/{resource}"),
        key=lambda b: b.creation_time, reverse=True
    )[:limit]
    return [
        f"{os.path.basename(b.name)}"
        for b in blobs
    ]

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