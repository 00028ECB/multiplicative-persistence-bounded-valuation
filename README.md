# Bounded valuation in fixed digit-multiset families

This repository accompanies a short note proving a bounded-valuation theorem for integers with a fixed multiset of non-1 digits and arbitrarily many additional 1s.

## Main theorem

Fix a base `b >= 2`, a prime `p` dividing `b`, and a finite multiset of digits from `2` through `b - 1`. Consider positive base-`b` integers containing exactly those non-1 digits, no zero digits, and any number of additional digits equal to `1`. Then their `p`-adic valuations are bounded.

For b = 2, the set of digits from 2 through b - 1 is empty, so the fixed multiset is necessarily empty. The family therefore consists only of binary repunits, all of which are odd. The substantive argument treats b >= 3.

For `b = 10` and `p = 2`, this proves Conjecture 2 posed by Brier, Clavier, Gutsche, and Naccache in *The Multiplicative Persistence Conjecture Is True for Odd Targets* (2021).

The proof is qualitative and does **not** prove that decimal multiplicative persistence is at most 11.

## Status

The argument has undergone repeated internal adversarial review and has been sent privately to the authors of the 2021 paper for comment. It has not yet been peer reviewed. A targeted literature search has not located an earlier proof, but novelty has not been independently confirmed.

## Contents

- `paper/bounded-valuation-note.tex` — reviewed theorem note;
- `src/mp_lab/` — Python reference search and independent checker;
- `certificates/` — versioned exact finite certificates;
- `rust-verifier/` — standalone Rust certificate verifier;
- `tests/` — Python cross-check and tamper tests;
- `docs/` — proof audit, certificate format, and novelty audit.

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

The computations support these finite examples. The theorem itself does not depend on computation.

## Reproducibility and citation

See `REPRODUCIBILITY.md`, `CITATION.cff`, and `AI_USE.md` in the curated release.

## Licensing

The software is released under the MIT License. The manuscript and research prose remain copyright Jason Stewart; see `LICENSE-PAPER` for permitted use.
