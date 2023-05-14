import pytest
from doubleblind.utils import *

@pytest.mark.parametrize('version,expected', [('3.0.0', [3, 0, 0]), ('0.1.3', [0, 1, 3]), ('2.0.5', [2, 0, 5])])
def test_parse_version(version, expected):
    assert parse_version(version) == expected