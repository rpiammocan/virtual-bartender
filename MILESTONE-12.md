# Milestone 12 — Release Preparation

Implemented:

- ingredient alias/normalization layer
- importer uses normalized aliases before creating new ingredients
- recipe image metadata: source, license, attribution, AI-generated flag
- UI displays AI-generated disclosure over AI recipe images
- US/metric recipe display toggle
- ~20 additional curated recipes/mocktails
- catalog now substantially larger for development/testing
- Alembic migration for image metadata and ingredient aliases
- CasaOS-ready Compose source with x-casaos metadata
- persistent local data and backup mount configuration
- CasaOS deployment documentation
- local SVG application icon

Still before V1 final:
- expand curated catalog closer to target ~250
- source/review actual open recipe images
- generate selected fallback AI images with disclosure where worthwhile
- polish sorting/filtering and mobile UI
- run integration/build tests and correct any issues
