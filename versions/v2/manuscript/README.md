# Rank-ideal consequences of the Brauer complete-mapping classification

Horace Dong proved in September 2026 that, for positive degree `n`, both monoids have a complete mapping exactly when `n = 1` or `n >= 4`; every proper Brauer factor admits one, and the sole partial Brauer exception is rank two at degree three. See Theorem 1.1 of *Complete mappings of the Brauer and partial Brauer monoids*, [September text](https://github.com/Horace-Maxwell/ai4math-results/blob/1342597dde7e3d424c88f0524dc2e6347670e6ad/papers/brauer-complete-mappings/note.pdf), and its [October version 2](https://github.com/Horace-Maxwell/ai4math-results/blob/a9c15a2d3bd9974a9bde05ca278fdcc2e28d8f5a/papers/brauer-complete-mappings/note.pdf). This answers the existence clauses of Problem 15.11 in Araújo, Bentz, Cameron, Hendrey and Kinyon, *Complete Mappings of Semigroups*, arXiv:2608.25092v1, Section 15, printed page 61.

The written proof gives an adjacent-subset version of the signed-triangle construction and derives the complete rank-ideal classification. For a nonempty rank-cutoff ideal `I_q` with `0 <= q <= n`, a Brauer ideal admits a complete mapping exactly when `n` is not 2 or 3, or `q < n`; a partial Brauer ideal admits one exactly when `n` is not 2 or 3, or `q <= 1`. Every complete mapping and its product permutation preserve ranks. The note also characterizes identity-sandwich Brandt factors over `S_2` and `S_3` and parametrizes all complete mappings of the minimal Brauer and rank-zero partial Brauer factors: `(m!)^(2m)` mappings for `m` half diagrams. Higher-rank enumeration is not covered.

## Contents

- `note.tex`: complete LaTeX source, with its bibliography included.
- `note.pdf`: readable typeset note, supplied separately from the source archive.
- `metadata.json`: creators, license, problem identity and scientific scope.
- `verify.py`: standard-library Python exact finite checks.
- `verification.json`: the deterministic expected output of those checks.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively use a conventional LaTeX installation with `geometry`, `lmodern`, the AMS packages, `booktabs`, `longtable`, `array`, `hyperref` and `microtype`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded, so BibTeX and external `.bib` files are unnecessary. No shell escape is required. A first Tectonic build needs access to its standard TeX bundle, or an existing local bundle.

## Exact finite checks

With Python 3.10 or later:

```sh
python3 verify.py > reproduced.json
cmp verification.json reproduced.json
```

The output contains `ALL_CHECKS_OK` in its `result` field. Computations use exact Python integers and permutations; there are no floating-point tolerances or randomized choices. They check 1,928 subset instances in eight degree/rank combinations, recurrence and binomial parity through degree 40, all 72 sign-fibre cases for `S_3`, and 76,856 nonzero factor elements across eight factors. All 76,856 selected products are also computed directly by three-row exterior connectivity and compared with the coordinate products. Diagram counts through degree four are independently enumerated. The finite ranges illustrate the constructions; the written proof establishes the all-degree statements.

Further checks construct transversals for the nine occurring rank-zero/rank-one classes at degrees one through three, check all 324 products of the exceptional 18-element nonzero rank-two factor, check eight identity-sandwich cases, and enumerate all 24 permutations of a four-element rectangular band, exactly 16 of which are complete mappings.

## Formal scope

The PDF links the precise Lean files at revision `a89e0fb9ba0f9002502ec8125455c2c2a9281443`. The declaration `D5.S3.Combinatorics.PerfectMatchings.AraujoBrauerCompleteMapping.result` states the positive-degree existence equivalences for both literal diagram monoids, including existence of their monoid structures. The subset-pairing, signed-half-cycle and signed-factor declarations specify the two exceptional infinite families. The rank-filtration lemma, the complete ideal classification, the identity-sandwich criterion and the minimal-factor enumeration have written proofs. The whole-monoid declaration does not state these additional results. The Python output states only its finite computational scope.

## Authors and license

1. Haobo Ma — ChronoAI Pte Ltd, Singapore.
2. Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore.

CC BY 4.0 (`cc-by-4.0`), https://creativecommons.org/licenses/by/4.0/ .
