# Virtual Bartender V1

Virtual Bartender is a local-first cocktail and mocktail recipe application designed to run on a home server such as CasaOS and be accessed from a laptop, phone, or tablet.

## 🍸 Open the Live Application

### [Launch Virtual Bartender](https://rpiammocan.github.io/virtual-bartender-web/)

The link above opens the browser-hosted Web edition. The CasaOS edition remains self-hosted on your own server.

## 🍹 Install on CasaOS

### ⬇️ [Download the latest CasaOS installation YAML](https://raw.githubusercontent.com/rpiammocan/virtual-bartender-casaos/main/casaos/virtual-bartender.yaml)

Download the YAML above, then import it into CasaOS to install Virtual Bartender.

[View the YAML on GitHub](https://github.com/rpiammocan/virtual-bartender-casaos/blob/main/casaos/virtual-bartender.yaml) · [CasaOS installation and troubleshooting guide](CASAOS.md)

The default Virtual Bartender web port is **9191**.

Once running, open:

```text
http://YOUR_CASAOS_IP:9191
```

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
- Human-readable recipe printing
- Metric display option
- Local SQLite storage
- Backup/restore support
- Responsive React web interface
- FastAPI backend
- Docker/CasaOS deployment
- Optional locally stored recipe images with provenance metadata

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

Pull the latest container images and recreate the CasaOS containers, or reinstall using the current CasaOS YAML linked at the top of this README.

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

Virtual Bartender V1 is actively being tested and refined for CasaOS deployment.
