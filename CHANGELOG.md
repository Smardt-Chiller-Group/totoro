# Changelog

All notable changes to this project will be documented in this file.

## [1.3.2] - 13th Jun, 2026
### Added
- `default` is now a valid host context in `totoro.yaml`
- New `get_deployment_target` method for centralised host lookup

### Changed
- `resolve_docker_context` and `resolve_env_file` now delegate to `get_deployment_target`
- Context switching via CLI flags (e.g. `--context`) is removed; `deployment_target` in `totoro.yaml` is now the only mechanism
- Compose commands now inject `SERVER_NAME` as an environment variable
- `utils.run()` now accepts a command as a string instead of a list

## [1.2.2] - 21st May, 2026
### Changed
- `totoro build` now enforces branch-aware dirty build policies. Aborts immediately on uncommitted changes for `master`; prompts for confirmation on all other branches.

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
- Tag argument in `totoro image` command is now optional. If ommited, it will be resolved automatically.
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

