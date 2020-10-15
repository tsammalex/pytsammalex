import pytest


@pytest.mark.bare
def test_import():
    from pytsammalex import clld
    from pytsammalex import lexibank
    assert clld and lexibank