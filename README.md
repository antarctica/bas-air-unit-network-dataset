# BAS Air Unit Network Dataset

Management of the network of routes and waypoints used by the British Antarctic Survey (BAS) Air Unit.

Including a utility to process routes and waypoints for use in handheld and aircraft GPS devices used by the Air Unit.

## Overview

### Purpose

To support the BAS Air Unit manage their network of routes and waypoints such that:

* information is internally consistent, through defined structures and constraints
* information is interoperable between different systems, through the use of open/standard formats
* information is well described and sharable with other teams, through distribution as datasets

### Background

This project was developed in response to discussions and requests with the BAS Air Unit to review and simplify the 
process they used to manage their network of waypoints, and to ensure its future sustainability.

BAS staff can read more about this background in this 
[GitLab issue](https://gitlab.data.bas.ac.uk/MAGIC/ops-support/-/issues/134) [Internal].

### Status

This project is a mature alpha. This means:

* all, or parts, of this project:
  * may, but should not, stop working (due to regressions or instability)
  * may not work correctly, or as expectedly (including destructively)
  * may change at any time (in terms of implementation or functionality)
* documentation may be missing or incorrect
* support for this project is provided on a best efforts / 'as is' basis
* outputs from this project should not be relied upon for operation use without through scrutiny

### Limitations

This service has a number of limitations, including:

* the default base map used in Garmin BaseCamp is not useful for Antarctica
* the Air Unit Network utility is only supported on Windows computers
* the Air Unit Network utility does not support multiple users importing data at the same time
* the Air Unit Network utility does not create backups when importing new data
* the Air Unit Network utility does not require route names to follow the required naming convention
* the Air Unit Network utility does not require waypoint identifiers to be unique across all waypoints
* the Air Unit Network utility does not require waypoint comments to follow the required structure
* the Air Unit Network utility does not require waypoints within imported routes to be listed as standalone waypoints
* comments for waypoints use an overly complex structure to support an ad-hoc serialisation format
* Unicode characters (such as emoji) cannot be used in route/waypoint names, comments, etc.
* CSV outputs are not designed for printing (i.e. column formatting and page breaks)
* the workspace directory and its data is only available at Rothera (i.e. it isn't synced back to Cambridge)

Some or all of these limitations will be addressed in [Future improvements](#future-improvements) to this project.

### Future improvements

See the project [issue tracker](#issue-tracking) for a backlog of planned features and ideas to further improve this
project.

## Usage

### Workspace directory

The *workspace directory* contains all files related to this project. This directory should be shared between all 
users/computers that require access by storing on a shared drive or synced folder accessible to relevant users.

**Note:** To create a new workspace directory, see the [Setup](#setup) section.

A typical/example workspace directory contains:

```
/path/to/workspace/directory
├── bas-air-unit-network-dataset.gpkg
├── input.gpx
└── output/
    ├── CSV/
    │   ├── 00_WAYPOINTS_2022_07_08.csv
    │   ├── 00_WAYPOINTS_2022_07_08_DD.csv
    ├── FPL/
    │   ├── 00_WAYPOINTS_2022_07_08.fpl
    │   ├── 01_BRAVO_TO_ALPHA.fpl
    │   ├── 02_BRAVO_TO_BRAVO.fpl
    │   └── 03_bBRAVO_TO_LIMA.fpl
    └── GPX/
        └── 00_NETWORK_2022_07_08.gpx
```

* the `output/` directory contains files for use in GPS devices and as print-outs, organised by file type
* the `input.gpx` GPX file contains routes and waypoints *exported* from an editor to be *imported* into the GeoPackage
* the `bas-air-unit-network-dataset.gpkg` GeoPackage file used internally by the Air Unit Network utility for storage

#### Access control

The Air Unit Network utility does not include access control, therefore the permissions applied to the working directory
should be used if access to information needs to be restricted. It is recommended that write permissions on the 
directory are restricted to users that have permission to edit information.

### Workflow

**Note:** You need to complete the steps in the [Setup](#setup) section to complete this workflow.

To update waypoints and routes (the network) and create new files for use in GPS devices and as print-outs:

1. create waypoints and routes in an editor, such as Garmin BaseCamp, QGIS, etc. as per the software's instructions
1. export waypoints and routes from this editor as a GPX file as per the software's instructions
1. [import the GPX file into the Air Unit Network utility](#importing-waypoints-and-routes-into-the-network-utility)
4. use the utility to [export the network in a range of formats](#exporting-waypoints-and-routes-using-the-network-utility) 
   (CSV, GPX and FPL)

#### Rules for creating waypoint features

Create waypoints as per these conventions (based on the [Information Model](#information-model):

- identifier/callsign: maximum 6 characters
- comment: a string consisting of 5 elements in the order below, each separated with a `|` (vertical bar) character:
    1. *name*: a full, or formal name for the waypoint (maximum 17 characters)
    2. *co-located with*: name of a related depot, instrument and/or other feature - use `N/A` if not relevant
    3. *last accessed at*: date waypoint was last accessed in the form `YYYY-MM-DD` - use `N/A` if unvisited
    4. *last accessed by*: pilot that that last accessed waypoint - use `N/A` if unvisited
    5. *other information*: any other information - use `N/A` if not relevant

For example (a co-located, previously visited, waypoint with a full name and additional information):

* identifier: `ALPHA`
* comment: `Alpha 001 | Dog | 2014-12-24 | CW | Bring treats.`

For example (a standalone, unvisited, waypoint with no full/formal name or additional information):

* identifier: `BRAVO`
* comment: `N/A | N/A | N/A | N/A | N/A`

**Note:** Only the 'name' in a comment will be included in FPL waypoints.

#### Rules for creating route features

Create routes as per the route naming convention: 

- `{Route Number}_{Start Waypoint Identifier}_To_{End Waypoint Identifier}`
- for example: `01_ALPHA_TO_BRAVO`
- the first route should use `01` as a route number, `00` is a reserved value and should not be used
- the maximum route number is `99`

#### Importing waypoints and routes into the Network utility

**WARNING!** Importing replaces all existing information. Ensure you have suitable backups of existing data.

**Note:** Output for this example is based on the [Test Network](#test-network).

```
# if needed activate virtual environment
$ source /path/to/venv/bin/activate

$ /path/to/venv/bin/airnet import --dataset-path /path/to/bas-air-unit-network-dataset.gpkg --input-path /path/to/input.gpx
Dataset is located at: /path/to/bas-air-unit-network-dataset.gpkg
Input is located at: /path/to/input.gpx

<NetworkManager : 12 Waypoints - 3 Routes>

Waypoints [12]:
01. <Waypoint 01G7T144RF7WENM8PBKC15W1YB :- [ALPHA_], POINT (-75.01463335007429 -69.91516669280827)>
02. <Waypoint 01G7T144RFVMA8XSD2NES8EFW0 :- [BRAVO_], POINT (-75.19033329561353 -70.8301666751504)>
03. <Waypoint 01G7T144RFBM65YQC317D7XCC8 :- [CHARLE], POINT (-71.49899996817112 -71.76016665995121)>
04. <Waypoint 01G7T144RFXNTDVKXCEBTW4DSJ :- [DELTA_], POINT (-66.09375 -72.7509999834001)>
05. <Waypoint 01G7T144RFMSAZZQEAD5ANBTAN :- [ECHO__], POINT (-61.611166689544916 -73.45333331264555)>
06. <Waypoint 01G7T144RFVJFRW1VY0MFQNW06 :- [FOXTRT], POINT (-70.22449999116361 -73.17583330906928)>
07. <Waypoint 01G7T144RFSM18AJ9G2A3GKGZ9 :- [GOLF__], POINT (-70.3125 -74.20000003650784)>
08. <Waypoint 01G7T144RFFA3B2009P6FAXC3H :- [HOTEL_], POINT (-65.43449998833239 -74.42566668614745)>
09. <Waypoint 01G7T144RFP1F3EB58V421Y65S :- [INDIA_], POINT (-63.017566641792655 -75.70466665551066)>
10. <Waypoint 01G7T144RFTW3RN38TNR6TJ585 :- [JULIET], POINT (-58.93050002865493 -76.34150002151728)>
11. <Waypoint 01G7T144RFV5N138VMTC80WTA1 :- [KILO__], POINT (-55.37100004032254 -77.16683333739638)>
12. <Waypoint 01G7T144RFNDB0TEMY911J8VN7 :- [LIMA__], POINT (-50.8461666572839 -78.08921668678522)>

Routes [3]:
01. <Route 01G7T144RF040ETQSEBGS73A9Z :- [01_BRAVO_TO_ALPHA], 2 waypoints, Start/End: BRAVO  / ALPHA >
02. <Route 01G7T144RFAN8RKG006NJ2CC4B :- [02_BRAVO_TO_BRAVO], 9 waypoints, Start/End: BRAVO  / BRAVO >
03. <Route 01G7T144RFGTXKKJGA1V6CM24F :- [03_BRAVO_TO_LIMA], 8 waypoints, Start/End: BRAVO  / LIMA  >

Import complete
```

#### Exporting waypoints and routes using the Network utility

```
# if needed activate virtual environment
$ source /path/to/venv/bin/activate

$ /path/to/venv/bin/airnet export --dataset-path /path/to/bas-air-unit-network-dataset.gpkg --output-path /path/to/output/dir/
Dataset is located at: /path/to/bas-air-unit-network-dataset.gpkg
Output directory is is: /path/to/output/dir/

- CSV export complete
- GPX export complete
- FPL export complete

Export complete
```

## Implementation

This project consists of:

* a description and schema for the main BAS Air Unit travel network (routes and waypoints)
* a Python library and command line utility to:
  * store waypoints and routes in a structured/neutral format (currently a GeoPackage)
  * import waypoints and routes from a GPX file from an editor such as Garmin BaseCamp, QGIS, etc.
  * export waypoints and routes into a range of output formats (currently CSV, GPX and Garmin FPL)

### Information model

The BAS Air Unit Network information model consists of two entities, forming two, related, datasets:

1. **Waypoints**: Features representing landing sites used by the Air Unit, usually co-located with a BAS Operations 
   depot, field camp or a science/monitoring instrument 
2. **Routes**: Features representing formally defined, frequently travelled, paths between two or more Waypoints, as 
   opposed to ad-hoc paths

For example:

* **Waypoints**: Fossil Bluff
* **Routes**: Rothera to Fossil Bluff

There is a many-to-many relationship between Waypoints and Routes. I.e. a Waypoint can be part of many Routes, and 
Routes can contain many Waypoints.

**Note:** This information model is abstract and requires implementing. See the [Data model](#data-model) section for 
the current implementation.

#### Waypoints (information model)

| Property           | Name             | Type                           | Occurrence | Length | Description                                                | Example                                   |
|--------------------|------------------|--------------------------------|------------|--------|------------------------------------------------------------|-------------------------------------------|
| `id`               | ID               | String                         | 1          | 1 - .. | Unique identifier                                          | '01G7MY680N332AW9H9HR9SG15T'              |
| `identifier`       | Identifier       | String                         | 1          | 1 - 6  | Unique reference                                           | 'ALPHA'                                   |
| `geometry`         | Geometry         | Geometry (2D Point, EPSG:4326) | 1          | -      | Position or location as a single coordinate                | 'SRID=4326;Point(-75.014648 -69.915214)'  |
| `name`             | Name             | String                         | 0-1        | 1 - 17 | Full or formal name                                        | 'Alpha 001'                               |
| `colocated_with`   | Co-located With  | String                         | 0-1        | 1 - .. | Features (from other domains) associated with the waypoint | 'Depot: Foo'                              |
| `last_accessed_at` | Last Accessed At | Date                           | 0-1        | 1 - .. | When the Waypoint was last accessed or visited             | '2014-12-24'                              |
| `last_accessed_by` | Last Accessed By | String                         | 0-1        | 1 - .. | Who last accessed or visited the Waypoint                  | 'Conwat'                                  |                            
| `comment`          | Comment          | String                         | 0-1        | 1 - .. | Freetext description or comments                           | 'Alpha 001 is on a high ridge ...'        |

##### ID (Waypoint)

IDs:

* MUST be unique
* MUST NOT be based on any information contained within the Waypoint
* MAY use any format/scheme:
  * the same scheme SHOULD be used for all IDs
  * non-sequential schemes are recommended

**Note:** This ID can be used to refer to each Waypoint in other systems (i.e. as a foreign identifier).

##### Identifiers (Waypoint)

Identifiers:

* MUST be between 1 and 6 uppercase alphanumeric characters without spaces (A-Z, 0-9)
* MUST be unique across all Waypoints

##### Geometry (Waypoint)

Geometries:

* MUST be expressed in decimal degrees using the EPSG:4326 projection
* MUST consist of a longitude (X) and latitude (Y) dimension (2D point)

##### Name (Waypoint)

If specified:

* MUST be between 1 and 17 uppercase alphanumeric or space characters (A-Z, 0-9, ' ')

##### Co-located with (Waypoint)

No special comments.

##### Last accessed at (Waypoint)

If specified:

* MUST be expressed as an [ISO 8601-1:2019](https://www.iso.org/standard/70907.html) date instant

##### Last accessed by (Waypoint)

If specified:

* MUST unambiguously reference an individual
* MAY use any scheme:
  * the same scheme SHOULD be used for all Waypoints

##### Comment (Waypoint)

No special comments.

#### Routes (information model)

| Property          | Name      | Type                      | Occurrence | Length | Description           | Example                      |
|-------------------|-----------|---------------------------|------------|--------|-----------------------|------------------------------|
| `id`              | ID        | String                    | 1          | 1 - .. | Unique identifier     | '01G7MZB9X0R8S7RTNYAMAQKHE4' |
| `name`            | Name      | String                    | 1          | 1 - .. | Name or reference     | '01_ALPHA_TO_BRAVO'          |
| `waypoints`       | Waypoints | List of Waypoint entities | 2-n        | -      | Sequence of Waypoints | -                            |

##### ID (Route)

IDs:

* MUST be unique
* MUST NOT be based on any information contained within the Route
* MAY use any format/scheme:
  * the same scheme SHOULD be used for all IDs
  * non-sequential schemes are recommended

**Note:** This ID can be used to refer to each Route in other systems (i.e. as a foreign identifier).

##### Name (Route)

Names:

* MUST use the format `{Sequence}_{First Waypoint Identifier}_TO_{Last Waypoint Identifier}`, where `{Sequence}` is 
  a zero padded, two character, auto-incrementing prefix (e.g. '01', '02', ..., '99').

##### Waypoints (Route)

Waypoints in Routes:

* MUST be a subset of the set of Waypoints
  * i.e. waypoints in routes MUST be drawn from a common set, rather than defined ad-hoc or inline within a Route
* MUST be expressed as a sequence:
  * i.e. a list in a specific order from a start to finish via any number of other places
* MAY be included multiple times
  * i.e. the start and end can be the same Waypoint, or a route may pass through the same waypoint multiple times

### Data model

The BAS Air Unit Network data model implements the [Information model](#information-model) using three entities:

1. **Waypoint**: Point features with attributes
2. **Route**: Features to contextualise a set of Waypoints, with attributes (such as route name)
3. **RouteWaypoint**: join between a Waypoint and a Route, with contextual attributes (such as sequence within route)

This data model describes how these entities are:

* persisted as features within layers within an OGC GeoPackage (version 1.2)
* represented as Python class instances (objects)

This GeoPackage and the data it contains, is considered the Source of Truth and definitive version/format.

**Note:** This data model does not describe how entities are encoded in specific [Output Formats](#output-formats).

**Note:** This data model does not describe specifics about how entities are encoded in GeoPackages (i.e. database 
schema), or describe GeoPackage meta tables, which are managed automatically by libraries used by this utility.

#### FIDs

Feature Identifiers (FIDs) are created automatically when features are persisted to GeoPackages. FIDs are unique 
auto-incrementing integers, and used as primary keys within database tables.

FIDs SHOULD be considered an implementation detail, and SHOULD be ignored in favour of ID properties (i.e. 'ID' rather 
than 'FID').

FIDs SHOULD NOT be exposed to end users and their values or structure MUST NOT be relied upon.

#### ULIDs

[Universally Unique Lexicographically Sortable Identifier (ULID)](https://github.com/ulid/spec)s are the scheme used 
for identifiers (IDs).

These IDs MAY be exposed to end users.

#### Waypoints (data model)

Python class: 

* `Waypoint` (single waypoint)
* `WaypointCollection` (waypoints set)

GeoPackage layer: `waypoints`

| Property           | Name             | Data Type     | Nullable | Unique | Max Length | Notes                                                |
|--------------------|------------------|---------------|----------|--------|------------|------------------------------------------------------|
| `fid`              | Feature ID       | Integer       | No       | Yes    | -          | Internal to database, primary key, auto-incrementing |
| `id`               | ID               | ULID (String) | No       | Yes    | -          | -                                                    |
| `identifer`        | Identifier       | String        | No       | Yes    | 6          | -                                                    |
| `geometry`         | Geometry         | 2D Point      | No       | No     | -          | -                                                    |
| `name`             | Name             | String        | Yes      | No     | 17         | -                                                    |
| `colocated_with`   | Co-located With  | String        | Yes      | No     | -          | -                                                    |
| `last_accessed_at` | Last Accessed At | Date          | Yes      | No     | -          | -                                                    |
| `last_accessed_by` | Last Accessed By | String        | Yes      | No     | -          | -                                                    |
| `comment`          | Comment          | String        | Yes      | No     | -          | -                                                    |

#### Routes (data model)

Python class: 

* `Route` (single route)
* `RouteCollection` (routes set)

GeoPackage layer: `routes`

| Property | Name       | Data Type       | Nullable | Unique | Max Length | Notes                                                |
|----------|------------|-----------------|----------|--------|------------|------------------------------------------------------|
| `fid`    | Feature ID | Integer         | No       | Yes    | -          | Internal to database, primary key, auto-incrementing |
| `id`     | ID         | ULID (String)   | No       | Yes    | -          | -                                                    |
| `name`   | Name       | String          | No       | Yes    | -          | -                                                    |

#### Route Waypoints (data model)

Python class: 

* `RouteWaypoint` (single waypoint in route)

GeoPackage layer: `route_waypoints`

| Property      | Name        | Data Type      | Nullable | Unique             | Max Length | Notes                                                                       |
|---------------|-------------|----------------|----------|--------------------|------------|-----------------------------------------------------------------------------|
| `fid`         | Feature ID  | Integer        | No       | Yes                | -          | Internal to database, primary key, auto-incrementing                        |
| `route_id`    | Route ID    | ULID (String)  | No       | Yes                | -          | Foreign key to Route entity                                                 |
| `waypoint_id` | Waypoint ID | ULID (String)  | No       | Yes                | -          | Foreign key to Waypoint entity                                              |
| `sequence`    | Sequence    | Integer        | No       | Yes (within Route) | -          | Position of waypoint within a route, value must be unique within each route |

**Note:** Though the `route_id` and `waypoint_id` columns are effectively foreign keys, though they are not configured 
as such within the GeoPackage.

### Source data

Input/source data MUST be saved in a GPX (GPS Exchange Format) version 1.1 file to be imported into this project.

**Note:** Only GPX files produced by Garmin BaseCamp are supported. GPX files produced by other tools may also work but 
are not formally supported.

Limitations:

* Garmin BaseCamp does not support custom GPX extensions, except Garmin's own, limiting fields to the core GPX 
  specification
* this requires non-standard fields (such as `waypoint.last_accessed_at`) to be added to the comment freetext field, 
  making it more complex (see notes in the [Creating a Waypoint](#rules-for-creating-waypoint-features) section)

### Test network

A network consisting of 12 waypoints and 3 routes is used to:

1. test various edge cases
2. provide consistency for repeatable testing
3. prevent needing to use real data that might be sensitive

**WARNING!** This test network is entirely fictitious. It MUST NOT be used for any real navigation.

The canonical test network is stored in `tests/resources/test-network/test-network.json` and is versioned using a date
in the `meta.version` property. A QGIS project is also provided to visualise the test network and ensure derived 
outputs match expected test data.

This dataset does not follow any particular standard or output format as it's intended to be a superset of other 
formats and support properties that may not be part of any standard. Derived versions of the network in some standard 
formats are also available (from the same directory) for testing data loading, etc.

#### Updating test network

If updating the test network, ensure to:

1. update the version attribute in the test network to the current date
1. recreate derived versions of the network as needed (for example the GPX derived output) [1]
1. use the network utility to generate sample exports [2]
1. manually verify the QGIS project for visualising the network is correct and update/fix as needed

[1]

```
$ poetry run python tests/create_derived_test_outputs.py
```

[2]

```
$ poetry run airnet import -d tests/resources/test-network/bas-air-unit-network-dataset.gpkg -i tests/resources/test-network/test-network.gpx
$ poetry run airnet export -d tests/resources/test-network/bas-air-unit-network-dataset.gpkg -o tests/resources/test-network/reference-outputs/
```

After running, ensure all dates in files are updated to values set in `tests/compare_outputs.py`.

### Output formats

#### Supported formats

**Note:** The GeoPackage used in the [Data Model](#data-model) is not a supported output format.

Format use-cases:

| Format | Use Case                          |
|--------|-----------------------------------|
| CSV    | Human readable, printed reference |
| GPX    | Machine readable, handheld GPS    |
| FPL    | Machine readable, aircraft GPS    |

Format details:

| Format | Name                   | Version  | File Type | Encoding    | Open Format          | Restricted Attributes | Extensions Available | Extensions Used  |
|--------|------------------------|----------|-----------|-------------|----------------------|-----------------------|----------------------|------------------|
| CSV    | Comma Separated Value  | N/A      | Text      | UTF-8 + BOM | Yes                  | No                    | No                   | N/A              |
| GPX    | GPS Exchange Format    | 1.1      | XML       | UTF-8       | Yes                  | Yes                   | Yes                  | No               |
| FPL    | (Garmin) Flight Plan   | 1.0      | XML       | UTF-8       | No (Vendor Specific) | Yes                   | Yes                  | No               |

Outputs produced for each format: 

| Format | Each Waypoint | Each Route | All Waypoints (Only) | All Routes (Only) | Waypoints and Routes (Combined) |
|--------|---------------|------------|----------------------|-------------------|---------------------------------|
| CSV    | No            | No         | Yes                  | No [1]            | No                              |
| GPX    | No            | No         | No [1]               | No [1]            | Yes                             |
| FPL    | No            | Yes        | Yes                  | No                | No                              |

Where 'All Waypoints (Only)' outputs are produced, waypoints will be sorted alphabetically.

[1] These outputs can be produced but are intentionally excluded as they aren't used by the Air Unit. See this 
[GitLab issue](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/101) [Internal] for details.

#### Output file names

Output files use an internal naming convention for all formats:

| Export Type                     | File Name (Pattern)                 | File Name (Example)           |
|---------------------------------|-------------------------------------|-------------------------------|
| Each Waypoint                   | N/A                                 | N/A                           |
| Each Route                      | `{route name}.ext`                  | `01_ALPHA_TO_BRAVO.ext`       |
| All Waypoints (Only)            | `00_WAYPOINTS_{current date}.ext`   | `00_WAYPOINTS_2014_12_24.ext` |
| All Routes (Only)               | `00_ROUTES_{current date}.ext`      | `00_ROUTES_2014_12_24.ext`    |
| Waypoints and Routes (Combined) | `00_NETWORK_{current date}.ext`     | `00_NETWORK_2014_12_24.ext`   |

Where `.ext` is a relevant file extension for each format (i.e. `.csv` for CSV outputs).

#### Output format - CSV

Notes:

* for compatibility with Microsoft Excel, CSV outputs include the UTF-8 Byte Order Mark (BOM), which may cause issues
  with other tools/applications
* CSV outputs use the first row as a column names header
* outputs produced for all routes use a `route_name` column to distinguish rows related to each route
* `waypoint.geometries` can optionally be included as separate latitude (Y) and longitude (X) columns in either:
  * decimal degrees (`latitude_dd`, `longitude_dd` columns) - native format
  * degrees, decimal minutes (`latitude_ddm`, `longitude_ddm` columns) - format used in aviation

Limitations:

* all properties are encoded as strings, without type hints using extended CSV schemes etc.
* CSV outputs are not validated

#### Output format - GPX

Notes:

* GPX outputs are validated against the GPX XSD schema automatically

Limitations:

* GPX metadata fields (author, last updated, etc.) are not currently populated
* the GPX comment field is set to the `waypoint.name` property only, as GPS devices used by the Air Unit only support 
  comments of upto 16 characters

#### Output format - FPL

Notes:

* FPL outputs are validated against a custom version of the Garmin [FPL XSD schema](#fpl-xml-schema) automatically
* route names will use spaces instead of underscores in FPL files, as underscores aren't allowed in FPL route names

Limitations:

* the `waypoint.colocated_with`, `waypoint.last_accessed_at`, `waypoint.last_accessed_by` and `waypoint.comment` 
  properties are not included in FPL waypoint comments, as they are limited to 17 characters [1]
* underscores (`_`) characters are stripped from route names *within* FPL files (rather than the names *of* FPL 
  files), a local override is used to replace underscores with spaces (` `) to work around this limitation
* FPL metadata fields (author, last updated, etc.) are not currently populated

[1] This limit comes from the specific UI shown in the aircraft GPS used by the BAS Air Unit.

##### FPL XML schema

A copy of the Garmin FPL XML/XSD schema, http://www8.garmin.com/xmlschemas/FlightPlanv1.xsd, is included in this 
project to locally validate generated FPL outputs. This schema cannot be used for validation in its published form, as
it contains a number of invalid regular expressions. These regular expressions have been modified in the schema used 
in this project, which hopefully match Garmin's intentions.

In order to produce FPL files that match those produced by earlier processing scripts used by the BAS Air Unit, a 
number of other changes have been made to the local version of the FPL schema. These include:

* removing the requirement for a `<waypoints-table>` element to be included in all FPL files (relevant to route FPLs)
* removing the requirement for all `<waypoint>` elements within `<route>` elements to be included in a 
  `<waypoint-table>` element (as a consequence of the above)
* altering the regular expression used for the `<country-name>` element to allow the `_` characters

**Note:** It is hoped these local modifications will be removed in future through testing with the in-aircraft GPS.
See [#12](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/32) for more information.

### Python CLI

A Python based utility, `airnet`, is used for:

* importing [Source data](#source-data) into the internal GeoPackage
* exporting data from the internal GeoPackage as [Outputs](#output-formats)
* creating new datasets (setup task, only needs to be performed once)
* describing the contents of a dataset at a high level

This utility provides a Command Line Interface (CLI) using the [Click](https://click.palletsprojects.com/en/8.1.x/) 
framework. To enable users to call the CLI from a shell, without needing to run through Python, the Click CLI instance 
is configured as a console script entrypoint in the `setup.py` generated by Poetry (and defined in `pyproject.toml`)

The Python methods used in the Click CLI call methods from a `NetworkManager` class, which together with a set of 
entity and entity collection classes, is responsible for loading and dumping data.

See `bas_air_unit_network_dataset.__main__:cli` for the Click CLI method.

See `bas_air_unit_network_dataset.__init__:NetworkManager` for the NetworkManager and related classes.

For a list of available commands and their options, run `airnet --help`.

For information on the installed package version, run `airnet --version`.

### CLI environment variables

Parameter values for the `airnet` command line interface (CLI) can be provided using environment variables. These are
typically used when automating commands as part of a script or other automation workflow. 

| Parameter               | Environment Variable  |
|-------------------------|-----------------------|
| `-d` / `--dataset-path` | `AIRNET_DATASET_PATH` |
| `-i` / `--input-path`   | `AIRNET_INPUT_PATH`   |
| `-o` / `--output-path`  | `AIRNET_OUTPUT_PATH`  |

**Note:** Where an option is set on the command line and using an environment variable, the command line value takes
precedence.

## Setup

### Requirements

- Python 3.9+
- libxml2 with `xmlint` binary available on Path
- read/write access to a suitable location for creating a [Workspace Directory](#workspace-directory)

**Note:** As of version 0.3.0, Windows is no longer a supported operating system for running this utility.

### Install Python package

It is strongly recommended to install the [Python Package](#development) in a Python virtual environment:

```
$ python -m venv /path/to/venv
$ source /path/to/venv/bin/activate
$ python -m pip install --upgrade pip
$ python -m pip install bas-air-unit-network-dataset
```

### Set up a workspace directory

Typically, the [Workspace Directory](#workspace-directory) will be located on a shared drive or within a synced folder.

**WARNING:** Running these commands within an existing workspace directory will reset the dataset, deleting any 
existing data. Ensure you have suitable backups of existing data.

```
# if needed activate virtual environment
$ source /path/to/venv/bin/activate
$ /path/to/venv/bin/airnet init --dataset-path '/path/to/workspace/directory'
Dataset will be located at: '/path/to/workspace/directory'

Dataset created at: '/path/to/workspace/directory'
```

## Development

### Local development environment

Check out project:

```
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset.git
$ cd air-unit-network-dataset
```

**Note:** If you do not have access to the BAS GitLab instance, clone from GitHub as a read-only copy instead.

[Poetry](https://python-poetry.org/docs/#installation) is used for managing the Python environment and dependencies.

[pyenv](https://github.com/pyenv/pyenv) is strongly recommended to ensure the Python version is the same as the one
used in externally provisioned environments. This is currently *3.9.18*.

```
$ pyenv install 3.9.18
$ pyenv local 3.9.18
$ poetry install
```

### Running CLI locally

```
$ poetry run airnet [COMMAND] [ARGS]
```

### Editorconfig

For consistency is strongly recommended to configure your IDE or other editor to use the [EditorConfig](https://EditorConfig.org) settings defined in [`.editorconfig`](.editorconfig).

### Dependencies

#### Dependency vulnerability checks

The [Safety](https://pypi.org/project/safety/) package is used to check dependencies against known vulnerabilities.

**WARNING!** As with all security tools, Safety is an aid for spotting common mistakes, not a guarantee of secure code.
In particular this is using the free vulnerability database, which is updated less frequently than paid options.

Checks are run automatically in [Continuous Integration](#continuous-integration). To check locally:

```
$ poetry run safety check --full-report
```

#### Static security scanning

Ruff is configured to run [Bandit](https://github.com/PyCQA/bandit), a static analysis tool for Python.

**WARNING!** As with all security tools, Bandit is an aid for spotting common mistakes, not a guarantee of secure code.
In particular this tool can't check for issues that are only be detectable when running code.

#### `lxml` package (bandit)

Bandit identifies the use of `lxml` classes and methods as a security issue, specifically:

> Element to parse untrusted XML data is known to be vulnerable to XML attacks

The recommendation is to use a *safe* implementation of an XML processor (`defusedxml`) that can avoid entity bombs and 
other XML processing attacks. However, `defusedxml` does not offer all the methods we need and there does not appear
to be such another processor that does provide them.

The main vulnerability this security issue relates to is processing user input that can't be trusted. This isn't really
applicable to this library directly, but rather to where it's used in implementing projects. I.e. if this library is 
used in a service that accepts user input, an assessment must be made whether the input needs to be sanitised.

Within this library itself, the only input that is processed is test records, all of which are assumed to be safe to 
process.

### Code linting

[Ruff](https://docs.astral.sh/ruff/) is used to lint and format Python files. Specific checks and config options are
set in `pyproject.toml`. Linting checks are run automatically in [Continuous Integration](#continuous-integration).

To check locally:

```
$ poetry run ruff check src/ tests/
$ poetry run ruff format --check src/ tests/
```

To format files:

```
$ poetry run ruff format src/ tests/
```

## Testing

Basic end-to-end tests are performed automatically in [Continuous Integration](#continuous-integration) to check the
[Test Network](#test-network) can be processed via the Network Utility [CLI](#usage).

Test outputs are compared against known good reference files in `tests/resources/test-network/reference-outputs/` by
comparing checksums on file contents using the `tests/compare_outputs.py` script.

### Continuous Integration

All commits will trigger a Continuous Integration process using GitLab's CI/CD platform, configured in `.gitlab-ci.yml`.

## Deployment

The Air Unit Network utility is distributed as a Python package installed through Pip from the
[PyPi](https://pypi.org/project/bas-air-unit-network-dataset/) registry.

Source and binary packages are built and published automatically using
[Poetry](https://python-poetry.org) in [Continuous Deployment](#continuous-deployment).

**Note:** Packages for non-tagged commits will use `0.0.0` as a version to indicate they're informal releases.

To build the Python package manually:

```
$ poetry build
```

To publish the Python package to PyPi manually, you will need an API token for the BAS organisational PyPi account,
set as the `POETRY_PYPI_TOKEN_PYPI` environment variable. Then run:

```
$ poetry publish --username british-antarctic-survey
```

### Continuous Deployment

All commits will trigger a Continuous Deployment process using GitLab's CI/CD platform, configured in `.gitlab-ci.yml`.

## Releases

- [all releases 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/releases)
- [latest release 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/releases/permalink/latest)

To create a release, create an issue using the *release* issue template and follow the included checklist.

## Feedback

This project is maintained by the BAS Mapping and Geographic Information Centre
([MAGIC](https://bas.ac.uk/teams/magic)), contactable at: [magic@bas.ac.uk](mailto:magic@bas.ac.uk).

## License

Copyright (c) 2022 - 2023 UK Research and Innovation (UKRI), British Antarctic Survey.

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
