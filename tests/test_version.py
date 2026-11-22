from overfunc.version import __version__
from packaging.version import Version


def test_version():
    assert isinstance(__version__, str)
    assert Version(__version__) > Version("0.0.0")
