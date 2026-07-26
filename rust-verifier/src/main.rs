use serde::Deserialize;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs;
use std::path::Path;

const SCHEMA: &str = "mp-lab.fixed-digit-valuation.v1";
const MAX_LENGTH: usize = 18;

type Result<T> = std::result::Result<T, String>;

#[derive(Deserialize)]
struct Certificate {
    schema: String,
    base: u32,
    prime: u128,
    digit_limits: Vec<(u8, usize)>,
    first_empty_suffix_level: usize,
    prior_level_witness: Option<u128>,
    maximum_valuation: usize,
    maximizing_witness: u128,
    counts: Counts,
    digests: Digests,
    certificate_sha256: String,
}

#[derive(Deserialize)]
struct Counts {
    empty_level_candidates: usize,
    short_exact_family_candidates: usize,
}

#[derive(Deserialize)]
struct Digests {
    empty_level_candidates_sha256: String,
    short_exact_family_sha256: String,
}

fn sha256(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn sha256_lines<I>(lines: I) -> String
where
    I: IntoIterator<Item = String>,
{
    let mut hasher = Sha256::new();
    for line in lines {
        hasher.update(line.as_bytes());
        hasher.update(b"\n");
    }
    format!("{:x}", hasher.finalize())
}

fn power(mut base: u128, mut exponent: usize) -> Result<u128> {
    let mut result = 1_u128;
    while exponent > 0 {
        if exponent % 2 == 1 {
            result = result
                .checked_mul(base)
                .ok_or_else(|| "integer overflow".to_string())?;
        }
        exponent /= 2;
        if exponent > 0 {
            base = base
                .checked_mul(base)
                .ok_or_else(|| "integer overflow".to_string())?;
        }
    }
    Ok(result)
}

fn powers_of_ten(length: usize) -> Result<Vec<u128>> {
    let mut powers = Vec::with_capacity(length);
    let mut value = 1_u128;
    for _ in 0..length {
        powers.push(value);
        value = value
            .checked_mul(10)
            .ok_or_else(|| "decimal overflow".to_string())?;
    }
    Ok(powers)
}

fn repunit(length: usize) -> Result<u128> {
    Ok((power(10, length)? - 1) / 9)
}

fn choose(
    items: &[usize],
    count: usize,
    start: usize,
    current: &mut Vec<usize>,
    output: &mut Vec<Vec<usize>>,
) {
    if current.len() == count {
        output.push(current.clone());
        return;
    }
    let needed = count - current.len();
    if items.len().saturating_sub(start) < needed {
        return;
    }
    for index in start..items.len() {
        current.push(items[index]);
        choose(items, count, index + 1, current, output);
        current.pop();
    }
}

fn combinations(items: &[usize], count: usize) -> Vec<Vec<usize>> {
    let mut output = Vec::new();
    choose(items, count, 0, &mut Vec::new(), &mut output);
    output
}

fn remaining_after(items: &[usize], selected: &[usize]) -> Vec<usize> {
    let selected: BTreeSet<_> = selected.iter().copied().collect();
    items
        .iter()
        .copied()
        .filter(|position| !selected.contains(position))
        .collect()
}

fn add_selected(value: u128, digit: u8, selected: &[usize], powers: &[u128]) -> Result<u128> {
    selected.iter().try_fold(value, |candidate, position| {
        candidate
            .checked_add((u128::from(digit) - 1) * powers[*position])
            .ok_or_else(|| "candidate overflow".to_string())
    })
}

fn enumerate(length: usize, limits: &[(u8, usize)], exact: bool) -> Result<BTreeSet<u128>> {
    fn recurse(
        index: usize,
        remaining: &[usize],
        value: u128,
        limits: &[(u8, usize)],
        exact: bool,
        powers: &[u128],
        output: &mut BTreeSet<u128>,
    ) -> Result<()> {
        if index == limits.len() {
            output.insert(value);
            return Ok(());
        }

        let (digit, limit) = limits[index];
        let counts: Box<dyn Iterator<Item = usize>> = if exact {
            Box::new(std::iter::once(limit))
        } else {
            Box::new(0..=limit.min(remaining.len()))
        };

        for count in counts {
            if count > remaining.len() {
                continue;
            }
            for selected in combinations(remaining, count) {
                let candidate = add_selected(value, digit, &selected, powers)?;
                let next = remaining_after(remaining, &selected);
                recurse(index + 1, &next, candidate, limits, exact, powers, output)?;
            }
        }
        Ok(())
    }

    let powers = powers_of_ten(length)?;
    let positions: Vec<_> = (0..length).collect();
    let mut output = BTreeSet::new();
    recurse(
        0,
        &positions,
        repunit(length)?,
        limits,
        exact,
        &powers,
        &mut output,
    )?;
    Ok(output)
}

fn short_family(cutoff: usize, limits: &[(u8, usize)]) -> Result<BTreeSet<u128>> {
    let minimum: usize = limits.iter().map(|(_, count)| count).sum::<usize>().max(1);
    let mut values = BTreeSet::new();
    for length in minimum..cutoff {
        values.extend(enumerate(length, limits, true)?);
    }
    Ok(values)
}

fn valuation(mut value: u128, prime: u128) -> Result<usize> {
    if value == 0 {
        return Err("value must be positive".to_string());
    }
    let mut exponent = 0;
    while value % prime == 0 {
        value /= prime;
        exponent += 1;
    }
    Ok(exponent)
}

fn validate_limits(limits: &[(u8, usize)]) -> Result<()> {
    let mut previous = None;
    for &(digit, count) in limits {
        if !(2..=9).contains(&digit) || count == 0 {
            return Err("invalid digit limit".to_string());
        }
        if let Some(previous_digit) = previous {
            if previous_digit >= digit {
                return Err("digit limits must be strictly increasing".to_string());
            }
        }
        previous = Some(digit);
    }
    Ok(())
}

fn witness_digits(mut value: u128) -> Result<BTreeMap<u8, usize>> {
    if value == 0 {
        return Err("witness must be positive".to_string());
    }
    let mut counts = BTreeMap::new();
    while value > 0 {
        let digit = (value % 10) as u8;
        if digit == 0 {
            return Err("witness contains zero".to_string());
        }
        if digit != 1 {
            *counts.entry(digit).or_insert(0) += 1;
        }
        value /= 10;
    }
    Ok(counts)
}

fn outer_digest(root: &Value) -> Result<String> {
    let mut unsigned = root.clone();
    unsigned
        .as_object_mut()
        .ok_or_else(|| "certificate root must be an object".to_string())?
        .remove("certificate_sha256");
    let bytes = serde_json::to_vec(&unsigned)
        .map_err(|error| format!("cannot canonicalize certificate: {error}"))?;
    Ok(sha256(&bytes))
}

fn verify(path: &Path) -> Result<()> {
    let text = fs::read_to_string(path)
        .map_err(|error| format!("cannot read {}: {error}", path.display()))?;
    let root: Value = serde_json::from_str(&text)
        .map_err(|error| format!("invalid JSON in {}: {error}", path.display()))?;
    let expected_outer = outer_digest(&root)?;
    let certificate: Certificate = serde_json::from_value(root)
        .map_err(|error| format!("invalid schema in {}: {error}", path.display()))?;

    if certificate.schema != SCHEMA {
        return Err("unsupported certificate schema".to_string());
    }
    if certificate.base != 10 || !matches!(certificate.prime, 2 | 5) {
        return Err("version 1 supports base 10 and prime 2 or 5".to_string());
    }
    if certificate.certificate_sha256 != expected_outer {
        return Err("certificate_sha256 mismatch".to_string());
    }
    validate_limits(&certificate.digit_limits)?;

    let cutoff = certificate.first_empty_suffix_level;
    if !(1..=MAX_LENGTH).contains(&cutoff) {
        return Err(format!("cutoff must be between 1 and {MAX_LENGTH}"));
    }

    let empty = enumerate(cutoff, &certificate.digit_limits, false)?;
    let modulus = power(certificate.prime, cutoff)?;
    if empty.iter().any(|value| value % modulus == 0) {
        return Err("claimed empty level is not empty".to_string());
    }

    if cutoff == 1 {
        if certificate.prior_level_witness.is_some() {
            return Err("level 1 must have null prior witness".to_string());
        }
    } else {
        let prior = enumerate(cutoff - 1, &certificate.digit_limits, false)?;
        let prior_modulus = power(certificate.prime, cutoff - 1)?;
        let divisible: BTreeSet<_> = prior
            .into_iter()
            .filter(|value| value % prior_modulus == 0)
            .collect();
        if divisible.is_empty() {
            return Err("claimed empty level is not first".to_string());
        }
        if !certificate
            .prior_level_witness
            .is_some_and(|witness| divisible.contains(&witness))
        {
            return Err("invalid prior-level witness".to_string());
        }
    }

    let short = short_family(cutoff, &certificate.digit_limits)?;
    let pairs: Vec<_> = short
        .iter()
        .map(|value| Ok((*value, valuation(*value, certificate.prime)?)))
        .collect::<Result<_>>()?;
    let short_max = pairs
        .iter()
        .map(|(_, exponent)| *exponent)
        .max()
        .unwrap_or(0);
    let actual_max = short_max.max(cutoff - 1);

    if certificate.maximum_valuation != actual_max {
        return Err(format!(
            "claimed maximum {} differs from verified {actual_max}",
            certificate.maximum_valuation
        ));
    }
    if valuation(certificate.maximizing_witness, certificate.prime)? != actual_max {
        return Err("maximizing witness has wrong valuation".to_string());
    }
    let required: BTreeMap<_, _> = certificate.digit_limits.iter().copied().collect();
    if witness_digits(certificate.maximizing_witness)? != required {
        return Err("maximizing witness is outside exact family".to_string());
    }

    if certificate.counts.empty_level_candidates != empty.len() {
        return Err("empty-level count mismatch".to_string());
    }
    if certificate.counts.short_exact_family_candidates != short.len() {
        return Err("short-family count mismatch".to_string());
    }

    let empty_digest = sha256_lines(empty.iter().map(ToString::to_string));
    if certificate.digests.empty_level_candidates_sha256 != empty_digest {
        return Err("empty-level digest mismatch".to_string());
    }
    let short_digest = sha256_lines(
        pairs
            .iter()
            .map(|(value, exponent)| format!("{value}:{exponent}")),
    );
    if certificate.digests.short_exact_family_sha256 != short_digest {
        return Err("short-family digest mismatch".to_string());
    }

    println!(
        "valid: {} (v_{} = {}, witness = {}, cutoff = {})",
        path.display(),
        certificate.prime,
        actual_max,
        certificate.maximizing_witness,
        cutoff
    );
    Ok(())
}

fn main() {
    let paths: Vec<_> = env::args().skip(1).collect();
    if paths.is_empty() {
        eprintln!("usage: mp-certificate-verifier CERTIFICATE.json [...]");
        std::process::exit(2);
    }

    let mut failed = false;
    for raw_path in paths {
        let path = Path::new(&raw_path);
        if let Err(error) = verify(path) {
            eprintln!("invalid: {}: {error}", path.display());
            failed = true;
        }
    }
    if failed {
        std::process::exit(1);
    }
}
