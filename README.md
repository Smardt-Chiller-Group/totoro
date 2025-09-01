## Totoro CLI

Totoro is a Python-based DevOps tool designed to streamline Docker-related commands and simplifies the management of Docker images and services, ensuring consistency across workflows.

### Features
- Docker image management
- Server configuration management
- Download database, translations & files backups from Spaces Object Storage
- Container orchestration

### Installation
Tested against Python (=>3.11.7):

```sh
pip install git+https://github.com/kinoki-choy/totoro.git@v1.0.0
```
or if using UV:
```sh
uv add git+https://github.com/kinoki-choy/totoro.git@v1.0.0
```

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
#   - certbot

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
    env_file: .envs/.env-dev
  master:
    host: production
    env_file: .envs/.env-production
  develop: &staging
    host: staging
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
│ image     Docker image management                                                       │
│ server    Server configuration management                                               │
│ spaces    Download database, translations & files backups from Spaces Object Storage    │
│ compose   Container orchestration                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
```

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
- Build and push a Docker image:
    ```
    totoro image build web
    totoro image push web
    ```
- Deploy services using Docker Compose:
    ```
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
The totoro.yaml file should define valid hosts and deployment targets:

```yaml
hosts:
  staging: staging.server.com
  staging2: staging2.server.com
  production: salesportal.smardt.com

deployment_targets:
  local:
    host: default
    env_file: .envs/.env-dev
  master:
    host: production
    env_file: .envs/.env-production
  develop: &staging
    host: staging
    env_file: .envs/.env-staging
  staging2:
    <<: *staging
    host: staging2
```
- Hosts: Named server addresses used for deployment.
- Deployment Targets: Map Git branch names to a host and environment file (env_file). Each target tells Totoro which server and settings to use when deploying a specific branch.
- Hosts are reusable server definitions.
- Deployment Targets link branches to a host and environment configuration.
- The host field is used as the Docker context during deployment, while env_file sets branch-specific environment variables.

More info on [Docker profiles](https://docs.docker.com/compose/how-tos/profiles/) and [Docker contexts](https://docs.docker.com/engine/manage-resources/contexts/).

#### Plugins
Totoro functionalities can be extended via plugins. Totoro automatically imports all of the modules in the directory specified in `plugins_dir_name` and mounts them via `app.add_typer(....)`.