# Virtual Bartender — Web Edition

This is the browser-hosted edition of Virtual Bartender.

It is a first-class platform target alongside CasaOS, Windows, and Android/APK. Users open a normal HTTPS URL in Chrome, Edge, Firefox, or Safari; CasaOS is not required.

## Architecture

The Web edition intentionally reuses the same application components as the other server-backed builds:

- `frontend/` — React + TypeScript user interface
- `backend/` — FastAPI recipe, inventory, matching, shopping, import, history, favorites, and backup services
- SQLite persistent application data

`web/docker-compose.yml` packages those components for ordinary web hosting. The frontend is the public entry point and proxies `/api/` and `/media/` to the private backend service.

## Run the Web edition

From the repository root:

```bash
docker compose -f web/docker-compose.yml up --build -d
```

Then open:

```text
http://localhost:8080
```

For an Internet-facing deployment, put an HTTPS reverse proxy or hosting platform in front of port 8080. Do not expose the backend service directly.

## Persistent data

Docker-managed volumes keep the Web edition independent of CasaOS host paths:

- `bartender_web_data` — SQLite database and locally stored recipe media
- `bartender_web_backups` — application backups

Removing/recreating containers does not delete these named volumes unless they are explicitly removed.

## Browser support

The frontend is a responsive Vite/React application and is intended for current desktop and mobile browsers. No APK, Windows installer, or CasaOS installation is required for this edition.

## Security note

The current Virtual Bartender V1 application is designed as a local-first, single-user application and does not yet provide Internet-grade user authentication. For public Internet hosting, authentication/access control should be added before treating the site as a public multi-user service.
