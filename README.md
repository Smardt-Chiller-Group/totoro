## Totoro CLI

Totoro is a Python-based DevOps tool designed to streamline Docker-related commands and simplifies the management of Docker images and services, ensuring consistency across workflows.

### Features
- Azure Container Registry authentication management
- Docker image management with interactive deployment target configuration
- Server configuration management
- Download database, translations & files backups from Spaces Object Storage
- Container orchestration

### Installation
Tested against Python (=>3.11.7):

```sh
pip install git+https://github.com/kinoki-choy/totoro.git@v1.3.0
```
or if using UV:
```sh
uv add git+https://github.com/kinoki-choy/totoro.git@v1.3.0
```

### Prerequisites
Totoro requires the following tools to be installed:
- **Azure CLI** (`az`) - For container registry authentication
- **Docker** - For building and managing containers
- **Git** - For repository operations

Totoro will automatically check for these prerequisites and provide clear error messages if any are missing.

### Configuration
Create a `totoro.yaml` file in the root of your project with the following structure:

```yaml
repository: container-registry-repository

services:
  - db
  - web
  - nginx

profiles:
  - all
  - db
  - web
  - redis
  - nginx
#   - certbot

dbs:
  - database_01
  - database_02
db_user: database-user-name

hosts:
  staging: staging.server.com
  staging2: staging2.server.com
  production: salesportal.smardt.com

deployment_targets:
  local:
    host: default
    engine: master
    env_file: .envs/.env-dev
  master:
    host: production
    engine: master
    env_file: .envs/.env-production
  develop: &staging
    host: staging
    engine: master
    env_file: .envs/.env-staging
  staging2:
    <<: *staging
    host: staging2

spaces:
  region_name: sgp1
  bucket: bucket_name
  endpoint_url: https://s3.ap-southeast-1.amazonaws.com
  prefix: backups
  # start_after is where you want S3 to start listing from.
  # S3 starts listing after this specified key. start_after can be any key in the bucket.
  start_after: bucket_name/db/db_2025-01-01_08-00-00.sql
  resources:
    - db
    - files
    - translations
  downloads_dir: path-to-store-download-dir

server_setup_script:
  dir: ./confs
  filename: setup.sh

plugins_dir_name: totoro_plugins
```

### Required Environment Variables
Totoro requires certain environment variables to function correctly. Ensure these are set before running any commands:
To set these environment variables in your shell, use:
```
export PGPASSWORD="your_postgres_password"
export AWS_ACCESS_KEY_ID="your_aws_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
```

