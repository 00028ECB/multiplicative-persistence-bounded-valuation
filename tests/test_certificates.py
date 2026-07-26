from __future__ import annotations

import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

from mp_lab.certificate_checker import CertificateError, verify_certificate
from mp_lab.certificates import generate_certificate


@pytest.mark.parametrize(
    "digits",
    [
        (2, 2, 2, 2, 7),
        (2, 2, 4, 7),
        (4, 4, 7),
        (2, 7, 8),
    ],
)
def test_generated_certificates_verify(digits: tuple[int, ...]) -> None:
    certificate = generate_certificate(dict(Counter(digits)))
    result = verify_certificate(certificate)
    assert result["valid"] is True
    assert result["maximum_valuation"] == certificate["maximum_valuation"]


def _refresh_outer_hash(certificate: dict[str, object]) -> None:
    unsigned = dict(certificate)
    unsigned.pop("certificate_sha256", None)
    encoded = json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    certificate["certificate_sha256"] = hashlib.sha256(encoded).hexdigest()


def test_tampered_witness_is_rejected_after_rehash() -> None:
    certificate = generate_certificate(dict(Counter((4, 4, 7))))
    tampered = deepcopy(certificate)
    tampered["maximizing_witness"] = 1117440
    _refresh_outer_hash(tampered)
    with pytest.raises(CertificateError):
        verify_certificate(tampered)


def test_tampered_digest_is_rejected() -> None:
    certificate = generate_certificate(dict(Counter((2, 7, 8))))
    tampered = deepcopy(certificate)
    tampered["digests"]["empty_level_candidates_sha256"] = "0" * 64
    # Refresh the outer hash so the checker reaches the mathematical digest.
    _refresh_outer_hash(tampered)

    with pytest.raises(CertificateError):
        verify_certificate(tampered)


def test_cutoff_one_family_has_exact_witness() -> None:
    certificate = generate_certificate({3: 1})
    assert certificate["first_empty_suffix_level"] == 1
    assert certificate["maximum_valuation"] == 0
    assert certificate["maximizing_witness"] == 3
    assert verify_certificate(certificate)["valid"] is True


def test_boolean_integer_fields_are_rejected() -> None:
    certificate = generate_certificate({3: 1})
    tampered = deepcopy(certificate)
    tampered["first_empty_suffix_level"] = True
    _refresh_outer_hash(tampered)
    with pytest.raises(CertificateError):
        verify_certificate(tampered)


@pytest.mark.parametrize(
    "filename",
    [
        "2-2-2-2-7.json",
        "2-2-4-7.json",
        "4-4-7.json",
        "2-7-8.json",
    ],
)
def test_committed_certificates_verify(filename: str) -> None:
    root = Path(__file__).resolve().parents[1]
    certificate = json.loads((root / "certificates" / filename).read_text())
    assert verify_certificate(certificate)["valid"] is True
