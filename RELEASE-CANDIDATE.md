# Virtual Bartender V1 Release Candidate Notes

## Catalog
- 250 seeded built-in recipes
- 90 normalized ingredients
- source/provenance on every seeded recipe
- linked variants and mocktail variants

## Validation
- Python syntax compilation passed
- database seed validation passed
- backend pytest suite passed
- frontend source is configured for a Vite/React production build
- npm dependency installation could not be completed in this artifact environment because the package-registry install timed out; run `npm install && npm run build` locally before deployment

## Networking
The production browser uses same-origin `/api` and `/media` routes. Nginx proxies these to FastAPI. This is necessary so CasaOS access works correctly from both laptops and smartphones on the local network.

## Initial open images
- Margarita — public domain / CC0
- Old Fashioned — CC BY-SA 4.0
- Mojito — CC BY-SA 4.0

Image attribution/license metadata is stored with each recipe and in `data/images/image-manifest.json`.

Images remain optional. Future open images can be added incrementally, and selected AI fallback images may be generated with an on-image `AI-generated image` disclosure.
