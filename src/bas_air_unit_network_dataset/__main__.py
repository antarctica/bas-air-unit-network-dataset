from importlib.metadata import version
from pathlib import Path

import click

from bas_air_unit_network_dataset import NetworkManager


class AppCommand(click.core.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.insert(
            0,
            click.core.Option(
                (
                    "-d",
                    "--dataset-path",
                ),
                help="Path to network dataset",
                required=True,
                envvar="AIRNET_DATASET_PATH",
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
            ),
        )


def inspect_network(network: NetworkManager) -> None:
    click.echo(network)
    click.echo("")

    click.echo(f"Waypoints [{len(network.waypoints)}]:")
    for i, waypoint in enumerate(network.waypoints):
        click.echo(f"{str(i + 1).zfill(2)}. {waypoint}")
    click.echo("")

    click.echo(f"Routes [{len(network.routes)}]:")
    for i, route in enumerate(network.routes):
        click.echo(f"{str(i + 1).zfill(2)}. {route}")


@click.group()
@click.version_option(version("bas_air_unit_network_dataset"))
def cli():
    """BAS Air Unit Network Dataset (`airnet`)"""
    pass


@cli.command()
@click.option(
    "-d",
    "--dataset-path",
    help="Path to network dataset directory",
    required=True,
    envvar="AIRNET_DATASET_PATH",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True),
)
def init(dataset_path: str) -> None:
    """Initialises an empty network"""
    _dataset_path = Path(dataset_path).joinpath("bas-air-unit-network-dataset.gpkg")
    click.echo(f"Dataset will be located at: {_dataset_path}")
    click.echo("")

    network = NetworkManager(dataset_path=_dataset_path, init=True)
    click.echo(f"Dataset created at: {network.dataset_path.absolute()}")


@cli.command(cls=AppCommand, name="import")
@click.option(
    "-i",
    "--input-path",
    help="Path to input file containing routes and waypoints",
    required=True,
    envvar="AIRNET_INPUT_PATH",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
)
def _import(dataset_path: str, input_path: str) -> None:
    """Import routes and waypoints into network from an input file"""
    _dataset_path = Path(dataset_path)
    _input_path = Path(input_path)
    click.echo(f"Dataset is located at: {_dataset_path}")
    click.echo(f"Input is located at: {_input_path}")
    click.echo("")

    # `init` is set to reset contents of dataset
    network = NetworkManager(dataset_path=Path(dataset_path), init=True)
    network.load_gpx(path=_input_path)
    inspect_network(network=network)

    click.echo("")
    click.echo("Import complete")


@cli.command(cls=AppCommand)
@click.option(
    "-o",
    "--output-path",
    help="Path to save outputs",
    required=True,
    envvar="AIRNET_OUTPUT_PATH",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True, resolve_path=True),
)
def export(dataset_path: str, output_path: str) -> None:
    """Export network, routes, waypoints as CSV/GPX/FPL outputs"""
    _dataset_path = Path(dataset_path)
    _output_path = Path(output_path)
    click.echo(f"Dataset is located at: {_dataset_path}")
    click.echo(f"Output directory is: {_output_path}")
    click.echo("")

    network = NetworkManager(dataset_path=_dataset_path, output_path=_output_path)

    network.dump_csv()
    print("- CSV export complete")
    network.dump_gpx()
    print("- GPX export complete")
    network.dump_fpl()
    print("- FPL export complete")

    click.echo("")
    click.echo("Export complete")


@cli.command(cls=AppCommand)
def inspect(dataset_path: str) -> None:
    """Inspect state of network, routes, waypoints"""
    _dataset_path = Path(dataset_path)
    click.echo(f"Dataset is located at: {_dataset_path}")
    click.echo("")

    network = NetworkManager(dataset_path=Path(dataset_path))
    inspect_network(network=network)


if __name__ == "__main__":
    cli()
