"""Reference enumeration for fixed non-1 digit-multiset families.

The implementation is intentionally direct and exact. It is used to generate
finite certificates; the standalone Python and Rust checkers independently
re-enumerate the relevant sets.
"""

from __future__ import annotations

import itertools
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .core import valuation


@dataclass(frozen=True)
class SuffixSearchResult:
    length: int
    modulus: int
    witness: int | None
    candidates_examined: int


@dataclass(frozen=True)
class ExactValuationBound:
    digit_limits: tuple[tuple[int, int], ...]
    prime: int
    base: int
    suffix_cutoff: int
    maximum_valuation: int
    witness: int


def normalize_limits(digit_limits: Mapping[int, int]) -> tuple[tuple[int, int], ...]:
    normalized: list[tuple[int, int]] = []
    for raw_digit, raw_count in digit_limits.items():
        digit = int(raw_digit)
        count = int(raw_count)
        if not 2 <= digit <= 9:
            raise ValueError("fixed digits must lie between 2 and 9")
        if count < 0:
            raise ValueError("digit counts must be nonnegative")
        if count:
            normalized.append((digit, count))
    normalized.sort()
    return tuple(normalized)


def limits_from_digits(digits: Iterable[int]) -> dict[int, int]:
    return dict(Counter(int(digit) for digit in digits))


def _validate_parameters(*, prime: int, base: int) -> None:
    if base != 10:
        raise ValueError("the reference enumerator currently supports base 10")
    if prime not in (2, 5):
        raise ValueError("prime must divide base 10; supported values are 2 and 5")


def _numbers_of_length(
    length: int,
    digit_limits: Mapping[int, int],
    *,
    exact: bool,
    base: int,
) -> list[int]:
    if length < 1:
        return []
    normalized = normalize_limits(digit_limits)
    required = sum(count for _, count in normalized)
    if exact and required > length:
        return []

    positions = tuple(range(length))
    repunit = (base**length - 1) // (base - 1)
    values: set[int] = set()

    def recurse(index: int, remaining: tuple[int, ...], value: int) -> None:
        if index == len(normalized):
            values.add(value)
            return

        digit, limit = normalized[index]
        counts = (limit,) if exact else range(min(limit, len(remaining)) + 1)
        for count in counts:
            if count > len(remaining):
                continue
            for selected in itertools.combinations(remaining, count):
                chosen = set(selected)
                next_remaining = tuple(
                    position for position in remaining if position not in chosen
                )
                addition = sum(
                    (digit - 1) * (base**position) for position in selected
                )
                recurse(index + 1, next_remaining, value + addition)

    recurse(0, positions, repunit)
    return sorted(values)


def find_divisible_suffix(
    length: int,
    digit_limits: Mapping[int, int],
    *,
    prime: int = 2,
    base: int = 10,
) -> SuffixSearchResult:
    """Find the smallest allowed length-``length`` suffix divisible by ``p^length``."""
    if length < 1:
        raise ValueError("length must be positive")
    _validate_parameters(prime=prime, base=base)
    candidates = _numbers_of_length(length, digit_limits, exact=False, base=base)
    modulus = prime**length
    witness = next((value for value in candidates if value % modulus == 0), None)
    return SuffixSearchResult(
        length=length,
        modulus=modulus,
        witness=witness,
        candidates_examined=len(candidates),
    )


def iter_exact_family_numbers(
    digit_limits: Mapping[int, int],
    *,
    max_length_exclusive: int,
    base: int = 10,
):
    """Yield every exact-family number shorter than ``max_length_exclusive``."""
    _validate_parameters(prime=2, base=base)
    minimum_length = max(1, sum(count for _, count in normalize_limits(digit_limits)))
    for length in range(minimum_length, max_length_exclusive):
        yield from _numbers_of_length(length, digit_limits, exact=True, base=base)


def first_empty_suffix_level(
    digit_limits: Mapping[int, int],
    *,
    prime: int = 2,
    base: int = 10,
    max_length: int | None = None,
) -> SuffixSearchResult:
    length = 1
    while True:
        if max_length is not None and length > max_length:
            raise RuntimeError(f"no empty suffix level found through {max_length}")
        result = find_divisible_suffix(
            length,
            digit_limits,
            prime=prime,
            base=base,
        )
        if result.witness is None:
            return result
        length += 1


def compute_exact_valuation_bound(
    digit_limits: Mapping[int, int],
    *,
    prime: int = 2,
    base: int = 10,
) -> ExactValuationBound:
    """Compute the exact maximum valuation using a finite suffix certificate.

    If level ``e`` is the first empty allowed-suffix level, every family member
    of length at least ``e`` has valuation at most ``e-1``. All shorter exact
    family members are enumerated separately.
    """
    _validate_parameters(prime=prime, base=base)
    normalized = normalize_limits(digit_limits)
    cutoff = first_empty_suffix_level(
        digit_limits,
        prime=prime,
        base=base,
    ).length

    short_values = list(
        iter_exact_family_numbers(
            digit_limits,
            max_length_exclusive=cutoff,
            base=base,
        )
    )
    short_pairs = [(value, valuation(value, prime)) for value in short_values]
    short_best = max(
        short_pairs,
        key=lambda pair: (pair[1], -pair[0]),
        default=(1, 0),
    )

    long_bound = cutoff - 1
    maximum = max(short_best[1], long_bound)

    if short_best[1] == maximum:
        witness = short_best[0]
    elif cutoff > 1:
        prior = find_divisible_suffix(
            cutoff - 1,
            digit_limits,
            prime=prime,
            base=base,
        )
        if prior.witness is None:
            raise AssertionError("preceding suffix level unexpectedly empty")
        witness = prior.witness
    else:
        witness = 1

    return ExactValuationBound(
        digit_limits=normalized,
        prime=prime,
        base=base,
        suffix_cutoff=cutoff,
        maximum_valuation=maximum,
        witness=witness,
    )
