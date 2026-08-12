# CasaOS Installation Guide

Virtual Bartender is designed to run locally on a CasaOS server and be accessed from a laptop, phone, or tablet on the same network. The application uses two Docker containers: a FastAPI backend and an Nginx-served React frontend. Its SQLite database, recipe images, and backups are stored outside the disposable containers.

> **Private repository note:** This repository is private. The simplest installation method is to clone it onto the CasaOS host over SSH using GitHub authentication, then launch the included Compose file.

## What you need

- A working CasaOS server with Internet access for the initial download/build.
- SSH access to the CasaOS host, or another way to open a terminal on it.
- Your GitHub account with access to this private repository.
- Git installed on the CasaOS host.
- Docker and Docker Compose. CasaOS normally provides the Docker environment.

## 1. Connect to the CasaOS server

From another computer, open PowerShell, Windows Terminal, Terminal, or another SSH client and connect to the CasaOS machine:

```bash
ssh YOUR_CASAOS_USERNAME@YOUR_CASAOS_IP
```

Replace the username and IP address with those of your CasaOS server.

## 2. Check Git and Docker

Run:

```bash
git --version
docker --version
docker compose version
```

If all three commands report versions, continue.

If Git is missing on a Debian/Ubuntu-based CasaOS host:

```bash
sudo apt update
sudo apt install -y git
```

## 3. Authenticate to the private GitHub repository

Because Virtual Bartender is private, GitHub must authenticate the clone. Do not put a GitHub password directly into scripts or Compose files.

One option is GitHub CLI if it is already installed on the CasaOS host:

```bash
gh auth login
```

Then choose GitHub.com and HTTPS and complete the browser/device login.

Alternatively, configure an SSH key for the CasaOS host in your GitHub account and use the SSH clone form. GitHub also supports HTTPS authentication with a personal access token.

## 4. Clone Virtual Bartender

Choose a permanent location for the source. For example:

```bash
cd /DATA
sudo mkdir -p Apps
sudo chown "$USER":"$USER" Apps
cd Apps
git clone https://github.com/rpiammocan/virtual-bartender.git
cd virtual-bartender
```

If you use GitHub SSH authentication instead, clone using the repository's SSH address.

Verify that the project contains at least:

```text
backend/
frontend/
casaos/
data/
docker-compose.yml
README.md
```

## 5. Prepare persistent directories

From the repository root:

```bash
mkdir -p data backups
```

Virtual Bartender stores its SQLite database and recipe media under `data/` and its backups under `backups/`. These directories survive container recreation.

## 6. Start Virtual Bartender

Run the CasaOS-specific Compose file from the repository root:

```bash
docker compose -f casaos/docker-compose.yml up --build -d
```

The first build can take several minutes because Docker must download base images and build the frontend and backend.

## 7. Verify the containers

Run:

```bash
docker compose -f casaos/docker-compose.yml ps
```

You should see both of these services running:

```text
virtual-bartender-backend
virtual-bartender-web
```

For a backend health check:

```bash
curl http://localhost:8000/api/health
```

A healthy backend should return:

```json
{"status":"ok"}
```

## 8. Open Virtual Bartender

From a computer or phone on the same network, browse to:

```text
http://YOUR_CASAOS_IP:8080
```

For example, if the CasaOS server is `192.168.1.50`:

```text
http://192.168.1.50:8080
```

The web interface uses same-origin `/api` and `/media` routes internally, so phones and other computers access the backend through the CasaOS server rather than trying to use their own `localhost` address.

## 9. Optional: change the web port or data locations

The CasaOS Compose file accepts these environment variables:

```text
APP_DATA_DIR
APP_BACKUP_DIR
WEB_PORT
```

For example:

```bash
APP_DATA_DIR=/DATA/AppData/virtual-bartender/data \
APP_BACKUP_DIR=/DATA/AppData/virtual-bartender/backups \
WEB_PORT=8090 \
docker compose -f casaos/docker-compose.yml up --build -d
```

You would then open `http://YOUR_CASAOS_IP:8090`.

## Updating Virtual Bartender later

Before updating, make sure important data is backed up. Then from the repository directory:

```bash
cd /DATA/Apps/virtual-bartender
git pull
docker compose -f casaos/docker-compose.yml up --build -d
```

The bind-mounted `data/` and `backups/` directories are not replaced when the containers are rebuilt.

## Stopping the application

```bash
docker compose -f casaos/docker-compose.yml down
```

To start it again:

```bash
docker compose -f casaos/docker-compose.yml up -d
```

Do not add `-v` to the `down` command unless you intentionally want Docker-managed volumes removed.

## Logs and troubleshooting

View all application logs:

```bash
docker compose -f casaos/docker-compose.yml logs --tail=100
```

Follow the logs live:

```bash
docker compose -f casaos/docker-compose.yml logs -f
```

Backend only:

```bash
docker logs virtual-bartender-backend --tail=100
```

Web frontend only:

```bash
docker logs virtual-bartender-web --tail=100
```

### Port 8080 is already in use

Choose another port, for example:

```bash
WEB_PORT=8090 docker compose -f casaos/docker-compose.yml up --build -d
```

Then open `http://YOUR_CASAOS_IP:8090`.

### Containers do not start

Check:

```bash
docker compose -f casaos/docker-compose.yml ps
docker compose -f casaos/docker-compose.yml logs --tail=200
```

### GitHub clone says authentication failed

The repository is private. Confirm that the CasaOS host has authenticated access to the GitHub account that owns or can read `rpiammocan/virtual-bartender`. GitHub no longer accepts normal account passwords for Git operations over HTTPS; use GitHub CLI/device authentication, SSH, or an appropriate personal access token.

## CasaOS dashboard integration

The included `casaos/docker-compose.yml` contains `x-casaos` metadata for CasaOS. The command-line Compose method above is the most predictable first installation path because this application currently builds its images from the source repository rather than pulling prebuilt images from a public container registry.

After the application is validated on the CasaOS host, a later release can publish prebuilt Docker images and make installation through CasaOS's graphical custom-app/import workflow simpler.
