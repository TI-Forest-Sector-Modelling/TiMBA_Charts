# Changelog

## [v0.4.0] - 2026-03-09
### Added:
- Added automated testing of all dashboards.
- Added NAI graphs to forest_db.
- Added legend for worldmap_db.
- Implemented trade dashboard with plots.
- Added global background color configuration in default_parameters.
- Added tabs for dashboard navigation.

### Changed:
- Adapted bitrade_db, forest_db, overview_db, and price_db to new project layout and unified structure.
- Shifted plots to a centralized PlotManager class.
- Implemented unified color scheme for sceanrios accross all dashboards.
- Replaced forest stock plot in overview_db.
- Optimized forest plots in PlotManager.
- Extracted layout functions from overview_db for reusability.

### Fixed:
- Fixed worldmap bug in overview_db.
- Fixed formatting issues in worldmap_db, price_db, forest_db, and overview_db.
- Fixed and unified units across all dashboards.
- Fixed download button functionality in all dashboards.
- Fixed bug limiting only one filter element in titles.
- Fixed titles in overview_db.

### Removed:
- Removed outdated analysis tools.
- Outcommented tests for import data that were not stable.


## [v0.3.0] - 2025-12-16
### Added:
- Introduced a new multi-page dashboard structure with a unified layout and additional pages for overview and validation.
- Added a data download feature to handle cases where no paths are provided by the user.
- Added a default color palette and extended options for custom color styling.
- Added uniform color and printing style configuration for dashboards and export.

### Changed:
- Updated entry point for the multi-page dashboard to simplify access.
- Updated the dashboard image location to use an external repository and adjusted related links.
- Harmonized the dashboard layout design, including overview and validation dashboards, and aligned button and download elements.

### Fixed:
- Fixed bugs related to dynamic navigation between dashboards and user-defined paths.
- Improved robustness of the new multi-page navigation by refining the object-oriented entry point and print settings.

### Removed:
- Deleted deprecated files related to the previous dashboard implementations and layout versions.
