# BAS Air Unit Network Dataset Implementation

## Overview

This project consists of:

* a description and schema for the main BAS Air Unit travel network (routes and waypoints)
* a Python library to:
  * import waypoints and routes from a GPX file, or other data source
  * export waypoints and routes into a range of output formats (currently CSV, GPX and Garmin FPL)

## Information model

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

### Waypoints (information model)

| Property           | Name             | Type                           | Occurrence | Length | Description                                                | Example                                  |
|--------------------|------------------|--------------------------------|------------|--------|------------------------------------------------------------|------------------------------------------|
| `id`               | ID               | String                         | 1          | 1 - .. | Unique identifier                                          | '01G7MY680N332AW9H9HR9SG15T'             |
| `identifier`       | Identifier       | String                         | 1          | 1 - 6  | Unique reference                                           | 'ALPHA'                                  |
| `geometry`         | Geometry         | Geometry (2D Point, EPSG:4326) | 1          | -      | Position or location as a single coordinate                | 'SRID=4326;Point(-75.014648 -69.915214)' |
| `name`             | Name             | String                         | 0-1        | 1 - 17 | Full or formal name                                        | 'Alpha 001'                              |
| `colocated_with`   | Co-located With  | String                         | 0-1        | 1 - .. | Features (from other domains) associated with the waypoint | 'Depot: Foo'                             |
| `last_accessed_at` | Last Accessed At | Date                           | 0-1        | 1 - .. | When the Waypoint was last accessed or visited             | '2014-12-24'                             |
| `last_accessed_by` | Last Accessed By | String                         | 0-1        | 1 - .. | Who last accessed or visited the Waypoint                  | 'Conwat'                                 |
| `fuel`             | Fuel             | Integer                        | 0-1        | 1 - .. | Fuel (amount)                                              | '10'                                     |
| `elevation_ft`     | Elevation (ft)   | Integer                        | 0-1        | 1 - .. | Elevation (in feet)                                        | 1200                                     |
| `comment`          | Comment          | String                         | 0-1        | 1 - .. | Freetext description or comments                           | 'Alpha 001 is on a high ridge ...'       |

#### ID (Waypoint)

IDs:

* MUST be unique
* MUST NOT be based on any information contained within the Waypoint
* MAY use any format/scheme:
  * the same scheme SHOULD be used for all IDs
  * non-sequential schemes are recommended

**Note:** This ID can be used to refer to each Waypoint in other systems (i.e. as a foreign identifier).

#### Identifiers (Waypoint)

Identifiers:

* MUST be between 1 and 6 uppercase alphanumeric characters without spaces (A-Z, 0-9)
* MUST be unique across all Waypoints

#### Geometry (Waypoint)

Geometries:

* MUST be expressed in decimal degrees using the EPSG:4326 projection
* MUST consist of a longitude (X) and latitude (Y) dimension (2D point)

#### Name (Waypoint)

If specified:

* MUST be between 1 and 17 uppercase alphanumeric or space characters (A-Z, 0-9, ' ')

#### Co-located with (Waypoint)

No special comments.

#### Last accessed at (Waypoint)

If specified:

