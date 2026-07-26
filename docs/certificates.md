# Machine-checkable valuation certificates

Phase 2 introduces a versioned JSON certificate for exact \(p\)-adic valuation
bounds in fixed decimal digit-multiset families.

## Threat model

The checker does not trust:

- the reference combinatorial search;
- the suffix-tree search;
- the reported witness;
- the reported first empty level;
- the candidate counts;
- the candidate-set digests;
- the outer certificate digest.

It independently enumerates:

1. every allowed suffix at the claimed first empty level;
2. every allowed suffix at the preceding level;
3. every shorter exact-family number;
4. all relevant valuations.

The checker imports neither existing search backend.

## Generate

```bash
python -m mp_lab.certificates \
  --digits 4,4,7 \
  --output certificates/4-4-7.json
```

## Verify

```bash
python -m mp_lab.certificate_checker certificates/4-4-7.json
```

## Version 1 fields

- `schema`
- `base`
- `prime`
- `digit_limits`
- `first_empty_suffix_level`
- `prior_level_witness`
- `maximum_valuation`
- `maximizing_witness`
- deterministic candidate counts
- SHA-256 digests of the complete finite candidate sets
- SHA-256 digest of the unsigned certificate

The current format supports decimal digits and primes 2 or 5.
