# Milestone 8 — Advanced Recipe Matching

Implemented:

- Exact-match status
- Substitution-match status
- Linked-variant status
- Almost There status
- Quantity-aware matching when inventory quantity is entered
- Unknown inventory quantity still means "assume enough"
- Optional ingredient shortfalls never block makeability
- Preferred substitution ordering
- Parent recipes can surface makeable linked variants/mocktail variants
- Surprise Me can independently include/exclude substitutions and variants
- UI now separates Exact / Substitution / Variant / Almost There

Quantity conversion note:
V1 only compares quantities directly when units are the same. Different known units are currently treated conservatively until the unit-conversion service is added.