* MUST be expressed as an [ISO 8601-1:2019](https://www.iso.org/standard/70907.html) date instant

#### Last accessed by (Waypoint)

If specified:

* MUST unambiguously reference an individual
* MAY use any scheme:
  * the same scheme SHOULD be used for all Waypoints

#### Fuel (Waypoint)

If specified:

* MUST be a positive integer

#### Elevation (Waypoint)

If specified:

* MUST be a positive integer

#### Comment (Waypoint)

No special comments.

### Routes (information model)

| Property          | Name      | Type                      | Occurrence | Length | Description           | Example                      |
|-------------------|-----------|---------------------------|------------|--------|-----------------------|------------------------------|
| `id`              | ID        | String                    | 1          | 1 - .. | Unique identifier     | '01G7MZB9X0R8S7RTNYAMAQKHE4' |
| `name`            | Name      | String                    | 1          | 1 - .. | Name or reference     | '01_ALPHA_TO_BRAVO'          |
| `waypoints`       | Waypoints | List of Waypoint entities | 2-n        | -      | Sequence of Waypoints | -                            |

#### ID (Route)

IDs:

* MUST be unique
* MUST NOT be based on any information contained within the Route
* MAY use any format/scheme:
  * the same scheme SHOULD be used for all IDs
  * non-sequential schemes are recommended

**Note:** This ID can be used to refer to each Route in other systems (i.e. as a foreign identifier).

#### Name (Route)

Names:

* MUST use the format `{Sequence}_{First Waypoint Identifier}_TO_{Last Waypoint Identifier}`, where `{Sequence}` is 
  a zero padded, two character, auto-incrementing prefix (e.g. '01', '02', ..., '99').

#### Waypoints (Route)

Waypoints in Routes:

* MUST be a subset of the set of Waypoints
  * i.e. waypoints in routes MUST be drawn from a common set, rather than defined ad-hoc or inline within a Route
* MUST be expressed as a sequence:
  * i.e. a list in a specific order from a start to finish via any number of other places
* MAY be included multiple times
  * i.e. the start and end can be the same Waypoint, or a route may pass through the same waypoint multiple times

## Data model

For use within the Python library included in this project, and as a reference to implementors for storing entities, a 
data model implementing the [Information model](#information-model) is available. For the later use-case, this data 
model assumes the use of a relational model, specifically for SQLite (as an OGC GeoPackage) and PostgreSQL. 

This data model uses three entities:

1. **Waypoint**: Point features with attributes
2. **Route**: Features to contextualise a set of Waypoints, with attributes (such as route name)
3. **RouteWaypoint**: join between a Waypoint and a Route, with contextual attributes (such as sequence within route)

**Note:** This data model does not describe how entities are encoded in specific [Output Formats](#output-formats).

### FIDs

Feature Identifiers (FIDs) are created automatically for features without one. FIDs are unique auto-incrementing 
integers, suitable for use as primary keys within relational database.

FIDs SHOULD be considered an implementation detail, and SHOULD be ignored in favour of ID properties (i.e. 'ID' rather 
than 'FID') outside the specific technology being used.

Consequently, FIDs SHOULD NOT be exposed to end users and their values or structure MUST NOT be relied upon.

### ULIDs

[Universally Unique Lexicographically Sortable Identifier (ULID)](https://github.com/ulid/spec)s are the scheme used 
for identifiers (IDs).

These IDs MAY be exposed to end users.

### Waypoints (data model)

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
| `fuel`             | Fuel             | Integer       | Yes      | No     | -          | -                                                    |
| `elevation_ft`     | Elevation (ft)   | Integer       | Yes      | No     | -          | -                                                    |
| `comment`          | Comment          | String        | Yes      | No     | -          | -                                                    |

### Routes (data model)

Python class: 

* `Route` (single route)
* `RouteCollection` (routes set)

GeoPackage layer: `routes`

| Property | Name       | Data Type       | Nullable | Unique | Max Length | Notes                                                |
|----------|------------|-----------------|----------|--------|------------|------------------------------------------------------|
| `fid`    | Feature ID | Integer         | No       | Yes    | -          | Internal to database, primary key, auto-incrementing |
| `id`     | ID         | ULID (String)   | No       | Yes    | -          | -                                                    |
| `name`   | Name       | String          | No       | Yes    | -          | -                                                    |

### Route Waypoints (data model)

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

## Output formats

### Supported formats

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
[GitLab issue 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/101) for details.

### Output file names

Output files use an internal naming convention for all formats:

| Export Type                     | File Name (Pattern)                 | File Name (Example)           |
|---------------------------------|-------------------------------------|-------------------------------|
| Each Waypoint                   | N/A                                 | N/A                           |
| Each Route                      | `{route name}.ext`                  | `01_ALPHA_TO_BRAVO.ext`       |
| All Waypoints (Only)            | `00_WAYPOINTS_{current date}.ext`   | `00_WAYPOINTS_2014_12_24.ext` |
| All Routes (Only)               | `00_ROUTES_{current date}.ext`      | `00_ROUTES_2014_12_24.ext`    |
| Waypoints and Routes (Combined) | `00_NETWORK_{current date}.ext`     | `00_NETWORK_2014_12_24.ext`   |

Where `.ext` is a relevant file extension for each format (i.e. `.csv` for CSV outputs).

### Output format - CSV

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

### Output format - GPX

Notes:

* GPX outputs are validated against the GPX XSD schema automatically

Limitations:

* GPX metadata fields (author, last updated, etc.) are not currently populated
* the GPX comment field is set to the `waypoint.name` property only, as GPS devices used by the Air Unit only support 
  comments of upto 16 characters

### Output format - FPL

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

#### FPL XML schema

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
See [#12 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/32) for more information.
