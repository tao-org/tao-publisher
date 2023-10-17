"""CLI test."""

from importlib.metadata import metadata

from click.testing import CliRunner
from tao._cli import main

runner = CliRunner()


def test_cli():
    """Running CLI without argument print help."""
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert result.stdout.startswith("Usage:")


def test_cli_version():
    """Running CLI with arg "version" print package name and version number."""
    m = metadata("tao")
    pkg_name = m["Name"]
    pkg_version = m["version"]
    pkg_summary = m["Summary"]

    result = runner.invoke(main, ["version"])

    assert result.exit_code == 0
    assert pkg_name in result.stdout
    assert pkg_version in result.stdout
    assert pkg_summary in result.stdout
