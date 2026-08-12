# Virtual Bartender V1

Virtual Bartender is a local-first cocktail and mocktail recipe application designed to run on a home server such as CasaOS and be accessed from a laptop, phone, or tablet.

## V1 highlights

- 250 seeded built-in recipes
- Cocktail and mocktail support
- My Bar inventory
- Makeable and Almost There drink matching
- Ingredient substitutions and recipe variants
- Tonight's Bar
- Smart shopping suggestions and printable shopping list
- Favorites and history
- Surprise Me
- Recipe import with review before saving
- Human-readable recipe export and printing
- Metric display option
- Local SQLite storage
- Backup/restore support
- Responsive React web interface
- FastAPI backend
- Docker/CasaOS deployment
- Optional locally stored recipe images with provenance metadata

## CasaOS installation

For CasaOS, the easiest installation is the Compose file at **`casaos/virtual-bartender.yaml`**. It builds directly from this public GitHub repository, so CasaOS does not need to authenticate to GitHub Container Registry.

The default Virtual Bartender web port is **9190**.

Once running, open:

```text
http://YOUR_CASAOS_IP:9190
```

Backend health check:

```text
http://YOUR_CASAOS_IP:8000/api/health
```

A complete source-based installation and troubleshooting guide is available in **[CASAOS.md](CASAOS.md)**.

## Standard Docker installation

From the repository root:

```bash
docker compose up --build -d
```

## Persistent data

Virtual Bartender keeps user/application data outside disposable containers. CasaOS uses:

```text
/DATA/AppData/virtual-bartender/data
/DATA/AppData/virtual-bartender/backups
```

Do not commit local databases, backups, environment secrets, `node_modules`, or Python virtual environments to Git. The repository `.gitignore` excludes these items.

## Updating

Re-import/rebuild the CasaOS application from the current `casaos/virtual-bartender.yaml`, or for a source clone:

```bash
git pull
docker compose -f casaos/docker-compose.yml up --build -d
```

## Project structure

```text
backend/                         FastAPI backend
frontend/                        React + TypeScript frontend
casaos/virtual-bartender.yaml    CasaOS direct-import definition
casaos/docker-compose.yml        CasaOS source-clone Compose configuration
data/                            Seed content and persistent runtime data
CASAOS.md                        Full CasaOS installation guide
docker-compose.yml               Standard Docker Compose deployment
```

## Current status

V1 is at release-candidate stage. The built-in recipe target has been reached. Backend validation and tests have passed in the development artifact environment; the final production frontend build and full CasaOS-host smoke test should be completed on the deployment machine.
