# BAS Air Unit Network Dataset

Management of the network of routes and waypoints used by the British Antarctic Survey (BAS) Air Unit.

Including a utility for the Air Unit to process routes and waypoints for use in their handheld and aircraft GPS devices.

## Overview

### Purpose

To support the BAS Air Unit manage their network of routes and waypoints such that:

* information is internally consistent, through defined structures and constraints
* information is interoperable between different systems, through the use of open/standard formats
* information is well described and sharable with other teams, through distribution as datasets

### Background

This project was developed in response to discussions and requests with the BAS Air Unit to review and simplify the 
process they used to manage their network of waypoints, and to ensure it's future sustainability.

BAS staff can read more about this background in this 
[GitLab issue](https://gitlab.data.bas.ac.uk/MAGIC/ops-support/-/issues/134) [Internal].

### Status

This project is an early alpha, working towards a Minimal Viable Product (MVP). This means:

* all, or parts, of this project: 
  * may not be working 
  * may stop working at any time
  * may not work correctly, or as expectedly (including destructively)
  * may change at any time (in terms of implementation or functionality)
* documentation may be missing or incorrect
* no support is provided for this project
* no real and/or sensitive information should be used with this project

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
* contextual comments for waypoints within a route (e.g. 'Start of route') cannot be set using Garmin BaseCamp
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

* the `output/` directory contains files for use in GPS devices and as print outs, organised by file type (CSV, GPX 
  and FPL)
* the `input.gpx` file contains routes and waypoints *exported* from Garmin BaseCamp to be *imported* into the Air 
  Unit Network utility
* the `bas-air-unit-network-dataset.gpkg` file is a GeoPackage used internally by the Air Unit Network utility

#### Access control

The Air Unit Network utility does not include access control, therefore the permissions applied to the working directory
should be used if access to information needs to be restricted. It is recommended that wrtite permissions on the 
directory are restricted to users that need to edit information.

### Workflow

**Note:** You need to complete the steps in the [Installation](#installation) section to complete this workflow.

To update waypoints and routes (the network) and create new files for use in GPS devices and as print outs:

1. [waypoints](#managing-waypoints-in-basecamp) and [routes](#managing-routes-in-basecamp) are created and edited using 
   Garmin BaseCamp
2. [export routes and waypoints from BaseCamp](#saving-waypoints-and-routes-from-basecamp) as a GPX file
3. [import the GPX file into the Air Unit Network utility](#importing-waypoints-and-routes-into-the-network-utility)
4. use the utility to [export the network in a range of formats](#exporting-waypoints-and-routes-using-the-network-utility) 
   (CSV, GPX and FPL)

The sub-sections below describe these steps in more detail.

### Managing waypoints in BaseCamp

#### Create a new waypoint

1. from the start menu, launch *BaseCamp*
2. from the upper left hand panel, under *My Collection*, select *BAS Air Unit Network* -> *BAS Air Unit Network*
3. choose the *Create a waypoint* tool (flag icon) from the top middle toolbar (creation tools)
4. select the general location of the waypoint (precise position can be entered later)
5. from the *General* tab of the waypoint properties screen that opens:
   1. enter a suitable *Name* or identifier (maximum 6 characters)
   2. enter a suitable *Comment*, which consists of 5 elements in the order below, each separated with a `|` (vertical 
      bar) character:
      1. *name*: a full, or formal name for the waypoint (maximum 17 characters)
      2. *co-located with*: name of a related depot, instrument and/or other feature - use `N/A` if not relevant
      3. *last accessed at*: date waypoint was last accessed in the form `YYYY-MM-DD` - use `N/A` if unvisited
      4. *last accessed by*: pilot that that last accessed waypoint - use `N/A` if unvisited
      5. *other information*: any other information - use `N/A` if not relevant
6. from the *Advanced* tab:
   1. if necessary, edit the *Position* to the correct latitude and longitude in degrees, decimal minutes (DDM) format
7. close the waypoint properties screen

For example (a co-located, previously visited, waypoint with a full name and additional information):

* name: `ALPHA`
* comment: `Alpha 001 | Dog | 2014-12-24 | CW | Bring treats.`
* position: `S69° 54.910' W75° 00.878'`

For example (a standalone, unvisited, waypoint with no full/formal name or additional information):

* name: `BRAVO`
* comment: `N/A | N/A | N/A | N/A | N/A`
* position: `S70° 49.810' W75° 11.420'`

**Note:** Only the 'name' in a comment will be included in FPL waypoints.

#### Edit an existing waypoint

1. from the start menu, launch *BaseCamp*
2. from the upper left hand panel, under *My Collection*, select *BAS Air Unit Network* -> *BAS Air Unit Network*
3. from the lower left hand panel, right click the waypoint to be edited and select *Get Info*
4. from the waypoint properties screen, update (as needed):
   1. the name (identifier)
   2. comment (see rules above for how comments must be written)
   3. position

### Managing routes in BaseCamp

#### Create a new route

1. from the start menu, launch *BaseCamp*
2. from the upper left hand panel, under *My Collection*, select *BAS Air Unit Network* -> *BAS Air Unit Network*
3. choose the *Create a route* tool (path/network icon) from the top middle toolbar (creation tools)
4. from the window that opens:
   1. enter the *starting* waypoint using the search box
   2. enter the *ending* waypoint using the search box
   3. select the *Go* command
5. from the *Via Points* tab of the route properties screen that opens:
   1. un-tick the *Autoname* checkbox
   2. rename the route as per the route naming convention: 
       * `{Route Number}_{Start Waypoint Identifier}_To_{End Waypoint Identifier}`
       * for example: `01_ALPHA_TO_BRAVO`
       * the first route should use `01` as a route number, `00` is a reserved value and should not be used
   3. if additional waypoints should be added between start and end waypoints:
      1. from the lower left navigation panel, drag waypoints into the route properties screen, in its position within 
         the route
   4. close the route properties screen

#### Edit an existing route

1. from the start menu, launch *BaseCamp*
2. from the upper left hand panel, under *My Collection*, select *BAS Air Unit Network* -> *BAS Air Unit Network*
3. from the lower left hand panel, right click the route to be edited and select *Get Info*
4. to remove a waypoint from the route:
   1. right click the route waypoint from the list and select *Remove*
5. to add a new waypoint to the route:
   1. from the lower left navigation panel, drag waypoints into the route properties screen, in its position within 
      the route
6. if the start or end waypoint in the route has changed, update the route name (see rules above for format)

### Saving waypoints and routes from BaseCamp 

1. from the start menu, launch *BaseCamp*
2. from the upper left hand panel, under *My Collection*, select *BAS Air Unit Network* -> *BAS Air Unit Network*
3. from the *File* menu, select *Export "BAS Air Unit Network"*
4. name the file `input.gpx` and save to the [Workspace directory](#workspace-directory) (the existing file should be 
   overwritten)
5. set the export format as *GPX v1.1*

### Importing waypoints and routes into the Network utility

1. from the start menu, launch *Command Prompt* and run the commands in [1]

**WARNING:** Importing replaces all existing information. Ensure you have suitable backups of existing data.

[1]

**Note:** If viewing this documentation as a PDF, some commands below may disappear off the page. If you select the 
line you should be able to copy into a tool such as Notepad to view it in full.

```
$ C:\ProgramData\Miniconda3\envs\airnet\Scripts\activate.bat

# navigate to the workspace directory
(airnet) $ cd '/path/to/workspace/directory'

(airnet) $ C:\ProgramData\Miniconda3\envs\airnet\python.exe C:\ProgramData\Miniconda3\envs\airnet\Scripts\airnet.exe import --dataset-path bas-air-unit-network-dataset.gpkg --input-path input.gpx
Dataset is located at: /path/to/workspace/directory/bas-air-unit-network-dataset.gpkg
Input is located at: /path/to/workspace/directory/input.gpx

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

### Exporting waypoints and routes using the Network utility

1. from the start menu, launch *Command Prompt* and run the commands in [1]

**Note:** If you encounter an error similar to [2], ensure you install the 
[Microsoft Visual C++ Redistributable](#microsoft-visual-c-redistributable) from the installation bundle.

[1]

**Note:** If viewing this documentation as a PDF, some commands below may disappear off the page. If you select the 
line you should be able to copy into a tool such as Notepad to view it in full.

```
$ C:\ProgramData\Miniconda3\envs\airnet\Scripts\activate.bat

# navigate to the workspace directory
(airnet) $ cd '/path/to/workspace/directory'

(airnet) $ C:\ProgramData\Miniconda3\envs\airnet\python.exe C:\ProgramData\Miniconda3\envs\airnet\Scripts\airnet.exe export --dataset-path bas-air-unit-network-dataset.gpkg --output-path output/
Dataset is located at: /path/to/workspace/directory/bas-air-unit-network-dataset.gpkg
Output directory is is: /path/to/workspace/directory/output

- CSV export complete
- GPX export complete
- FPL export complete

Export complete
```

[2]

> The code execution cannot proceed because VCRUNTIME140.dll was not found. Reinstalling the program may fix this 
> problem.

## Installation

### Install software

**Note:** You will need an internet connection, administrator rights and access to the 
[Installation bundle](#installation-bundle) to install the Air Unit Network utility.

To install software needed to manage the Air Unit Network dataset:

1. ensure all required Windows updates are installed
2. download, or copy from a hard drive, the [Installation bundle](#installation-bundle)
   1. these instructions assume you will download, or copy, the bundle to your *Downloads* directory
3. from the installation bundle, install Garmin BaseCamp, and optionally, QGIS:
   1. run `garmin-basecamp-installer.exe` to install Garmin BaseCamp
   2. optionally, run `qgis-installer.msi` to install the Long Term Support (LTS) version of QGIS
4. from the installation bundle, install Miniconda (needed to run the Air Unit Network utility):
   1. run `miniconda-installer.exe` to install Miniconda
   2. select the *All users (requires admin privileges)* installation option when asked 
5. from the installation bundle, install LibXML2 (needed to run the Air Unit Network utility):
   1. unzip the `libxml2.zip` archive to a temporary directory
   2. copy the `libxml2` directory to `C:\Program Files`, such that `C:\Program Files\libxml2\bin\xmllint.exe` exists
   3. from Windows Explorer, right click *This PC* from the left hand panel and click *Properties* 
      1. from the left hand menu of the System Control Panel screen, click *Advanced system settings*
      2. from the *Advanced* tab of the System Properties screen, click *Environment Variables*
      3. from the bottom section (System variables) select the *Path* variable and click *Edit*:
         1. from the Edit environment variable screen, click *New*
         2. enter `C:\Program Files\libxml2\bin` as a new entry (at the bottom of the list)
      4. click *OK*, then *OK*, then *OK* again and close Control Panel
   4. delete the temporary directory created earlier
6. from the installation bundle, install the Air Unit Network utility virtual environment:
   1. unzip the `airnet-virtual-environment.zip` archive to a temporary directory (this will take some time)
   2. from the *View* tab in Explorer, check the *Hidden items* checkbox
   3. copy the `airnet` directory to `C:\ProgramData\Miniconda3\envs`, such that 
   `C:\ProgramData\Miniconda3\envs\airnet\Scripts\airnet.exe` exists 
   4. delete the temporary directory created earlier
   5. optionally, uncheck the *Hidden items* checkbox in Explorer

**Note:** Only versions of software within the Installation Bundle are supported.

#### Microsoft Visual C++ redistributable

In some cases you also need to install the Microsoft Visual C++ Redistributable package, which is needed for LibXML2.

**Note:** Usually a version of this package will already be installed and these instructions are not necessary.

To install the package:

1. from the installation bundle run `microsoft-vc-installer.exe`
2. reboot the computer after installation

### Configure software

#### Configure Garmin BaseCamp

To configure Garmin BaseCamp needed to manage the Air Unit Network dataset:

1. from the start menu, launch *BaseCamp*
2. when asked for an activity type, select *Direct*
3. from the upper left hand panel, under *My Collection*:
   1. right-click and select *New List folder*
   2. name the folder `BAS Air Unit Network`
4. within this new folder:
   1. right-click and select *New List*
   2. name the list `BAS Air Unit Network`
5. from the upper left hand panel, under *My Collection*, select *BAS Air Unit Network* -> *BAS Air Unit Network*
6. from the *File* menu, select *Import into "BAS Air Unit Network"*
7. select the `input.gpx` file from the [Workspace directory](#workspace-directory)

### Installation bundle

The installation bundle is a folder of supported software installers and packages. It is designed to run offline and be
distributed via an external hard-drive.

The definitive installation bundle is stored in the
[MAGIC Office 365 OneDrive](https://nercacuk.sharepoint.com/:f:/s/BASMagicTeam/EvFtTOCBeClCgflcEju58OEBc5xeU0LuTxjxUwQ_V55LVg?e=Fs1gAi)
and is accessible to all BAS staff. When South, MAGIC will hold a copy of the installation bundle on a hard drive.

Software in the installation bundle will be updated periodically after testing, and when new versions of the Air Unit 
Network utility are released.

**Note:** Only versions of software within the Installation Bundle are supported.

## Implementation

This project consists of:

* a description of the waypoints and routes datasets for the BAS Air Unit
* a Python command line utility to:
  * store waypoints and routes in a structured/neutral format (currently a GeoPackage)
  * import waypoints and routes from a GPX file from an editor such as Garmin BaseCamp
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

| Property           | Name             | Type                              | Occurrence | Length | Description                                                | Example                                   |
|--------------------|------------------|-----------------------------------|------------|--------|------------------------------------------------------------|-------------------------------------------|
| `id`               | ID               | String                            | 1          | 1 - .. | Unique identifier                                          | '01G7MY680N332AW9H9HR9SG15T'              |
| `identifier`       | Identifier       | String                            | 1          | 1 - 6  | Unique reference                                           | 'ALPHA'                                   |
| `geometry`         | Geometry         | Geometry (2D/3D Point, EPSG:4326) | 1          | -      | Position or location as a single coordinate                | 'SRID=4326;Point(-75.014648 -69.915214)'  |
| `name`             | Name             | String                            | 0-1        | 1 - 17 | Full or formal name                                        | 'Alpha 001'                               |
| `colocated_with`   | Co-located With  | String                            | 0-1        | 1 - .. | Features (from other domains) associated with the waypoint | 'Depot: Foo'                              |
| `last_accessed_at` | Last Accessed At | Date                              | 0-1        | 1 - .. | When the Waypoint was last accessed or visited             | '2014-12-24'                              |
| `last_accessed_by` | Last Accessed By | String                            | 0-1        | 1 - .. | Who last accessed or visited the Waypoint                  | 'Conwat'                                  |                            
| `comment`          | Comment          | String                            | 0-1        | 1 - .. | Freetext description or comments                           | 'Alpha 001 is on a high ridge ...'        |

##### ID (Waypoint)

IDs:

* MUST be unique
* MUST NOT be based on any information contained within the Waypoint
* MAY use any format/scheme:
  * the same scheme SHOULD be used for all IDs
  * non-sequential schemes are recommended

**Note:** This ID can be used to refer to each Waypoint in other systems (i.e. as an foreign identifier).

##### Identifiers (Waypoint)

Identifiers:

* MUST be between 1 and 6 uppercase alpha-numeric characters without spaces (A-Z, 0-9)
* MUST be unique across all Waypoints

##### Geometry (Waypoint)

Geometries:

* MUST be expressed in decimal degrees using the EPSG:4326 projection.
* MUST consist of either:
  * a longitude (X) and latitude (Y) dimension (2D point)
  * a longitude (X), latitude (Y) and elevation (Z) dimension (3D point)

##### Name (Waypoint)

If specified:

* MUST be between 1 and 17 uppercase alpha-numeric or space characters (A-Z, 0-9, ' ')

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

**Note:** This ID can be used to refer to each Route in other systems (i.e. as an foreign identifier).

##### Name (Route)

Names:

* MUST use the format `{Sequence}_{First Waypoint Identifier}_TO_{Last Waypoint Identifier}`, where `{Sequence}` is 
  a zero padded, auto-incrementing prefix (e.g. '01_', '02_', ..., '99_').

##### Waypoints (Route)

Waypoints in Routes:

* MUST be a subset of the set of Waypoints
  * i.e. waypoints in routes MUST be drawn from a common set, rather than defined ad-hoc or inline within a Route
* MUST be expressed as a sequence:
  * i.e. a list in a specific order from a start to finish via any number of other places
* MUST contain at least 2 Waypoints but MAY contain more:
  * i.e. a start and end
* MAY be included multiple times
  * i.e. the start and end can be the same Waypoint, or a route may pass through the same waypoint multiple times
* MAY include a contextual comment or description
  * e.g. 'Start of route'

### Data model

The BAS Air Unit Network data model implements the [Information model](#information-model) using three entities:

1. **Waypoint**: Point features with attributes
2. **Route**: Features to contextualise a set of Waypoints, with attributes (such as route name)
3. **RouteWaypoint**: join between a Waypoint and a Route, with contextual attributes (such as sequence within route)

This data model describes how these entities are:

* persisted as features within layers within an OGC GeoPackage (version 1.2)
* represented as Python class instances (objects)

This GeoPackage, and the data it contains, is considered the Source of Truth and definitive version/format.

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
| `geometry`         | Geometry         | 2D/3D Point   | No       | No     | -          | -                                                    |
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
| `comment`     | Comment     | String         | Yes      | No                 | -          | -                                                                           |

**Note:** Though the `route_id` and `waypoint_id` columns are effectively foreign keys, they are not configured as 
such within the GeoPackage.

### Source data

Input/source data MUST be saved in a GPX (GPS Exchange Format) version 1.1 file to be imported into this project.

**Note:** Only GPX files produced by Garmin BaseCamp are supported. GPX files produced by other tools may also work but 
are not formally supported.

Limitations:

* Garmin BaseCamp does not support custom GPX extensions, except Garmin's own, limiting fields to the core GPX 
  specification
* this requires non-standard fields (such as `waypoint.last_accessed_at`) to be added to the comment freetext field, 
  making it more complex (see notes in the [Creating a Waypoint](#create-a-new-waypoint) section)

### Test network

A test network of 12 waypoints and 3 routes is used to:

1. test various edge cases
2. provide consistency for repeatable testing
3. prevent needing to use real data that might be sensitive

**Note:** Route and waypoints in the test network are arbitrary and do not reflect any actual features.

**WARNING!** This test network is entirely fictitious. It MUST NOT be used for any real navigation.

A [Workspace Directory](#workspace-directory) for the test network is maintained in the
[MAGIC Office 365 OneDrive](https://nercacuk.sharepoint.com/:f:/s/BASMagicTeam/EhBAbE0tTDxCt298WEPOWoMBtuV7yxOYuJ8bPslVdKlASQ)
and is accessible to all BAS staff. When South, MAGIC will hold a copy of the test network on a hard drive.

A QGIS project is provided to visualise the test network and ensure exported outputs match expected test data.

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

| Format | Name                   | Version  | Encoding | Open Format          | Restricted Attributes | Extensions Available | Extensions Used  |
|--------|------------------------|----------|----------|----------------------|-----------------------|----------------------|------------------|
| CSV    | Comma Separated Value  | N/A      | Text     | Yes                  | No                    | No                   | N/A              |
| GPX    | GPS Exchange Format    | 1.1      | XML      | Yes                  | Yes                   | Yes                  | No               |
| FPL    | (Garmin) Flight Plan   | 1.0      | XML      | No (Vendor Specific) | Yes                   | Yes                  | No               |

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

* CSV outputs use the first row as a column names header
* outputs produced for all routes use a `route_name` column to distinguish rows related to each route
* `waypoint.geometries` can optionally be included as separate latitude (Y) and longitude (X) columns in either:
  * decimal degrees (`latitude_dd`, `longitude_dd` columns) - native format
  * degrees, decimal minutes (`latitude_ddm`, `longitude_ddm` columns) - format used in aviation

Limitations:

* all properties are encoded as strings, without type hints using extended CSV schemes etc.
* `waypoint.geometries` containing an elevation (Z) dimension are not included in CSV outputs
* CSV outputs are not validated

#### Output format - GPX

Notes:

* GPX outputs are validated against the GPX XSD schema automatically

Limitations:

* GPX metadata fields (author, last updated, etc.) are not currently populated
* the `waypoint.name`, `waypoint.colocated_with`, `waypoint.last_accessed_at`, `waypoint.last_accessed_by` 
  and `waypoint.comment`, properties are combined into the GPX comment field, as GPX lacks fields for these properties
* `waypoint.geometries` containing an elevation (Z) dimension are not included in GPX outputs

#### Output format - FPL

Notes:

* FPL outputs are validated against a custom version of the Garmin [FPL XSD schema](#fpl-xml-schema) automatically
* route names will use spaces instead of underscores in FPL files, as underscores aren't allowed in FPL route names

Limitations:

* the `waypoint.colocated_with`, `waypoint.last_accessed_at`, `waypoint.last_accessed_by` and `waypoint.comment` 
  properties are not included in FPL waypoint comments, as they are limited to 17 characters [1]
* underscores (`_`) characters are stripped from route names *within* FPL files (rather than the names *of* FPL 
  files), a local override is used to replace underscores with spaces (` `) to workaround this limitation
* FPL metadata fields (author, last updated, etc.) are not currently populated
* `waypoint.geometries` containing an elevation (Z) dimension are not included in FPL outputs

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
| ----------------------- | --------------------- |
| `-d` / `--dataset-path` | `AIRNET_DATASET_PATH` |
| `-i` / `--input-path`   | `AIRNET_INPUT_PATH`   |
| `-o` / `--output-path`  | `AIRNET_OUTPUT_PATH`  |

**Note:** Where an option is set on the command line and using an environment variable, the command line value takes
precedence.

## Setup

### Populate the installation bundle

**Note:** You will need appropriate rights within the BAS MAGIC team OneDrive to complete these steps.

To populate the [Installation Bundle](#installation-bundle):

* download the latest Garmin BaseCamp installer (Windows) and rename to `garmin-basecamp-installer.exe`
* download the latest LTS QGIS installer (Windows) and rename to `qgis-installer.msi`
* download the latest MiniConda installer (Python 3.9, Windows 64 bit) and rename to `miniconda-installer.exe`
* download the latest LibXML2 Windows build:
  * visit the [LibXML2](https://gitlab.gnome.org/GNOME/libxml2/-/tree/master/) Gnome project
  * view the latest Continuous Deployment pipeline
  * view the `cmake:msvc` job
  * download the artefact
  * extract the artefact Zip, rename the containing directory `libxml2` and rezip the directory as `libxml2.zip`
* download the 
  [Microsoft Visual C++ 2015 Redistributable Update 3 RC](https://www.microsoft.com/en-us/download/confirmation.aspx?id=52685) 
  package [1] and rename to `microsoft-vc-installer.exe`
* create a `build` directory and:
  * download the latest 7-Zip installer and rename to `7zip-installer.exe`

Before saving installers to the Installation Bundle, test them in a [deployment VM](#setup-a-windows-deployment-vm).

[1] This specific version (14.0.24123) was used because the latest version available at the time of testing (14.32.
31332, Sept 2022) did not work. In future, it may be that another version is needed, especially if the version of 
LibXML2 changes.

### Setup a workspace directory

1. using Windows Explorer, create a suitable directory to use a Workspace (typically on a shared drive or within a 
   synced folder)
2. from the start menu, launch *Command Prompt* and run the commands in [1]

**WARNING:** Running these commands within an existing workspace directory will reset the dataset, deleting any 
existing data. Ensure you have suitable backups of existing data.

**Note:** Due to an internal limitation, on Windows computers the workspace directory must be on the same drive as
the Python interpreter. This will almost always be the `C:` drive.

[1]

**Note:** If viewing this documentation as a PDF, some commands below may disappear off the page. If you select the 
line you should be able to copy into a tool such as Notepad to view it in full.

```
$ C:\ProgramData\Miniconda3\envs\airnet\Scripts\activate.bat

(airnet) $ C:\ProgramData\Miniconda3\envs\airnet\python.exe C:\ProgramData\Miniconda3\envs\airnet\Scripts\airnet.exe init --dataset-path '/path/to/workspace/directory'
Dataset will be located at: '/path/to/workspace/directory'

Dataset created at: '/path/to/workspace/directory'
```

### Setup a Windows deployment VM

**Note:** You will access to the BAS MAGIC resource pool in the BAS vSphere instance to complete these steps.

To create a test VM:

1. login to the [BAS vSphere](https://bsv-vcsa-s1.nerc-bas.ac.uk/ui/) instance
2. from the left panel, switch to the second view (to see templates)
3. from the left panel, select *[root]* -> *Cambridge* -> *BASDEV* -> *air-unit-test-template*
4. right-click and select *New VM from this template*:
   1. select a suitable name (e.g. `air-unit-test5`) and choose the MAGIC folder/resource pool in the *BASDEV* cluster
5. power on the resulting VM (the network may initially show as disconnected but will usually add itself)
6. login as the IEUser with the shared password `Passw0rd!`.

To create the VM template used above:

1. download the VMware version of the 
   [Microsoft Edge test VMs](https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/)
2. follow [these instructions](https://gitlab.data.bas.ac.uk/WSF/bas-base-images#vcentre) to create a VM template, 
   making changes as needed:
   1. name the VM and template `air-unit-test`
   2. set the RAM to 8GB
   3. you should not need to add a virtual network interface or CD device, as this will already be setup

## Development

### Development environment

Git and [Poetry](https://python-poetry.org) are required to set up a local development environment of this project.

**Note:** If you use [Pyenv](https://github.com/pyenv/pyenv), this project sets a local Python version for consistency.

```shell
# clone from the BAS GitLab instance if possible
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset.git

# setup virtual environment
$ cd air-unit-network-dataset
$ poetry install
```

### Running commands in development

Within a [Development Environment](#development-environment) use Poetry to test CLI commands. E.g.:

```
$ poetry run airnet --help
```

### Dependencies

Python dependencies for this project are managed with [Poetry](https://python-poetry.org) in `pyproject.toml`.

#### Adding new dependencies

To add a new (development) dependency:

```shell
$ poetry add [dependency] (--dev)
```

### Testing

Automated tests are not currently implemented (see 
[#16](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/16) for more information).

#### Manual outputs testing

Manual testing of outputs is strongly encouraged prior to a release.

These should aim to be as comprehensive as possible, rather than only testing the outputs currently needed. This 
currently requires manual/ad-hoc modification of the `NetworkManager.dump_*()` methods as shown in this commit:

* https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/blob/9892b56c1669bd88dfd5b7212c2d05861c7b5fa0/src/bas_air_unit_network_dataset/__init__.py#L1112
* https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/blob/9892b56c1669bd88dfd5b7212c2d05861c7b5fa0/src/bas_air_unit_network_dataset/__init__.py#L1134

## Deployment

The Air Unit Network utility is distributed in two forms:

1. a Python package that can be installed through Pip from the
   [PyPi](https://pypi.org/project/bas-air-unit-network-dataset/) registry
2. a packaged Anaconda environment

**Note:** Both distributions require OS dependencies to be installed separately (namely GDAL and LibXML2), see the 
[Installation](#installation) section for more information.

### Python package

The Python package is standard, pure Python Pip package, built by Poetry as a binary wheel and source package.

To build the Python package manually:

```
$ poetry build
```

To publish the Python package to PyPi manually, you will need an API token for the BAS organisational PyPi account,
set as the `POETRY_PYPI_TOKEN_PYPI` environment variable. Then run:

```
$ poetry publish --username british-antarctic-survey
```

### Packaged Anaconda environment

The packaged Anaconda environment uses [Conda Pack](https://conda.github.io/conda-pack/) to create an OS/platform 
specific archive of an Anaconda virtual environment, such that dependencies can be copied and installed offline. 
This is designed for use in running the Air Unit Network utility in Antarctica.

**Note:** This process will produce an environment that can be run on Windows (10), x86 64 bit computers only.

First, [Create a Python Package](#python-package). Then within a 
[Windows Deployment VM](#setup-a-windows-deployment-vm):

1. connect to OneDrive, such that the [Installation Bundle](#installation-bundle) can be accessed and updated
2. from the Installation Bundle, run `miniconda-installer.exe`, installing for all users
3. from the 'build' directory in the Installation Bundle, run the 7Zip installer (`7z.exe`)
4. from the start menu, launch *Anaconda PowerShell Prompt* with admin privileges and run the commands in [1]
5. from the user *Downloads* directory, extract `airnet.tar.gz` using 7-zip: 
   1. then, extract `airnet.tar` to `airnet/`
   2. then, right-click `airnet/` -> *Send to* -> *Compressed (zipped) folder* to produce `airnet.zip`
   3. rename `airnet.zip` to `airnet-virtual-environment.zip`
   4. copy `airnet.zip` to the definitive copy of the [Installation Bundle](#installation-bundle), replacing the 
      existing file

[1]

```shell
(base) $ cd $env:userprofile
(base) $ cd ./Downloads

(base) $ conda create -n airnet
(base) $ conda activate airnet
(airnet) $ conda config --env --add channels conda-forge
(airnet) $ conda config --env --set channel_priority strict
(airnet) $ conda install fiona
(airnet) $ python -m pip install bas-air-unit-network-dataset

(airnet) $ conda activate base
(base) $ conda install -c conda-forge conda-pack
(base) $ conda pack -n airnet -o airnet.tar.gz
```

## Release procedure

For all releases:

1. create a release branch
2. [manually test outputs](#manual-outputs-testing)
3. close release in `CHANGELOG.md`
4. bump package version `poetry version [minor/patch]`
5. build and publish [Python package](#python-package) to PyPi
6. build a [Packaged Anaconda Environment](#packaged-anaconda-environment)
7. convert project README to PDF using [markdowntopdf](https://www.markdowntopdf.com) and update in installation bundle
8. push changes, merge the release branch into `main` and tag with version
9. update the GitLab release with:
    * a link to the relevant milestone(s)
    * change log entries
    * link to [PyPi package](https://pypi.org/project/bas-air-unit-network-dataset/#history)
    * link to PDF version of documentation (share link to document in SharePoint)
    * link to installation bundle (share link to archive in SharePoint)
10. compress the [Installation Bundle](#installation-bundle) into a 7Zip archive (to allow fr transfer South via AMS) 
11. copy the [Installation Bundle](#installation-bundle) and [Test Network](#test-network) to a hard drive to take South

## Feedback

The maintainer of this project is the BAS Mapping and Geographic Information Centre (MAGIC), they can be contacted at:
[magic@bas.ac.uk](mailto:magic@bas.ac.uk).

## Issue tracking

This project uses issue tracking, see the
[Issue tracker](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues) for more information.

**Note:** Read & write access to this issue tracker is restricted. Contact the project maintainer to request access.

## License

Copyright (c) 2022 UK Research and Innovation (UKRI), British Antarctic Survey.

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
