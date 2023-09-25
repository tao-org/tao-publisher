"""Basic package test."""


def test_package_import():
    import tao  # noqa


def test_package_version_is_defined():
    import tao

    assert tao.__version__ != "undefined"
