# Reproducibility guide

The curated snapshot is intended to be verifiable from a fresh clone without access to the private research lab..

## Python verification

Requirements: Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
ruff check .
```

The Python suite cross-checks the reference combinatorial implementation against an independently structured suffix-tree backend. It also verifies committed certificates and rejects altered fields, witnesses, and hashes.

## Standalone certificate checking

```bash
python -m mp_lab.certificate_checker certificates/2-2-2-2-7.json
python -m mp_lab.certificate_checker certificates/2-2-4-7.json
python -m mp_lab.certificate_checker certificates/4-4-7.json
python -m mp_lab.certificate_checker certificates/2-7-8.json
```

The checker does not import either search backend. It independently enumerates the claimed empty suffix level, preceding nonempty level, every shorter exact-family number, valuations, counts, and complete candidate-set digests.

## Rust verification

Requirements: stable Rust with rustfmt and Clippy.

```bash
cargo fmt --manifest-path rust-verifier/Cargo.toml -- --check
cargo clippy --manifest-path rust-verifier/Cargo.toml -- -D warnings
cargo run --release --manifest-path rust-verifier/Cargo.toml -- certificates/*.json
```

The Rust verifier shares no implementation code with Python and uses checked `u128` arithmetic.

## Building the paper

A standard TeX Live installation with `pdflatex` is sufficient:

```bash
cd paper
pdflatex bounded-valuation-note.tex
pdflatex bounded-valuation-note.tex
cd ..
```

LaTeX intermediate files and generated PDFs should not be committed to source control. A versioned PDF may be attached to a GitHub release or deposited with the preprint.

## Expected canonical results

| Certificate | Maximum valuation | Witness |
|---|---:|---:|
| `2-2-2-2-7.json` | 13 | `172122112` |
| `2-2-4-7.json` | 15 | `211111411712` |
| `4-4-7.json` | 7 | `111744` |
| `2-7-8.json` | 9 | `1178112` |

## Scope

These computations certify finite examples. They are not used in the proof of the general bounded-valuation theorem.
