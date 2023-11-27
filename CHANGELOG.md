# BAS Air Unit Network Dataset - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed [BREAKING!]

* 3D geometry support, waypoint geometries may no longer specify elevation values
  [#150](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/150)
* Support for comments in route waypoints
  [#141](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/141)
* Support for installing/running on Windows
  [#198](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/198)

### Added

* Flake8 code linting
  [#83](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/83)
* Bandit static security analysis
  [#85](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/85)
* Safety vulnerability scanning
  [#84](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/84)
* Black code formatting
  [#81](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/81)
* Basic Continuous Integration
  [#82](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/82)
* Improved Continuous Integration, verifying test network can be minimally processed
  [#168](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/168)
* Versioning to the test network
  [#173](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/173)
* Script to recreate test network as GeoJSON for testing in QGIS
  [#174](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/174)
* Continuous Deployment
  [#167](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/167)
* GitLab release issue template
  [#124](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/124)

### Fixed

* File encoding for CSV files when opened with Microsoft Excel
  [#185](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/185)
* Addressing security vulnerabilities
  [#195](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/195)
* Correcting double longitude value in convert to DDM function
  [#196](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/196)
* Various bugs and improvements to FPL exporter
  [#197](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/197)

### Changed

* Upgrading Python dependencies
  [#140](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/140)
* Downgrading required Python version to 3.8, for compatibility with the Operations Data Store project
  [#138](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/138)
* Incorporating the test network into this project
  [#172](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/172)
* Waypoints will be sorted by their sequence when added to a route
  [#164](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/164)
* Refactoring classes into more manageable modules
  [#202](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/202)
  [#206](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/206)
* Aligning development environment stack with Ops Data Store
  [#200](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/200)
* Upgrading to Python 3.9.x
  [#202](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/202)
* Including FPL XSD schema refactored to be included as static file
  [#203](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/203)

### Removed

* Installation bundle concept
  [#199](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/199)

## [0.2.2] - 2022-10-21

### Added

* Note that on Windows the working directory must be on the same drive as the Python interpreter
  [#128](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/128)

### Fixed

* Creating datasets in a path with missing parent directories
  [#128](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/128)
* Files encoded as UTF-8 with BOM, which could not be parsed correctly as input files
  [#130](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/130)

## [0.2.1] - 2022-09-29

### Added

* Fix for missing Microsoft Visual C++ redistributable
  [#122](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/122)

### Fixed

* Typo in LibXML2 installation instructions
  [#121](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/121)

## [0.2.0] - 2022-09-28 [BREAKING!]

### Changed [BREAKING!]

* `designator` field in waypoints changed to `identifier`
  [#114](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/114)
* Splitting `comment` field into `name` and `comment` fields (as part of overall GPX `cmt` field)
  [#99](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/99)
* `description` field maximum length limited to maximum FPL comment length
  [#105](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/105)
* FPL comment length limited to 17 characters
  [#104](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/104)

### Added

* Option to create CSV outputs with DD and/or DDM lat lon fields
  [#94](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/94)
* Missing documentation for setting CLI parameters using environment variables
  [#65](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/65)
* Background section in README
  [#109](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/109)

### Fixed

* Corrected to use spaces rather than underscores in FPL route names
  [#95](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/95)
* Command example parameters used the wrong values
  [#97](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/97)
* Output format table incorrectly stated CSV files produced a network output
  [#96](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/96)
* Incorrect installation instructions for setting the user vs. system PATH environment variable
  [#91](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/91)

### Changed

* Sorting waypoints alphabetically - does not apply to route waypoints
  [#100](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/100)
* Omitting some generated outputs to suit Air Unit requirements
  [#101](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/101)
* Adjusting method parameters to be more descriptive/intuitive
  [#51](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/51)

## [0.1.0] - 2022-07-14

### Added

* Core `Waypoint`, `WaypointCollection`, `Route`, `RouteCollection`, `RouteWaypoint` classes, and initial 
  `NetworkManager` class
  [#5](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/5)
* CSV export
  [#7](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/7)
* GPX export
  [#2](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/2)
* FPL export
  [#4](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/4)
* Degrees decimal minutes (DDM) coordinate formatting for CSV export
  [#36](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/36)
* GeoPackage persistence layer
  [#9](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/9)
* Basic CLI
  [#41](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/41)
* GPX import from Garmin BaseCamp
  [#47](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/47)
* Information/data model documentation
  [#10](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/11)
* Project documentation
  [#35](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/35)
* Installation bundle for required software
  [#52](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/52)
* Test network data
  [#6](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/6)
* QGIS visualisation for test network
  [#27](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/27)
* GitHub repository mirroring
  [#88](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/88)
* PyPi publishing (manually)
  [#79](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/79)

### Fixed

* Waypoints table being duplicated in FPL export
  [#38](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/38)
* Description/comment property not included in CSV export
  [#40](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/40)
* Waypoints in network GPX file ony including waypoints used in routes
  [#53](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/53)
* CSV newline line separator incorrect on Windows
  [#63](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/63)
* Incorrect file names used in output directory
  [#66](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/66)
