# Milestone 9 — Units, Smart Shopping, URL Import

Implemented:

## Unit conversion
- Converts supported US volumetric units to metric base values for quantity-aware matching.
- Current supported seeded units: oz, tsp, tbsp.
- Non-convertible units such as dash/piece remain conservative.

## Smart shopping
- Finds Almost There recipes with exactly one blocker.
- Groups by missing ingredient.
- Shows how many recipes each purchase unlocks.
- Lists the affected recipes.
- Lets the user add a suggested item to the categorized shopping list.

## URL recipe import
- Accepts http/https URLs.
- First attempts Schema.org/JSON-LD Recipe extraction.
- Falls back to webpage heuristic extraction.
- Preserves source URL and source hostname.
- Returns a review payload rather than saving automatically.
- Surfaces extraction warnings.
- Frontend review page added.

Still next:
- structured parsing of imported ingredient text into quantities/units/known ingredients
- duplicate detection before import save
- final review/edit/save workflow
- Markdown/TXT export
- backup/restore UI and automatic backup scheduler
