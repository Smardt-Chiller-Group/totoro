import typer
import invoke

from totoro.utils import run
from totoro.settings import load_settings


app = typer.Typer()
config = load_settings()
repository = config.get('repository')

@app.callback()
def callback():
    """
    Azure Container Registry authentication
    """

def check_prerequisites():
    """Check if required tools are installed"""
    errors = []
    
    # Check for Azure CLI
    try:
        result = invoke.run('az --version', hide=True, warn=True)
        if not result.ok:
            errors.append("Azure CLI (az) is not installed or not working")
    except:
        errors.append("Azure CLI (az) is not installed")
    
    # Check for Docker
    try:
        result = invoke.run('docker --version', hide=True, warn=True)
        if not result.ok:
            errors.append("Docker is not installed or not working")
    except:
        errors.append("Docker is not installed")
    
    if errors:
        typer.echo(typer.style('\n❌ Missing prerequisites:\n', fg='red', bold=True))
        for error in errors:
            typer.echo(typer.style(f'  • {error}', fg='red'))
        typer.echo()
        return False
    
    return True

def is_azure_logged_in() -> bool:
    """Check if user is logged in to Azure"""
    try:
        result = invoke.run('az account show', hide=True, warn=True)
        return result.ok
    except:
        return False

def is_acr_logged_in(registry: str) -> bool:
    """Check if Docker is logged in to ACR"""
    try:
        # Try to check docker credentials for the registry
        result = invoke.run(f'docker login {registry} --username 00000000-0000-0000-0000-000000000000 --password-stdin < /dev/null 2>&1 | grep -q "unauthorized"', hide=True, warn=True)
        # Try az acr login which is idempotent
        result = invoke.run(f'az acr login --name {registry.split(".")[0]} --only-show-errors', hide=True, warn=True)
        return result.ok
    except:
        return False

@app.command()
def login():
    """
    Login to Azure Container Registry (ACR)
    
    This command performs two steps:
    1. Azure login (az login) - Opens browser for authentication
    2. ACR login (az acr login) - Authenticates Docker with the container registry
    """
    # Check prerequisites first
    if not check_prerequisites():
        raise typer.Exit(code=1)
    
    # Extract ACR name from repository URL
    # repository format: smardtacrdev.azurecr.io/smardtportal
    registry_url = '.'.join(repository.split('/')[-1].split('.')[:-1]) if '/' in repository else repository.split('/')[0]
    acr_name = repository.split('.')[0] if '.' in repository else None
    
    if not acr_name:
        typer.echo(typer.style('❌ Could not extract ACR name from repository configuration', fg='red'))
        raise typer.Exit(code=1)
    
    typer.echo(typer.style('\nAzure Container Registry Login', fg='cyan', bold=True))
    typer.echo(typer.style('='*60 + '\n', fg='cyan'))
    
    # Step 1: Check Azure login status
    typer.echo(typer.style('Step 1: Azure Login', fg='blue', bold=True))
    
    if is_azure_logged_in():
        typer.echo(typer.style('✓ Already logged in to Azure\n', fg='green'))
    else:
        typer.echo('Opening browser for authentication...')
        typer.echo('Follow the prompts in your terminal to select subscription.\n')
        
        try:
            result = run(['az login'], stdout=False)
            if not result.ok:
                typer.echo(typer.style('\n❌ Azure login failed', fg='red'))
                raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(typer.style(f'\n❌ Azure login failed: {str(e)}', fg='red'))
            raise typer.Exit(code=1)
        
        typer.echo(typer.style('\n✓ Azure login successful\n', fg='green'))
    
    # Step 2: ACR login (always attempt, it's idempotent and fast)
    typer.echo(typer.style(f'Step 2: ACR Login ({acr_name})', fg='blue', bold=True))
    
    try:
        result = run([f'az acr login --name {acr_name}'])
        if not result.ok:
            typer.echo(typer.style(f'\n❌ ACR login failed for {acr_name}', fg='red'))
            raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(typer.style(f'\n❌ ACR login failed: {str(e)}', fg='red'))
        raise typer.Exit(code=1)
    
    typer.echo(typer.style(f'\n✓ Successfully logged in to {acr_name}', fg='green', bold=True))
    typer.echo(typer.style('\nYou can now build and push images!\n', fg='green'))

