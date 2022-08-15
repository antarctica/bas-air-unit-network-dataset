# BAS Air Unit Network Dataset - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

* output format table incorrectly stated CSV files produced a network output
  [#96](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/96)
* incorrect installation instructions for setting the user vs. system PATH environment variable
  [#91](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/91)

## [0.1.0] - 2022-07-14

### Added

* core `Waypoint`, `WaypointCollection`, `Route`, `RouteCollection`, `RouteWaypoint` classes, and initial 
  `NetworkManager` class
  [#5](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/5)
* CSV export
  [#7](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/7)
* GPX export
  [#2](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/2)
* FPL export
  [#4](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/4)
* degrees decimal minutes (DDM) coordinate formatting for CSV export
  [#36](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/36)
* GeoPackage persistence layer
  [#9](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/9)
* basic CLI
  [#41](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/41)
* GPX import from Garmin BaseCamp
  [#47](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/47)
* information/data model documentation
  [#10](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/11)
* project documentation
  [#35](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/35)
* installation bundle for required software
  [#52](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/52)
* create test network
  [#6](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/6)
* create QGIS visualisation for test network
  [#27](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/27)
* GitHub repository mirroring
  [#88](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/88)
* PyPi publishing (manually)
  [#79](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/79)

### Fixed

* waypoints table being duplicated in FPL export
  [#38](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/38)
* description/comment property not included in CSV export
  [#40](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/40)
* waypoints in network GPX file ony including waypoints used in routes
  [#53](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/53)
* CSV newline line separator incorrect on Windows
  [#63](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/63)
* incorrect file names used in output directory
  [#66](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/66)
