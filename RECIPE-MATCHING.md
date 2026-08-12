# V1 Recipe Matching Engine

The first implementation follows the V1 rules:

1. A required ingredient must be present in the selected bar.
2. Approved substitutions can satisfy a required ingredient.
3. Optional ingredients do not prevent a recipe from being Makeable.
4. Zero missing required ingredients => `makeable`.
5. Exactly one missing required ingredient => `almost_there`.
6. More than one missing required ingredient => `not_makeable`.
7. Matching returns an explanation and lists the missing ingredients.
8. My Bar and Tonight's Bar are selected through the same matching engine but use different inventory contexts.

## Quantity handling

Quantity-aware matching is intentionally not enabled in this first engine pass. The schema already stores quantity and unit so that the next matching-engine revision can add it without changing the API concept.

## Future matching layers

Before the engine is considered complete, it will gain:
- compatible ingredient forms
- preferred substitutions
- ingredient-family matching
- quantity-aware matching
- recipe variants
- richer "Almost There" explanations
- ranking/filtering for the UI
