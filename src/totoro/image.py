import typer
import invoke
from typing import Optional

from totoro.utils import run, resolve_docker_tag, resolve_docker_context
from totoro.settings import load_settings, save_settings, save_deployment_target
from totoro.validations import validate


app = typer.Typer()
config = load_settings()
repository = config.get('repository')

@app.callback()
def callback():
    """
    Docker image management
    """

def get_engine_branches() -> list[str]:
    """
    Get available branches from the engine repository.
    Returns ['master'] if unable to fetch branches.
    """
    try:
        result = invoke.run(
            'cd smardt_portal/smardt_api/calculator && git branch -r',
            hide=True,
            warn=True
        )
        if result.ok:
            # Parse remote branches, remove 'origin/' prefix and filter out HEAD
            branches = []
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if 'origin/' in line and 'HEAD' not in line:
                    branch = line.replace('origin/', '')
                    branches.append(branch)
            return branches if branches else ['master']
        return ['master']
    except Exception:
        return ['master']

def confirm_deployment_target(tag: str, service: str) -> bool:
    """
    Show deployment target details and ask for confirmation.
    If target doesn't exist, offer to create it.
    Returns True if user wants to proceed, False otherwise.
    """
    deployment_targets = config.get('deployment_targets', {})
    
    if tag in deployment_targets:
        # Show existing deployment target
        target = deployment_targets[tag]
        typer.echo(typer.style('\n' + '='*60, fg='cyan'))
        typer.echo(typer.style('  Deployment Target Configuration', fg='cyan', bold=True))
        typer.echo(typer.style('='*60, fg='cyan'))
        typer.echo(f"  Branch/Tag:  {typer.style(tag, fg='yellow', bold=True)}")
        typer.echo(f"  Host:        {typer.style(target.get('host', 'N/A'), fg='green')}")
        typer.echo(f"  Engine:      {typer.style(target.get('engine', 'N/A'), fg='green')}")
        typer.echo(f"  Env File:    {typer.style(target.get('env_file', 'N/A'), fg='green')}")
        typer.echo(typer.style('='*60 + '\n', fg='cyan'))
        
        return typer.confirm('Do you want to proceed with this configuration?')
    else:
        # Deployment target doesn't exist
        typer.echo(typer.style(f'\n⚠️  No deployment target found for branch: {tag}', fg='yellow', bold=True))
        
        if not typer.confirm('\nWould you like to create a new deployment target?'):
            typer.echo(typer.style('Build cancelled.', fg='red'))
            return False
        
        # Create new deployment target
        new_target = create_deployment_target(tag, service)
        if new_target:
            # Add to config in memory (for immediate use)
            config['deployment_targets'][tag] = new_target
            # Save only the deployment target to file (preserves formatting)
            save_deployment_target(tag, new_target)
            typer.echo(typer.style(f'\n✓ Deployment target for "{tag}" saved to totoro.yaml', fg='green', bold=True))
            return True
        else:
            typer.echo(typer.style('Build cancelled.', fg='red'))
            return False

