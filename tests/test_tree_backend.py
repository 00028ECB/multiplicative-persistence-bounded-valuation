from __future__ import annotations

from collections import Counter

import pytest

from mp_lab.bounded_digits import find_divisible_suffix
from mp_lab.tree_backend import find_divisible_suffix_tree, first_empty_tree_level


@pytest.mark.parametrize(
    ("digits", "max_length"),
    [
        ((4, 4, 7), 9),
        ((2, 7, 8), 10),
        ((2, 2, 4, 7), 12),
        ((2, 3), 7),
        ((6,), 6),
        ((8, 9), 7),
    ],
)
def test_tree_backend_matches_reference_existence(
    digits: tuple[int, ...],
    max_length: int,
) -> None:
    limits = dict(Counter(digits))
    for length in range(1, max_length + 1):
        reference = find_divisible_suffix(length, limits)
        independent = find_divisible_suffix_tree(length, limits)
        assert (reference.witness is None) == (independent.witness is None)
        if independent.witness is not None:
            assert independent.witness % (2**length) == 0
            decimal = str(independent.witness)
            assert len(decimal) == length
            assert "0" not in decimal
            observed = Counter(int(digit) for digit in decimal if digit != "1")
            assert all(observed[digit] <= count for digit, count in limits.items())


def test_corrected_table4_cutoffs() -> None:
    # These are first empty B_e suffix levels, not exact maxima plus one.
    expected = {
        (2, 2, 2, 2, 7): 10,
        (2, 2, 4, 7): 13,
        (4, 4, 7): 7,
        (2, 7, 8): 8,
    }
    for digits, cutoff in expected.items():
        result = first_empty_tree_level(dict(Counter(digits)))
        assert result.length == cutoff


def test_invalid_prime_is_rejected() -> None:
    with pytest.raises(ValueError):
        find_divisible_suffix_tree(3, {4: 1}, prime=3)
