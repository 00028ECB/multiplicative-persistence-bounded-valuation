"""Small exact-integer utilities used by the verification code."""

from __future__ import annotations


def valuation(value: int, prime: int) -> int:
    """Return the exponent of ``prime`` dividing positive ``value``."""
    if value <= 0:
        raise ValueError("value must be positive")
    if prime < 2:
        raise ValueError("prime must be at least 2")

    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent
