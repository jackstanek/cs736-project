from plot.miss_rate_curve import MissRateCurve, MissRatePoint, CacheStat

import pytest


_parsing_test_cases = [
    (
        "65536 79889888 19.3% (5973/30974)",
        MissRatePoint(65536, 79889888, CacheStat(5973, 25001)),
    ),
    (
        "131072 154146720 20.2% (6253/30974)",
        MissRatePoint(131072, 154146720, CacheStat(6253, 24721)),
    ),
]


@pytest.mark.parametrize("test_input,expected", _parsing_test_cases)
def test_parsing_miss_rate_point(test_input, expected):
    """Test parsing miss rate point"""
    assert MissRatePoint.parse_miss_rate_point(test_input) == expected


def test_parsing_curve():
    """Test parsing a miss rate curve"""
    strs, expected = zip(*_parsing_test_cases)
    assert MissRateCurve.parse_miss_rate_curve(strs) == MissRateCurve(list(expected))