def create_deployment_target(tag: str, service: str) -> Optional[dict]:
    """
    Interactive creation of a new deployment target.
    Returns the new target dict or None if cancelled.
    """
    typer.echo(typer.style('\n--- Create New Deployment Target ---\n', fg='cyan', bold=True))
    
    # Select host
    hosts = config.get('hosts', {})
    host_choices = list(hosts.keys()) + ['default']
    
    typer.echo('Available hosts:')
    for idx, host in enumerate(host_choices, 1):
        display_name = f"{host} ({hosts[host]})" if host in hosts else host
        typer.echo(f"  [{idx}] {display_name}")
    
    while True:
        try:
            host_idx = typer.prompt('\nSelect host (enter number)', type=int)
            if 1 <= host_idx <= len(host_choices):
                selected_host = host_choices[host_idx - 1]
                break
            else:
                typer.echo(typer.style(f'Please enter a number between 1 and {len(host_choices)}', fg='red'))
        except (ValueError, typer.Abort):
            typer.echo(typer.style('\nCancelled.', fg='red'))
            return None
    
    # Select engine branch (only relevant for web service)
    if service == 'web':
        typer.echo('\nFetching available engine branches...')
        engine_branches = get_engine_branches()
        
        # Put 'master' first if it exists
        if 'master' in engine_branches:
            engine_branches.remove('master')
            engine_branches.insert(0, 'master')
        
        typer.echo('\nAvailable engine branches:')
        for idx, branch in enumerate(engine_branches, 1):
            typer.echo(f"  [{idx}] {branch}")
        typer.echo(f"  [{len(engine_branches) + 1}] Enter custom branch name")
        
        while True:
            try:
                engine_idx = typer.prompt('\nSelect engine branch (enter number)', type=int)
                if 1 <= engine_idx <= len(engine_branches):
                    selected_engine = engine_branches[engine_idx - 1]
                    break
                elif engine_idx == len(engine_branches) + 1:
                    selected_engine = typer.prompt('Enter custom branch name')
                    break
                else:
                    typer.echo(typer.style(f'Please enter a number between 1 and {len(engine_branches) + 1}', fg='red'))
            except (ValueError, typer.Abort):
                typer.echo(typer.style('\nCancelled.', fg='red'))
                return None
    else:
        # Default to master for non-web services
        selected_engine = 'master'
    
    # Select or enter env file
    typer.echo('\nEnvironment file path:')
    typer.echo('  [1] .envs/.env-dev')
    typer.echo('  [2] .envs/.env-staging')
    typer.echo('  [3] .envs/.env-production')
    typer.echo('  [4] Enter custom path')
    
    env_file_map = {
        1: '.envs/.env-dev',
        2: '.envs/.env-staging',
        3: '.envs/.env-production'
    }
    
    while True:
        try:
            env_idx = typer.prompt('\nSelect environment file (enter number)', type=int)
            if env_idx in env_file_map:
                selected_env_file = env_file_map[env_idx]
                break
            elif env_idx == 4:
                selected_env_file = typer.prompt('Enter custom env file path')
                break
            else:
                typer.echo(typer.style('Please enter a number between 1 and 4', fg='red'))
        except (ValueError, typer.Abort):
            typer.echo(typer.style('\nCancelled.', fg='red'))
            return None
    
    # Summary and final confirmation
    new_target = {
        'host': selected_host,
        'engine': selected_engine,
        'env_file': selected_env_file
    }
    
    typer.echo(typer.style('\n--- Summary ---', fg='cyan', bold=True))
    typer.echo(f"  Branch/Tag:  {tag}")
    typer.echo(f"  Host:        {selected_host}")
    typer.echo(f"  Engine:      {selected_engine}")
    typer.echo(f"  Env File:    {selected_env_file}")
    
    if typer.confirm('\nSave this deployment target?'):
        return new_target
    else:
        return None

@app.command()
def build(
    service: str = typer.Argument(..., help='Service to build'),
    tag: str = typer.Option(None, help='Tag for Docker image. If omitted, it will be derived from the current Git branch'),
    use_cache: bool = typer.Option(True, '--cache/--no-cache', help='Use cache')
):
    """
    Build docker image
    """
    validate('service', service)

    tag = tag or resolve_docker_tag()
    
    # Confirm deployment target before proceeding
    if not confirm_deployment_target(tag, service):
        raise typer.Exit(code=1)

    # Now proceed with the build
    if service == 'web':
        engine_branch = config.get('deployment_targets')[tag]['engine']
        typer.echo(
            typer.style(f'\nFetching latest changes from `{engine_branch}` for chiller selection engine...', dim=True, fg='green')
        )
        run([
            f'cd smardt_portal/smardt_api/calculator && git switch {engine_branch} && git pull'
        ], stdout=False)

    typer.echo(typer.style('\nBuilding Docker image...', fg='blue', bold=True))
    run([
        'docker image build',
        f'-f dockerfiles/{service}/{service}.Dockerfile',
        f'-t {repository}/{service}:{tag} .',
        '' if use_cache else '--no-cache'
    ])
    
    typer.echo(typer.style(f'\n✓ Successfully built {repository}/{service}:{tag}', fg='green', bold=True))

@app.command()
def push(
    service: str = typer.Argument(..., help='Service to push'),
    tag: str = typer.Option(None, help='Tag for Docker image. If omitted, it will be derived from the current Git branch')
):
    """
    Push image to container registry
    """
    validate('service', service)

    tag = tag or resolve_docker_tag()
    run([f'docker push {repository}/{service}:{tag}'])

@app.command()
def pull(
    service: str = typer.Argument(..., help='Service to pull'),
    tag: str = typer.Option(None, help='Tag for Docker image. If omitted, it will be derived from the current Git branch'),
    ctx: str = typer.Option(None, '--context', help='Docker context'),
):
    """
    Pull image from container registry
    """
    validate('service', service)
    if ctx: validate('context', ctx)

    tag = tag or resolve_docker_tag()
    ctx = ctx or resolve_docker_context(tag, ctx=='default')
    run([
        f'docker --context {ctx} pull {repository}/{service}:{tag}'
    ])