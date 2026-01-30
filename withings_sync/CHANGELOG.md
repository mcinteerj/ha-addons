# Changelog

## [1.4.0] - 2025-01-30

### Added
- API token authentication for external sync requests
- Token display in Web UI with copy button for easy automation setup
- `/api-token` endpoint (ingress-only) to retrieve token

### Changed
- `/sync` endpoint now requires Bearer token for non-ingress requests
- Updated DOCS with automation examples using rest_command

### Security
- External API calls require authentication token
- Token auto-generated on first use, stored with 600 permissions

## [1.3.0] - 2025-01-30

### Added
- Exposed port 8099 for automation triggers via rest_command

## [1.2.0] - 2025-01-30

### Changed
- **Breaking**: Moved all credential storage from `/config/` to `/data/`
- **Breaking**: Garmin credentials now entered via Web UI instead of addon config
- Light theme aligned with Home Assistant design language
- Fixed ingress routing using X-Ingress-Path header

### Security
- Garmin credentials file has restrictive permissions (600)

## [1.1.1] - 2025-01-30

### Fixed
- Initial release with ingress support

## [1.0.0] - 2025-01-30

### Added
- Initial addon structure
- Flask web UI for OAuth flow
- Withings to Garmin sync via withings-sync CLI
