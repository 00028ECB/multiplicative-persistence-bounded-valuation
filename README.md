# Two Short Proofs of a Bounded-Valuation Theorem in Multiplicative Persistence

This repository preserves two short qualitative proofs of a bounded-valuation theorem for integers with a fixed multiset of non-1 digits and arbitrarily many additional 1s, together with reproducible finite verification developed alongside the proofs.

## Current status

For decimal base and `p = 2`, the theorem gives the qualitative boundedness assertion posed as Conjecture 2 by Brier, Clavier, Gutsche, and Naccache in *The Multiplicative Persistence Conjecture Is True for Odd Targets* (2021).

Patrick Nyadjo Fonga gives a quantitative proof of the conjecture in arXiv:2608.27802, obtaining explicit bounds and an effective finite method for the even-target persistence program. The proofs preserved here are different: a finitely branching divisible-suffix argument using König's lemma and an equivalent `p`-adic compactness argument.

The computational code and certificates in this repository are retained as reproducibility material for the finite experiments; they are not needed for the qualitative proofs.

## Main theorem

Fix a base `b >= 2`, a prime `p` dividing `b`, and a finite multiset of digits from `2` through `b - 1`. Consider positive base-`b` integers containing exactly those non-1 digits, no zero digits, and any number of additional digits equal to `1`. Then their `p`-adic valuations are bounded.

For b = 2, the set of digits from 2 through b - 1 is empty, so the fixed multiset is necessarily empty. The family therefore consists only of binary repunits, all of which are odd. The substantive argument treats b >= 3.

The theorem is qualitative. It does **not** provide the effective cutoff required by the even-target persistence search, and it does **not** prove that decimal multiplicative persistence is at most 11. Fonga's quantitative result supplies the former ingredient.

## Contents

- `paper/bounded-valuation-note.tex` — short theorem note containing the suffix-tree and `p`-adic compactness proofs;
- `src/mp_lab/` — Python reference search and independent checker;
- `certificates/` — versioned exact finite certificates;
- `rust-verifier/` — standalone Rust certificate verifier;
- `tests/` — Python cross-check and tamper tests;
- `docs/` — proof audit, certificate format, and historical novelty audit.

## Quick verification

Python 3.11 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
```

Verify one certificate independently in Python:

```bash
python -m mp_lab.certificate_checker certificates/4-4-7.json
```

Verify all canonical certificates independently in Rust:

```bash
cargo fmt --manifest-path rust-verifier/Cargo.toml -- --check
cargo clippy --manifest-path rust-verifier/Cargo.toml -- -D warnings
cargo run --release --manifest-path rust-verifier/Cargo.toml -- certificates/*.json
```

## Representative certified cases

| Fixed non-1 multiset | Exact maximum `v_2` | Witness |
|---|---:|---:|
| `2,2,2,2,7` | 13 | `172122112` |
| `2,2,4,7` | 15 | `211111411712` |
| `4,4,7` | 7 | `111744` |
| `2,7,8` | 9 | `1178112` |

These computations certify the listed finite examples. They are independent of the qualitative theorem proofs.

## Reproducibility and citation

See `REPRODUCIBILITY.md`, `CITATION.cff`, and `AI_USE.md`.

## Licensing

The software is released under the MIT License. The manuscript and research prose remain copyright Jason Stewart; see `LICENSE-PAPER` for permitted use.