@app.command()
def logout():
    """
    Logout from Azure and Azure Container Registry
    
    This command performs:
    1. Azure logout (az logout)
    2. Docker logout from ACR registry
    """
    # Extract registry URL from repository
    # repository format: smardtacrdev.azurecr.io/smardtportal
    registry_url = repository.split('/')[0] if '/' in repository else repository
    
    typer.echo(typer.style('\nLogging out...', fg='cyan', bold=True))
    typer.echo(typer.style('='*60 + '\n', fg='cyan'))
    
    # Step 1: Azure logout
    typer.echo(typer.style('Step 1: Azure Logout', fg='blue', bold=True))
    
    if not is_azure_logged_in():
        typer.echo(typer.style('ℹ️  Not logged in to Azure\n', fg='yellow'))
    else:
        try:
            result = run(['az logout'])
            if not result.ok:
                typer.echo(typer.style('❌ Azure logout failed\n', fg='red'))
            else:
                typer.echo(typer.style('✓ Logged out from Azure\n', fg='green'))
        except Exception as e:
            typer.echo(typer.style(f'❌ Azure logout failed: {str(e)}\n', fg='red'))
    
    # Step 2: Docker logout from ACR
    typer.echo(typer.style(f'Step 2: Docker Logout from {registry_url}', fg='blue', bold=True))
    
    try:
        result = run([f'docker logout {registry_url}'])
        if not result.ok:
            typer.echo(typer.style(f'❌ Docker logout failed for {registry_url}\n', fg='red'))
        else:
            typer.echo(typer.style(f'✓ Logged out from {registry_url}\n', fg='green'))
    except Exception as e:
        typer.echo(typer.style(f'❌ Docker logout failed: {str(e)}\n', fg='red'))
    
    typer.echo(typer.style('Logout complete!\n', fg='green'))

@app.command()
def status():
    """
    Check Azure and ACR login status
    """
    # Check prerequisites first
    if not check_prerequisites():
        raise typer.Exit(code=1)
    
    # Extract ACR info
    acr_name = repository.split('.')[0] if '.' in repository else None
    registry_url = repository.split('/')[0] if '/' in repository else repository
    
    typer.echo(typer.style('\nLogin Status', fg='cyan', bold=True))
    typer.echo(typer.style('='*60 + '\n', fg='cyan'))
    
    # Check Azure login
    typer.echo(typer.style('Azure CLI:', fg='blue', bold=True))
    if is_azure_logged_in():
        try:
            result = invoke.run('az account show --query "{Name: name, SubscriptionId: id, TenantId: tenantId}" -o table', hide=True)
            typer.echo(typer.style('  ✓ Logged in\n', fg='green'))
            typer.echo(result.stdout)
        except:
            typer.echo(typer.style('  ✓ Logged in\n', fg='green'))
    else:
        typer.echo(typer.style('  ✗ Not logged in\n', fg='red'))
    
    # Check ACR/Docker login
    typer.echo(typer.style(f'\nAzure Container Registry ({acr_name}):', fg='blue', bold=True))
    try:
        # Try a quick ACR check
        result = invoke.run(f'az acr login --name {acr_name} --only-show-errors', hide=True, warn=True)
        if result.ok:
            typer.echo(typer.style('  ✓ Logged in and credentials valid\n', fg='green'))
        else:
            typer.echo(typer.style('  ✗ Not logged in or credentials expired\n', fg='red'))
    except:
        typer.echo(typer.style('  ✗ Not logged in or credentials expired\n', fg='red'))