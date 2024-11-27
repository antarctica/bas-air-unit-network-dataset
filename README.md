# BAS Air Unit Network Dataset

Utility to process routes and waypoints used by the British Antarctic Survey (BAS) Air Unit.

## Overview

**Note:** This project is focused on needs within the British Antarctic Survey. It has been open-sourced in case it is
of interest to others. Some resources, indicated with a '🛡' or '🔒' symbol, can only be accessed by BAS staff or
project members respectively. Contact the [Project Maintainer](#project-maintainer) to request access.

### Purpose

To support the BAS Air Unit manage their network of routes and waypoints such that:

* information is internally consistent, through defined structures and constraints
* information is interoperable between different systems, through the use of open/standard formats
* information is well described and sharable with other teams, through distribution as datasets (through the 
  [Ops Data Store 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store))

### Background

This project was developed in response to discussions and requests with the BAS Air Unit to review and simplify the 
process they used to manage their network of waypoints, and to ensure its future sustainability.

BAS staff can read more about this background in this 
[GitLab issue 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-support/-/issues/134).

### Limitations

This service has a number of limitations, including:

* the Air Unit Network utility does not support multiple, or additional, networks
* the Air Unit Network utility does not require route names to follow the required naming convention
* the Air Unit Network utility does not require waypoint identifiers to be unique across all waypoints
* the Air Unit Network utility does not require waypoint comments to follow the required GPX comment structure
* the Air Unit Network utility does not require waypoints within imported routes to be listed as standalone waypoints
* comments for waypoints use an overly complex structure to support an ad-hoc serialisation format within GPX files
* Unicode characters (such as emoji) are unsupported in route/waypoint names, comments, etc.

Some or all of these limitations may be addressed in future improvements to this project. See the project 
[issue tracker 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues) for details.

## Install

```
$ python -m pip install bas-air-unit-network-dataset
```

## Usage

### Loading features from GPX files

If loading waypoints and routes from a GPX file, these requirements must be met in addition to the constraints from the 
[Information Model](IMPLEMENTATION.md#information-model):

- the GPX comment field should consist of 8 elements, in the order below, separated with a vertical bar (`|`):
  - *name*: a full, or formal name for the waypoint (maximum 17 characters)
  - *co-located with*: name of a related depot, instrument and/or other feature - use `N/A` if not applicable
  - *last accessed at*: date waypoint was last accessed in the form `YYYY-MM-DD` - use `N/A` if unvisited
  - *last accessed by*: pilot that that last accessed waypoint - use `N/A` if unvisited
  - *fuel*: amount of fuel at a waypoint, as a positive whole number - use `N/A` if not applicable
  - *elevation_ft*: elevation at waypoint, as a positive whole number - use `N/A` if not applicable
  - *comment*: any other information - use `N/A` if not applicable
  - *category*: a grouping value - use `N/A` if not applicable

For example (a co-located, previously visited, waypoint with a full name, additional information and a category):

* identifier: `ALPHA`
* comment: `Alpha 001 | Dog | 2014-12-24 | CW | 10 | 130 | Bring treats. | Animals`

For example (a standalone, unvisited, waypoint with no full/formal name or additional information):

* identifier: `BRAVO`
* comment: `N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A`

**Note:** Only the 'name' in a comment will be included in FPL waypoints.

### Creating outputs

See the [`tests/create_outputs.py`](tests/create_outputs.py) for an example of converting a set of input waypoints and 
routes into output formats, creating an [Output Directory](#output-directory), using an instance of the 
`MainAirUnitNetwork` class.

The `Network` class (on which the `MainAirUnitNetwork` class is based) includes a built-in method for loading features 
from a GPX file (used in the example above). To load data from other data sources, construct `Waypoint` and `Route` 
features directly and add to a `Network` object.

### Output directory

When using the `MainAirUnitNetwork` class from this project to process waypoints and routes, an output directory 
similar to the example below will be created:

```
/path/to/output/directory
├── CSV
│   ├── 00_WAYPOINTS_DDM_2023_12_03.csv
│   └── 00_WAYPOINTS_DD_2023_12_03.csv
├── FPL
│   ├── 00_NETWORK_2023_12_03.fpl
│   ├── 01_BRAVO_TO_ALPHA.fpl
│   ├── 02_BRAVO_TO_BRAVO.fpl
│   └── 03_BRAVO_TO_LIMA.fpl
├── GPX
│   ├── 00_NETWORK_2023_12_03.gpx
└── PDF
    └── 00_WAYPOINTS_2023_12_03.pdf
```

#### Access control

The Air Unit Network utility does not include access control. If needed, access controls should be applied to the
output directory, as is the case for the [Ops Data Store 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store) for 
example.

## Implementation

See [Implementation](IMPLEMENTATION.md) documentation.

## Developing

See [Developing](DEVELOPING.md) documentation.

## Releases

- [all releases 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/releases)
- [latest release 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/releases/permalink/latest)
- [PyPi](https://pypi.org/project/bas-air-unit-network-dataset/)

## Project maintainer

British Antarctic Survey ([BAS](https://www.bas.ac.uk)) Mapping and Geographic Information Centre
([MAGIC](https://www.bas.ac.uk/teams/magic)). Contact [magic@bas.ac.uk](mailto:magic@bas.ac.uk).

The project lead is [@felnne](https://www.bas.ac.uk/profile/felnne).

## License

Copyright (c) 2022 - 2024 UK Research and Innovation (UKRI), British Antarctic Survey (BAS).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
