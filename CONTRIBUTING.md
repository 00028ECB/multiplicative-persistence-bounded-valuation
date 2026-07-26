# Contributing

This project concerns an exact mathematical claim. Contributions should prioritize correctness, reproducibility, and clear separation between theorem, conjecture, computation, and speculation.

## Mathematical comments

For a possible flaw, state the exact theorem hypothesis or proof step involved and provide a concrete counterexample or derivation where possible. Questions about novelty should include a precise citation or search lead.

## Software changes

- Preserve integer-exact arithmetic.
- Add or update tests with every behavior change.
- Keep independent verification implementations logically separate.
- Do not weaken certificate validation for convenience.
- Record finite search bounds and deterministic workload information.

Before opening a pull request, run:

```bash
pytest
ruff check .
cargo fmt --manifest-path rust-verifier/Cargo.toml -- --check
cargo clippy --manifest-path rust-verifier/Cargo.toml -- -D warnings
```

## Research conduct

Do not describe the result as peer reviewed unless and until that occurs. Do not claim that this theorem proves decimal multiplicative persistence is at most 11. Security issues or accidentally exposed private information should be reported privately rather than filed in a public issue.