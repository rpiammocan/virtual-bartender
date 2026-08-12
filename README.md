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

A complete step-by-step guide is available in **[CASAOS.md](CASAOS.md)**.

The short version is:

```bash
cd /DATA/Apps
git clone https://github.com/rpiammocan/virtual-bartender.git
cd virtual-bartender
mkdir -p data backups
docker compose -f casaos/docker-compose.yml up --build -d
```

Because this repository is private, authenticate the CasaOS host with GitHub before cloning it. See `CASAOS.md` for GitHub authentication choices, verification, updating, backups, port changes, and troubleshooting.

Once running, open:

```text
http://YOUR_CASAOS_IP:8080
```

Backend health check:

```text
http://YOUR_CASAOS_IP:8000/api/health
```

## Standard Docker installation

From the repository root:

```bash
docker compose up --build -d
```

Then open:

```text
http://localhost:8080
```

## Persistent data

Virtual Bartender keeps user/application data outside disposable containers. The default Compose configuration uses:

```text
data/       SQLite database and local media
backups/    application backups
```

Do not commit local databases, backups, environment secrets, `node_modules`, or Python virtual environments to Git. The repository `.gitignore` excludes these items.

## Updating

For a CasaOS source installation:

```bash
git pull
docker compose -f casaos/docker-compose.yml up --build -d
```

See **[CASAOS.md](CASAOS.md)** before updating a system containing data you care about.

## Project structure

```text
backend/                 FastAPI backend
frontend/                React + TypeScript frontend
casaos/                  CasaOS-specific Compose configuration
data/                    Seed content and persistent runtime data
CASAOS.md                Full CasaOS installation guide
docker-compose.yml       Standard Docker Compose deployment
```

## Current status

V1 is at release-candidate stage. The built-in recipe target has been reached. Backend validation and tests have passed in the development artifact environment; the final production frontend build and full CasaOS-host smoke test should be completed on the deployment machine.
