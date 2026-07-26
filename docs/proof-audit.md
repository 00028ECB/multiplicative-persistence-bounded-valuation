# Final adversarial proof review

**Date:** 2026-07-20 (America/Phoenix)  
**Object reviewed:** `paper/bounded-valuation-note-reviewed.tex`  
**Verdict:** no mathematical counterexample or logical gap found; several expository repairs made.

## The theorem after review

For a base `b >= 2`, a prime `p | b`, and a fixed finite multiset of base-`b` digits other than 1, consider positive integers with exactly those exceptional digits, no zero digits, and any number of additional 1s. Their `p`-adic valuations are bounded.

The base-2 case is trivial: the only allowed positive numbers are binary repunits `2^r - 1`, all odd. The substantive proof treats `b >= 3`.

## Attacks performed

### 1. Does unbounded valuation produce a suffix at every depth?

Yes. For requested depth `e`, choose

`v_p(x) >= ceil((e-1) log_p b) + 1`.

Then `x > b^(e-1)`, so it has at least `e` digits. Since `p | b`, `log_p b >= 1`, so the same threshold is at least `e`; hence `p^e | x`.

### 2. Can a suffix lose its leading digit?

No. Zero digits are excluded from the family, so the most significant digit of every extracted suffix is nonzero. It is genuinely an `e`-digit string.

### 3. Is parent closure valid when `p^2 | b` or when `b` is composite?

Yes. If `y_(e+1) = a_e b^e + y_e`, then `v_p(b^e) = e v_p(b) >= e`. Thus `p^e | a_e b^e`; divisibility of the child by `p^(e+1)` implies divisibility of the parent by `p^e`. No assumption that `v_p(b)=1` is used.

### 4. Are the hypotheses of Koenig's lemma actually present?

Yes after adjoining the empty root. Each vertex has at most `b-1` children, parent closure connects every vertex to the root, and the quantitative suffix extraction supplies a vertex at every depth.

### 5. Can non-1 digits keep appearing forever by moving positions?

Not along a single branch. Each exceptional digit has a fixed total budget. Hence only finitely many branch coordinates can differ from 1, even though exceptional digits may drift to higher positions across a sequence before the diagonal subsequence is selected.

### 6. Does the final divisibility calculation have the correct sign?

Yes. From

`y_e = A_N + (b^e - b^N)/(b-1)`

we obtain

`(b-1)y_e = (b-1)A_N + b^e - b^N`.

Both `y_e` and `b^e` are divisible by `p^e`, so `(b-1)A_N - b^N` is divisible by `p^e` for arbitrarily large `e`.

### 7. Why must a fixed integer divisible by arbitrarily high powers of `p` vanish?

Every nonzero integer has finite `p`-adic valuation. Therefore the fixed integer is zero.

### 8. Is the final congruence contradiction correct?

For `b >= 3`, `(b-1)A_N = b^N` reduces modulo `b-1` to `0 = 1`, since `b = 1 mod (b-1)`. The modulus is at least 2. For `N=0` the same contradiction reads `0=1`.

### 9. What happens in base 2?

The congruence argument degenerates because `b-1=1`, but the theorem remains true trivially. This was corrected in the note: base 2 is handled separately rather than excluded from the statement.

### 10. Is coordinatewise digit stabilization enough for p-adic convergence?

Yes, but the original short draft left the epsilon argument implicit. Given `r`, choose `J` with `p^r | b^J`. Once the first `J` digits stabilize and all selected integers have length exceeding `J`, the difference from the limiting series lies in `b^J Z_p`, hence in `p^r Z_p`.

### 11. Is division by `b-1` legal in the p-adic proof?

Yes. Since `p | b`, we have `p not | (b-1)`, so `b-1` is a unit in `Z_p`. This is now stated explicitly.

### 12. Does an empty fixed multiset cause an edge case?

No. The family consists of base-`b` repunits. The tree proof gives `N=0`, and the contradiction remains valid for `b >= 3`; base 2 is already handled separately.

### 13. Does the theorem imply the multiplicative-persistence bound 11?

No. It is a qualitative boundedness theorem for each fixed digit multiset. A global persistence proof would need effective bounds controlled across all relevant multisets and genealogical states.

### 14. Is the finite certificate statement stronger than justified?

The note distinguishes the first empty suffix level `B_e` from the complete finite set `C_e = A_e union B_e`. An empty `B_e` controls long numbers only; shorter exact-family numbers must be enumerated separately.

## Remaining risk

The remaining risk is not an identified mathematical defect. It is novelty and prior-art risk: the argument is elementary enough that it may be folklore, hidden in an unpublished note, or recognizable as a special case of a broader compactness result under different terminology.

## Recommended claim language

> We give an elementary proof of a conjecture stated in a 2021 preprint. We have not located an earlier proof after a targeted literature and citation search, but priority and novelty remain subject to confirmation by the original authors and independent experts.
