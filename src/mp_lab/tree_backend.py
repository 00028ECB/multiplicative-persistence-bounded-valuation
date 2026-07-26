"""Independent suffix-tree backend for fixed digit-multiset searches.

This implementation deliberately does not enumerate digit positions by
combinations. It grows valid least-significant suffixes one digit at a time and
prunes a suffix immediately unless its first k digits form a number divisible
by p**k.

For a final length-e candidate divisible by p**e, every shorter suffix must
satisfy the corresponding divisibility condition because p divides the base.
Thus the pruning is exact.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .bounded_digits import normalize_limits


@dataclass(frozen=True)
class TreeLevelResult:
    length: int
    modulus: int
    witness: int | None
    used_counts: tuple[tuple[int, int], ...] | None
    states_examined: int
    states_surviving: int


def _validate_parameters(*, prime: int, base: int) -> None:
    if base != 10:
        raise ValueError("the current digit representation supports base 10 only")
    if prime not in (2, 5):
        raise ValueError("prime must divide base 10; supported values are 2 and 5")


def find_divisible_suffix_tree(
    length: int,
    digit_limits: Mapping[int, int],
    *,
    prime: int = 2,
    base: int = 10,
) -> TreeLevelResult:
    """Find a valid length-``length`` suffix using recursive divisibility.

    A state is ``(value, count_vector)`` for the suffix already built from the
    least significant digit upward. All surviving level-k states are divisible
    by ``prime**k``.
    """
    if length < 1:
        raise ValueError("length must be positive")
    _validate_parameters(prime=prime, base=base)
    normalized = normalize_limits(digit_limits)
    digits = tuple(digit for digit, _ in normalized)
    limits = tuple(limit for _, limit in normalized)

    states: dict[int, tuple[int, ...]] = {0: (0,) * len(normalized)}
    examined = 0

    for position in range(length):
        modulus = prime ** (position + 1)
        place = base**position
        next_states: dict[int, tuple[int, ...]] = {}

        for value, counts in states.items():
            examined += 1
            candidate = value + place
            if candidate % modulus == 0:
                next_states[candidate] = counts

            for index, digit in enumerate(digits):
                if counts[index] >= limits[index]:
                    continue
                examined += 1
                candidate = value + digit * place
                if candidate % modulus != 0:
                    continue
                updated = list(counts)
                updated[index] += 1
                next_states[candidate] = tuple(updated)

        states = next_states
        if not states:
            return TreeLevelResult(
                length=length,
                modulus=prime**length,
                witness=None,
                used_counts=None,
                states_examined=examined,
                states_surviving=0,
            )

    witness = min(states)
    counts = states[witness]
    used_counts = tuple(
        (digit, count)
        for digit, count in zip(digits, counts, strict=True)
        if count
    )
    return TreeLevelResult(
        length=length,
        modulus=prime**length,
        witness=witness,
        used_counts=used_counts,
        states_examined=examined,
        states_surviving=len(states),
    )


def first_empty_tree_level(
    digit_limits: Mapping[int, int],
    *,
    prime: int = 2,
    base: int = 10,
    max_length: int | None = None,
) -> TreeLevelResult:
    """Return the first length with no divisible allowed suffix."""
    length = 1
    while True:
        if max_length is not None and length > max_length:
            raise RuntimeError(f"no empty tree level found through length {max_length}")
        result = find_divisible_suffix_tree(
            length,
            digit_limits,
            prime=prime,
            base=base,
        )
        if result.witness is None:
            return result
        length += 1
