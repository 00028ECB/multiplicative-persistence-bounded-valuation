"""Versioned JSON certificates for exact fixed-digit valuation bounds.

The generator may use the reference search implementation. Verification is
performed by :mod:`mp_lab.certificate_checker`, which deliberately has no
dependency on either search backend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Iterable, Mapping
from pathlib import Path

from .bounded_digits import (
    compute_exact_valuation_bound,
    find_divisible_suffix,
    iter_exact_family_numbers,
    limits_from_digits,
)
from .core import valuation

SCHEMA = "mp-lab.fixed-digit-valuation.v1"


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


def _suffix_level_digest(
    length: int,
    digit_limits: Mapping[int, int],
    *,
    prime: int,
    base: int,
) -> tuple[str, int]:
    """Hash every allowed suffix at one level in ascending numeric order."""
    normalized = tuple(sorted((int(d), int(c)) for d, c in digit_limits.items() if c))
    candidates: list[int] = []
    repunit = (base**length - 1) // (base - 1)

    def recurse(index: int, remaining: tuple[int, ...], value: int) -> None:
        if index == len(normalized):
            candidates.append(value)
            return
        digit, limit = normalized[index]
        for count in range(limit + 1):
            for selected in __import__("itertools").combinations(remaining, count):
                selected_set = set(selected)
                next_remaining = tuple(p for p in remaining if p not in selected_set)
                addition = sum((digit - 1) * (base**p) for p in selected)
                recurse(index + 1, next_remaining, value + addition)

    recurse(0, tuple(range(length)), repunit)
    candidates = sorted(set(candidates))
    return _sha256_lines(str(value) for value in candidates), len(candidates)


def _short_family_digest(
    digit_limits: Mapping[int, int],
    *,
    cutoff: int,
    prime: int,
    base: int,
) -> tuple[str, int]:
    values = sorted(
        iter_exact_family_numbers(
            digit_limits,
            max_length_exclusive=cutoff,
            base=base,
        )
    )
    lines = (f"{value}:{valuation(value, prime)}" for value in values)
    return _sha256_lines(lines), len(values)


def generate_certificate(
    digit_limits: Mapping[int, int],
    *,
    prime: int = 2,
    base: int = 10,
) -> dict[str, object]:
    """Generate a complete version-1 certificate."""
    result = compute_exact_valuation_bound(
        digit_limits,
        prime=prime,
        base=base,
    )
    cutoff = result.suffix_cutoff

    suffix_digest, suffix_count = _suffix_level_digest(
        cutoff,
        digit_limits,
        prime=prime,
        base=base,
    )
    short_digest, short_count = _short_family_digest(
        digit_limits,
        cutoff=cutoff,
        prime=prime,
        base=base,
    )

    prior = find_divisible_suffix(
        cutoff - 1,
        digit_limits,
        prime=prime,
        base=base,
    ) if cutoff > 1 else None

    witness = result.witness
    required_digits = sorted(
        digit
        for digit, count in result.digit_limits
        for _ in range(count)
    )
    observed_digits = sorted(
        int(character)
        for character in str(witness)
        if character != "1"
    )
    if "0" in str(witness) or observed_digits != required_digits:
        # The reference bound routine historically used repunit(...) when the
        # first empty suffix level was 1. The bound was correct, but the
        # returned witness could lie outside a nonempty exact family. At
        # cutoff 1 every allowed units digit is coprime to ``prime``, so the
        # canonical no-1 arrangement is a valid valuation-zero witness.
        if not required_digits:
            witness = 1
        else:
            witness = int("".join(str(digit) for digit in required_digits))
        if valuation(witness, prime) != result.maximum_valuation:
            raise AssertionError("failed to construct an exact-family witness")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "base": base,
        "prime": prime,
        "digit_limits": [[d, c] for d, c in result.digit_limits],
        "first_empty_suffix_level": cutoff,
        "prior_level_witness": None if prior is None else prior.witness,
        "maximum_valuation": result.maximum_valuation,
        "maximizing_witness": witness,
        "counts": {
            "empty_level_candidates": suffix_count,
            "short_exact_family_candidates": short_count,
        },
        "digests": {
            "empty_level_candidates_sha256": suffix_digest,
            "short_exact_family_sha256": short_digest,
        },
        "generator": {
            "name": "mp-lab Python reference generator",
            "version": 1,
        },
    }
    payload["certificate_sha256"] = hashlib.sha256(_canonical_json(payload)).hexdigest()
    return payload


def write_certificate(
    path: str | Path,
    digit_limits: Mapping[int, int],
    *,
    prime: int = 2,
    base: int = 10,
) -> dict[str, object]:
    certificate = generate_certificate(digit_limits, prime=prime, base=base)
    Path(path).write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return certificate


def _parse_digits(raw: str) -> dict[int, int]:
    digits = [int(part.strip()) for part in raw.split(",") if part.strip()]
    return limits_from_digits(digits)


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m mp_lab.certificates")
    parser.add_argument("--digits", required=True, help="comma-separated fixed digits")
    parser.add_argument("--output", required=True)
    parser.add_argument("--prime", type=int, default=2)
    args = parser.parse_args()
    certificate = write_certificate(
        args.output,
        _parse_digits(args.digits),
        prime=args.prime,
    )
    print(json.dumps(certificate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
