# ADR Workflow

## File Naming
`NNNN-title-with-hyphens.md` — NNNN is the next sequential number from `docs/adr/index.md`.

## Creating a New ADR
1. Copy from `docs/adr/template.md` without modifying the template itself.
2. Set Status to `proposed` and Date to today.
3. Add a row to `docs/adr/index.md`.
4. Link related ADRs using relative paths.

## Updating Status
- Only modify the `Status` field and `Date`; never rewrite accepted ADR content.
- When superseding, add a link to the new ADR in the old one.

## Linking
Use relative links only. Standard relationship labels: `Supersedes`, `Refined by`, `Related to`.

## Required Sections (from template)
- **Context** – problem statement, constraints, current state
- **Decision Drivers** – technical/business requirements, measurable where possible
- **Options Considered** – ≥2 options, pros/cons, "do nothing" if applicable
- **Decision** – chosen option and rationale
- **Consequences** – positive, negative, and neutral impacts

## Immutability Rule
ADRs are immutable once accepted. Create a new ADR to supersede; never delete or rewrite old ones.