### Usage
If this is your first time using Totoro, run the following command to initialize your Docker [contexts](https://docs.docker.com/engine/manage-resources/contexts/):
```
totoro init
```

To view general usage and available commands, run:
```
totoro --help
```
```
$ totoro --help

 Options ─────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                 │
│ --show-completion             Show completion for the current shell, to copy it or      |
│                               customize the installation.                               |
│ --help                        Show this message and exit.                               │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────╮
| init      Set up Docker contexts                                                        |
│ login     Login to Azure Container Registry (ACR)                                       │
│ logout    Logout from Azure and Azure Container Registry                                │
│ status    Check Azure and ACR login status                                              │
│ image     Docker image management                                                       │
│ server    Server configuration management                                               │
│ spaces    Download database, translations & files backups from Spaces Object Storage    │
│ compose   Container orchestration                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
```

### Authentication

Before building and pushing Docker images, you need to authenticate with Azure Container Registry:

#### Login to Azure and ACR
```bash
totoro login
```
This command will:
1. Check if you're already logged in to Azure (skips browser auth if authenticated)
2. Provide the link for Azure authentication via a browser if needed
3. Prompt you to select your Azure subscription
4. Authenticate Docker with your Azure Container Registry

**Example output:**
```
Azure Container Registry Login
============================================================

Step 1: Azure Login
✓ Already logged in to Azure

Step 2: ACR Login (smardtacrdev)
Login Succeeded

✓ Successfully logged in to smardtacrdev

You can now build and push images!
```

#### Check authentication status
```bash
totoro status
```
Displays your current Azure and ACR login status with account details.

#### Logout
```bash
totoro logout
```
Logs out from both Azure CLI and Docker registry.

### Getting Help for Specific Commands

To see detailed usage, available subcommands, and arguments for each command, use:
```
totoro <command> --help
```

For example, to see all available options for the **compose** command:
```
totoro compose --help
```

This will display:
```
$ totoro compose --help

 Usage: totoro compose [OPTIONS] COMMAND [ARGS]...

 Container orchestration

╭─ Options ──────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                            │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────╮
│ up     Docker compose up                                                               │
│ down   Docker compose down                                                             │
╰────────────────────────────────────────────────────────────────────────────────────────╯
```
You can then run:
```
totoro compose up --help
```
to get details on how to start services.

### Example Usages

#### Authentication
```bash
# Login to Azure and ACR
totoro login

# Check login status
totoro status

# Logout
totoro logout
```

#### Building and Pushing Images

When you run `totoro image build`, Totoro will:
1. Show you the deployment target configuration for your current branch
2. Ask for confirmation before proceeding
3. If the branch is not configured, guide you through creating a new deployment target interactively

```bash
# Build a Docker image (will show confirmation prompt)
totoro image build web

# Push the image to the registry
totoro image push web
```

**Example confirmation prompt:**
```
============================================================
  Deployment Target Configuration
============================================================
  Branch/Tag:  feature-new-ui
  Host:        staging
  Engine:      master
  Env File:    .envs/.env-staging
============================================================

Do you want to proceed with this configuration? [y/N]:
```

**Interactive deployment target creation:**

If your current branch doesn't have a deployment target configured, Totoro will guide you through creating one:

```
⚠️  No deployment target found for branch: feature-new-ui

Would you like to create a new deployment target? [y/N]: y

--- Create New Deployment Target ---

Available hosts:
  [1] staging (staging.smardt.com)
  [2] staging2 (staging2.smardt.com)
  [3] production (salesportal.smardt.com)
  [4] default

Select host (enter number): 1

Fetching available engine branches...

Available engine branches:
  [1] master
  [2] develop
  [3] feature-calculator-v2
  [4] Enter custom branch name

Select engine branch (enter number): 1

Environment file path:
  [1] .envs/.env-dev
  [2] .envs/.env-staging
  [3] .envs/.env-production
  [4] Enter custom path

Select environment file (enter number): 2

--- Summary ---
  Branch/Tag:  feature-new-ui
  Host:        staging
  Engine:      master
  Env File:    .envs/.env-staging

Save this deployment target? [y/N]: y

✓ Deployment target for "feature-new-ui" saved to totoro.yaml
```

#### Container Orchestration
```bash
# Deploy services using Docker Compose
totoro compose up all
```

### Conventions
Totoro relies heavily on conventions to ensure consistency. Users should adhere to the following assumptions for directory structures and file locations:

#### Dockerfiles
Totoro assumes that Dockerfiles follow a structured directory naming convention. For example:
```
totoro image build web
```
This command expects the Dockerfile for the web service to be located at:
```
./dockerfiles/web/web.Dockerfile
```
#### Hosts and Deployment Targets
The totoro.yaml file should define valid hosts and deployment targets as well as chiller selection API branch:

```yaml
hosts:
  staging: staging.server.com
  staging2: staging2.server.com
  production: salesportal.smardt.com

deployment_targets:
  local:
    host: default
    engine: master
    env_file: .envs/.env-dev
  master:
    host: production
    engine: master
    env_file: .envs/.env-production
  develop: &staging
    host: staging
    engine: master
    env_file: .envs/.env-staging
  staging2:
    <<: *staging
    host: staging2
```
- **Hosts**: Named server addresses used for deployment.
- **Deployment Targets**: Map Git branch names to a host, engine branch, and environment file (env_file). Each target tells Totoro which server and settings to use when deploying a specific branch.
- **Engine**: Specifies which branch of the Smardt selection API to use for web service builds.
- Hosts are reusable server definitions.
- Deployment Targets link branches to a host and environment configuration.
- The host field is used as the Docker context during deployment, while env_file sets branch-specific environment variables.

**Note**: New deployment targets can be created interactively using `totoro image build` when building from an unconfigured branch. Totoro will preserve your YAML file formatting when adding new targets.

More info on [Docker profiles](https://docs.docker.com/compose/how-tos/profiles/) and [Docker contexts](https://docs.docker.com/engine/manage-resources/contexts/).

#### Plugins
Totoro functionalities can be extended via plugins. Totoro automatically imports all of the modules in the directory specified in `plugins_dir_name` and mounts them via `app.add_typer(....)`.

### Troubleshooting

#### Missing Prerequisites
If you see errors about missing tools (Azure CLI or Docker), install them:

**Azure CLI:**
```bash
# Ubuntu/Debian/WSL
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# macOS
brew install azure-cli
```

**Docker:**
- Follow the [official Docker installation guide](https://docs.docker.com/get-docker/)

#### Authentication Issues
- If `totoro login` fails, try running `az login` manually first to diagnose Azure CLI issues
- Check that you have access to the Azure Container Registry
- Verify your Azure subscription is active

#### Deployment Target Issues
- Ensure your `totoro.yaml` is in the root directory where you run commands
- Check that host names in the configuration match your actual server addresses
- Verify environment files exist at the specified paths

### Development

#### Setting up the development environment with Nix

If you're contributing to Totoro, you can use Nix for a consistent development environment:

```bash
# Clone the repository
git clone https://github.com/kinoki-choy/totoro.git
cd totoro

# Enter the Nix development shell
nix develop

# The environment is now ready with:
# - Python 3.11
# - Azure CLI
# - Docker
# - All Python dependencies installed in .venv
```

The Nix flake provides an isolated development environment with all required tools and automatically creates a Python virtual environment with Totoro installed in editable mode.