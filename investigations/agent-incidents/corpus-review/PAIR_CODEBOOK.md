# Comparing conclusions across follow-ups

This codebook defines the manual comparison of each original report with its continued investigation. A longer report or a higher reconstruction grade does not, by itself, establish improvement. The comparison concerns the underlying propositions and their supporting evidence.

## Transition definitions

| Transition | Meaning |
|---|---|
| `retained_supported` | A supported observation or reasonable qualified inference remains defensible. This does not turn an inference into proof. |
| `retained_problem` | A contradicted or insufficiently supported conclusion remains problematic, even if its explanation becomes longer. |
| `corrected_statement` | The follow-up replaces the earlier statement with a substantively corrected account. |
| `qualified_statement` | The follow-up narrows or qualifies the earlier claim enough to match the available evidence. Adding a confidence adjective alone is insufficient. |
| `omitted` | The earlier proposition is absent. Disappearance is not correction. |
| `superseded` | The proposition materially changes and cannot be treated as simply retained. This includes a previously defensible claim becoming problematic. |
| `unassessable` | The relation or scope cannot be resolved adequately. |

A correction may be silent. It does not prove that the investigator recognized its earlier mistake or changed its internal understanding. Explicit acknowledgment is recorded separately.

Every parent claim has exactly one transition. Every follow-up claim is either mapped to a parent claim or identified as new. Several parent claims may map to one follow-up entry. Compare the actual source passages, including qualifications elsewhere in the report; do not match by keywords alone.

If comparison reveals a coding mistake in either report, correct that assessment and record the reconciliation. Do not alter a judgment merely to make a transition fit. Unchanged wording cannot demonstrate a new qualification simply because the two readings initially assigned different labels.

## Stored comparison

Each JSON file records:

- Parent and follow-up artifact identifiers, review IDs and source hashes.
- `manual_comparison: true`, a comparison summary and its limits.
- One transition per parent claim: the one-based parent claim index; mapped follow-up indices; transition; rationale; parent and follow-up source lines; explicit acknowledgment; and whether the interpretation is disputable.
- Every follow-up claim index not mapped to a parent, in `new_followup_claim_indices`.

Claim indices refer to the ordered `claims` arrays in the associated review files. Changes to those arrays require reconciliation of the comparisons.

## Provenance and denominators

The published index contains 78 comparisons. Archived run metadata verifies 77 links and repairs one: C059 continued C216, not C215. The original C215 comparison remains in `pairs/`; the verified C216 comparison is in `pairs-repaired/`. The primary results therefore use **78 corrected continuations**, while the complete record contains **79 manual comparisons**, including the diagnostic original. These sets must not be added.

New or materially changed problematic follow-up entries include unmatched new claims and problematic superseding claims. They are deduplicated by follow-up claim index; entries also mapped as retained problems are excluded from the new-or-changed count. Both components are reported separately. Sensitivity counts exclude disputed parent, follow-up and transition readings. A retained problem qualifies for the narrower count only when at least one mapped problematic follow-up claim is also undisputed; an adequate repair requires a mapped undisputed supported claim. Omitted claims have no follow-up judgment.

Counts of repairs, retained problems and new problems can overlap within a report. Claims are grouped interpretive units, not independent trials. This comparison does not estimate a causal effect of time, length, model or provider, and it does not measure operational harm.
