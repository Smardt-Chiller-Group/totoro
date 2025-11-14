# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 14th Nov, 2025
### Added
- **Azure Container Registry Authentication Management**
  - `totoro login` - Smart login with automatic status detection, skips browser auth if already authenticated
  - `totoro logout` - Logout from Azure CLI and Docker registry
  - `totoro status` - Check current Azure and ACR login status with account details
  - Prerequisite validation for Azure CLI and Docker before operations
  
- **Interactive Deployment Target Management**
  - Pre-build confirmation prompt showing deployment configuration (branch, host, engine, env_file)
  - Interactive deployment target creation workflow for unconfigured branches
  - User-friendly numbered menus for host, engine branch, and environment file selection
  - Dynamic engine branch detection from calculator repository with fallback to master
  - Custom branch name entry option for engine selection

### Changed
- `totoro image build` now requires explicit confirmation before building, showing full deployment configuration
- Enhanced error handling with clear, actionable error messages for missing prerequisites

## [1.2.1] - 6th Oct, 2025
### Changed
- Clean up and removed confusing boolean parameters

## [1.2.0] - 5th Oct, 2025
### Added
- `totoro.yaml` now accepts 'engine' parameter for identifying correct branch to use for chiller branch selection API.

## [1.1.0] - 1st Sept, 2025
### Added
- Utility functions for resolving Docker tag, context and env file
### Changed
- Tag argument in `totoro image` command is now optional. If omitted, it will be resolved automatically.
- `totoro image`, `totoro compose`, `totoro server` commands no longer require `--context` option

## [1.0.0] - 18th Aug, 2025
### Added
- Initial release of **Totoro CLI**.
- Docker image management (`totoro image build/push`).
- Server configuration management (`totoro server`).
- Download backups (databases, translations, files) from Spaces Object Storage (`totoro spaces`).
- Container orchestration with Docker Compose (`totoro compose up/down/exec`).
- Support for service profiles, hosts, and environment configuration via `totoro.yaml`.
- Plugin support for extending Totoro with custom commands.