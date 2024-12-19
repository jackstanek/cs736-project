import pytest

from plot.sample import rejection_sample


def test_rejection_sampling_only_selects_good():
    """Test that rejection sampling only selects matching elements"""
    test_cases = list(range(100))
    n = 25
    choices = rejection_sample(test_cases, lambda x: not bool(x % 2), n)
    assert all(c % 2 == 0 for c in choices)


def test_rejection_sampling_selects_correct_number():
    test_cases = list(range(100))
    n = 25
    choices = rejection_sample(test_cases, lambda x: x < 50, n)
    assert len(choices) == n
