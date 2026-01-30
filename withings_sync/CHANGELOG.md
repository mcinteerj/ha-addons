# Changelog

## [1.2.0] - 2025-01-30

### Changed
- **Breaking**: Moved all credential storage from `/config/` to `/data/`
  - You will need to re-authenticate after updating
- **Breaking**: Garmin credentials now entered via Web UI instead of addon config
  - Removed `garmin_username` and `garmin_password` from addon options
  - More consistent UX - both services configured in same place
- Light theme aligned with Home Assistant design language
- Fixed ingress routing (404 on authorize/sync endpoints)

### Security
- Garmin credentials file has restrictive permissions (600)
- Removed deprecated config map

## [1.1.1] - 2025-01-30

### Fixed
- Initial release with ingress support

## [1.0.0] - 2025-01-30

### Added
- Initial addon structure
- Flask web UI for OAuth flow
- Withings to Garmin sync via withings-sync CLI
