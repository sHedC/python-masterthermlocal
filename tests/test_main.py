"""Test the Main command."""

from masterthermconnect.__main__ import main as MasterthermConnect


def test_help(capsys) -> None:
    """Test the Main Help."""
    MasterthermConnect(["--help"])

    out, err = capsys.readouterr()
    assert out.startswith("usage: masterthermconnect [-h] [--version]")
    assert err == ""
