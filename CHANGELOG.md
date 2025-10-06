# Changelog

All notable changes to this project will be documented in this file.

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

