"""Standalone verifier for version-1 valuation certificates.

This module intentionally does not import ``bounded_digits`` or
``tree_backend``. It re-enumerates the relevant finite sets directly.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

SCHEMA = "mp-lab.fixed-digit-valuation.v1"


class CertificateError(ValueError):
    """Raised when a certificate is malformed or mathematically false."""


def _canonical_json(data: object) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def _sha256_lines(lines: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for line in lines:
        digest.update(line.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _valuation(n: int, prime: int) -> int:
    if n <= 0:
        raise CertificateError("witnesses must be positive")
    exponent = 0
    while n % prime == 0:
        n //= prime
        exponent += 1
    return exponent


def _normalize_limits(raw: object) -> tuple[tuple[int, int], ...]:
    if not isinstance(raw, list):
        raise CertificateError("digit_limits must be a list")
    normalized: list[tuple[int, int]] = []
    seen: set[int] = set()
    for item in raw:
        if not isinstance(item, list) or len(item) != 2:
            raise CertificateError("each digit limit must be [digit, count]")
        digit, count = item
        if type(digit) is not int or type(count) is not int:
            raise CertificateError("digit limits must be integers")
        if digit in seen or not 2 <= digit <= 9 or count <= 0:
            raise CertificateError("invalid or duplicate digit limit")
        seen.add(digit)
        normalized.append((digit, count))
    return tuple(sorted(normalized))


def _allowed_suffixes(
    length: int,
    limits: tuple[tuple[int, int], ...],
    *,
    base: int,
) -> list[int]:
    repunit = (base**length - 1) // (base - 1)
    positions = tuple(range(length))
    values: set[int] = set()

    def recurse(index: int, remaining: tuple[int, ...], value: int) -> None:
        if index == len(limits):
            values.add(value)
            return
        digit, limit = limits[index]
        for count in range(limit + 1):
            for selected in itertools.combinations(remaining, count):
                chosen = set(selected)
                next_remaining = tuple(p for p in remaining if p not in chosen)
                addition = sum((digit - 1) * (base**p) for p in selected)
                recurse(index + 1, next_remaining, value + addition)

    recurse(0, positions, repunit)
    return sorted(values)


def _exact_family_numbers(
    limits: tuple[tuple[int, int], ...],
    *,
    cutoff: int,
    base: int,
) -> list[int]:
    exact_count = sum(count for _, count in limits)
    values: list[int] = []
    for length in range(max(1, exact_count), cutoff):
        repunit = (base**length - 1) // (base - 1)
        positions = tuple(range(length))

        def recurse(index: int, remaining: tuple[int, ...], value: int) -> None:
            if index == len(limits):
                values.append(value)
                return
            digit, count = limits[index]
            for selected in itertools.combinations(remaining, count):
                chosen = set(selected)
                next_remaining = tuple(p for p in remaining if p not in chosen)
                addition = sum((digit - 1) * (base**p) for p in selected)
                recurse(index + 1, next_remaining, value + addition)

        recurse(0, positions, repunit)
    return sorted(values)


def verify_certificate(certificate: dict[str, object]) -> dict[str, object]:
    """Verify syntax, checksums, witnesses, emptiness, and exact maximum."""
    if certificate.get("schema") != SCHEMA:
        raise CertificateError("unsupported certificate schema")
    base = certificate.get("base")
    prime = certificate.get("prime")
    if base != 10 or prime not in (2, 5):
        raise CertificateError("version 1 supports base 10 and prime 2 or 5")

    supplied_hash = certificate.get("certificate_sha256")
    unsigned = dict(certificate)
    unsigned.pop("certificate_sha256", None)
    expected_hash = hashlib.sha256(_canonical_json(unsigned)).hexdigest()
    if supplied_hash != expected_hash:
        raise CertificateError("certificate_sha256 mismatch")

    limits = _normalize_limits(certificate.get("digit_limits"))
    cutoff = certificate.get("first_empty_suffix_level")
    if type(cutoff) is not int or cutoff < 1:
        raise CertificateError("invalid first_empty_suffix_level")

    empty_level = _allowed_suffixes(cutoff, limits, base=base)
    divisible_empty = [n for n in empty_level if n % (prime**cutoff) == 0]
    if divisible_empty:
        raise CertificateError("claimed empty suffix level is not empty")

    if cutoff > 1:
        prior_level = _allowed_suffixes(cutoff - 1, limits, base=base)
        prior_divisible = [n for n in prior_level if n % (prime ** (cutoff - 1)) == 0]
        if not prior_divisible:
            raise CertificateError("claimed empty level is not the first")
        if certificate.get("prior_level_witness") not in prior_divisible:
            raise CertificateError("prior-level witness is invalid")
    elif certificate.get("prior_level_witness") is not None:
        raise CertificateError("level 1 certificate must have null prior witness")

    short_values = _exact_family_numbers(limits, cutoff=cutoff, base=base)
    short_pairs = [(value, _valuation(value, prime)) for value in short_values]
    short_best = max(short_pairs, key=lambda pair: (pair[1], -pair[0]), default=(1, 0))

    long_bound = cutoff - 1
    claimed_max = certificate.get("maximum_valuation")
    witness = certificate.get("maximizing_witness")
    if type(claimed_max) is not int or type(witness) is not int:
        raise CertificateError("invalid maximum or witness")
    if _valuation(witness, prime) != claimed_max:
        raise CertificateError("maximizing witness has wrong valuation")

    witness_digits = Counter(int(ch) for ch in str(witness) if ch != "1")
    required = Counter(dict(limits))
    if witness_digits != required or "0" in str(witness):
        raise CertificateError("maximizing witness is outside the exact family")

    actual_max = max(short_best[1], long_bound)
    if claimed_max != actual_max:
        raise CertificateError(
            f"claimed maximum {claimed_max} differs from verified {actual_max}"
        )

    counts = certificate.get("counts")
    digests = certificate.get("digests")
    if not isinstance(counts, dict) or not isinstance(digests, dict):
        raise CertificateError("missing counts or digests")

    empty_digest = _sha256_lines(str(value) for value in empty_level)
    short_digest = _sha256_lines(
        f"{value}:{exponent}" for value, exponent in short_pairs
    )
    if counts.get("empty_level_candidates") != len(empty_level):
        raise CertificateError("empty-level candidate count mismatch")
    if counts.get("short_exact_family_candidates") != len(short_values):
        raise CertificateError("short-family candidate count mismatch")
    if digests.get("empty_level_candidates_sha256") != empty_digest:
        raise CertificateError("empty-level digest mismatch")
    if digests.get("short_exact_family_sha256") != short_digest:
        raise CertificateError("short-family digest mismatch")

    return {
        "valid": True,
        "maximum_valuation": actual_max,
        "maximizing_witness": witness,
        "first_empty_suffix_level": cutoff,
        "empty_level_candidates": len(empty_level),
        "short_exact_family_candidates": len(short_values),
    }


def verify_file(path: str | Path) -> dict[str, object]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CertificateError("certificate root must be an object")
    return verify_certificate(data)


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m mp_lab.certificate_checker")
    parser.add_argument("certificate")
    args = parser.parse_args()
    result = verify_file(args.certificate)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
