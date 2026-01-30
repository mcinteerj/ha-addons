# Changelog

## [1.2.0] - 2025-01-30

### Changed
- **Breaking**: Moved credential storage from `/config/.withings_sync_data/` to `/data/`
  - You will need to re-authenticate after updating
- Updated run.sh to use bashio
- Removed deprecated `map` config (no longer writes to HA config directory)

### Security
- Added ingress IP restriction (only accepts connections from HA proxy)

## [1.1.1] - 2025-01-30

### Fixed
- Initial release with ingress support

## [1.0.0] - 2025-01-30

### Added
- Initial addon structure
- Flask web UI for OAuth flow
- Withings to Garmin sync via withings-sync CLI
