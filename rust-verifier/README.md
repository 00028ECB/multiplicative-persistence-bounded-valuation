# Independent Rust certificate verifier

This binary independently checks version-1 fixed-digit valuation certificates.
It shares no search code with the Python generator or checker.

## Run

```bash
cargo run --release --manifest-path rust-verifier/Cargo.toml -- \
  certificates/2-2-2-2-7.json \
  certificates/2-2-4-7.json \
  certificates/4-4-7.json \
  certificates/2-7-8.json
```

For each certificate it recomputes:

- the canonical outer SHA-256 digest;
- every allowed number at the claimed first empty suffix level;
- every allowed number at the preceding suffix level;
- every shorter exact-family number and its valuation;
- the exact maximum and maximizing-witness membership;
- candidate counts and complete candidate-set SHA-256 digests.

The implementation uses checked `u128` arithmetic and currently accepts
certificates with decimal cutoff at most 18. That covers the canonical cases
in this repository while keeping overflow behavior explicit.
