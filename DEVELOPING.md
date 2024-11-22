# BAS Air Unit Network Dataset - Development Documentation

## Local development environment

Requirements:

* Python 3.9 ([pyenv](https://github.com/pyenv/pyenv) recommended)
* [Poetry](https://python-poetry.org/docs/#installation)
* Git (`brew install git`)
* libxml2 with `xmlint` binary available on Path

Setup:

```
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset.git
$ cd air-unit-network-dataset
$ pyenv install 3.9.18
$ pyenv local 3.9.18
$ poetry install
```

**Note:** If you do not have access to the BAS GitLab instance, clone from GitHub as a read-only copy instead.

## Dependencies

### Vulnerability scanning

The [Safety](https://pypi.org/project/safety/) package is used to check dependencies against known vulnerabilities.

**WARNING!** As with all security tools, Safety is an aid for spotting common mistakes, not a guarantee of secure code.
In particular this is using the free vulnerability database, which is updated less frequently than paid options.

Checks are run automatically in [Continuous Integration](#continuous-integration). To check locally:

```
$ poetry run safety scan
```

## Linting

### Ruff

[Ruff](https://docs.astral.sh/ruff/) is used to lint and format Python files. Specific checks and config options are
set in [`pyproject.toml`](./pyproject.toml). Linting checks are run automatically in
[Continuous Integration](#continuous-integration).

To check linting locally:

```
$ poetry run ruff check src/ tests/
```

To run and check formatting locally:

```
$ poetry run ruff format src/ tests/
$ poetry run ruff format --check src/ tests/
```

### Static security analysis

Ruff is configured to run [Bandit](https://github.com/PyCQA/bandit), a static analysis tool for Python.

**WARNING!** As with all security tools, Bandit is an aid for spotting common mistakes, not a guarantee of secure code.
In particular this tool can't check for issues that are only be detectable when running code.

### Editorconfig

For consistency, it's strongly recommended to configure your IDE or other editor to use the
[EditorConfig](https://editorconfig.org/) settings defined in [`.editorconfig`](./.editorconfig).

## Testing

Basic end-to-end tests are performed automatically in [Continuous Integration](#continuous-integration) to check the
[Test Network](#test-network) can be processed via the Network Utility using the 
[`tests/create_outputs.py`](tests/create_outputs.py).

```
$ poetry run python ./tests/create_outputs.py ./tests/resources/test-network/test-network.gpx ./tests/out
```

Test outputs are compared against known good reference files in 
[`tests/resources/test-network/reference-outputs/`](tests/resources/test-network/reference-outputs) by
comparing checksums on file contents using the [`tests/compare_outputs.py`](tests/compare_outputs.py) script.

```
$ poetry run python ./tests/compare_outputs.py ./tests/out
```

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

1. update the `meta.version` property in `test-network.json` to the current date
1. if schema has changed, make adjustments to `create_derived_test_outputs.py`
1. recreate derived versions of the network as needed (for example the GPX derived output) [1]
1. use the network utility to generate sample exports [2]
1. manually verify the QGIS project for visualising the network is correct and update/fix as needed
1. update `reference_date` variable `compare_outputs.py` to reflect `meta.version` property in `test-network.json`

[1]

```
$ poetry run python tests/resources/test-network/create_derived_test_outputs.py
```

[2]

```
$ poetry run python tests/create_outputs.py tests/resources/test-network/test-network.gpx tests/resources/test-network/reference-outputs/
```

### Continuous Integration

All commits will trigger a Continuous Integration process using GitLab's CI/CD platform, configured in `.gitlab-ci.yml`.

## Available releases

See [README](./README.md#releases).

### Release workflow

Create a [release issue](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset/-/issues/new?issue[title]=x.x.x%20release&issuable_template=release)
and follow the instructions.

GitLab CI/CD will automatically create a GitLab Release based on the tag, including:

- milestone link
- change log extract
- package artefact
- link to README at the relevant tag

GitLab CI/CD will automatically trigger a [Deployment](#deployment) of the new release.

## Deployment

### Python package

The Air Unit Network utility is distributed as a Python package installed through Pip from the
[PyPi](https://pypi.org/project/bas-air-unit-network-dataset/) registry.

### Deployment workflow

[Continuous Deployment](#continuous-deployment) will:

- build this package using Poetry
- upload it to [PyPi](https://pypi.org/project/flask-entra-auth/)

The package can also be built manually if needed:

```
$ poetry build
```

To publish the Python package to PyPi manually:

```
$ poetry publish --username british-antarctic-survey
```

**Note:** You will need an API token for the BAS PyPi account set as `POETRY_PYPI_TOKEN_PYPI`.

### Continuous Deployment

Tagged commits created for [Releases](./README.md#releases) will trigger Continuous Deployment using GitLab's
CI/CD platform configured in [`.gitlab-ci.yml`](./.gitlab-ci.yml).
