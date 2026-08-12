# Virtual Bartender V1

Offline-first cocktail recipe and bar-management application.

## Foundation milestone

This repository contains the initial V1 scaffold:
- FastAPI backend
- React + TypeScript frontend
- SQLite via SQLAlchemy
- Alembic migration structure
- Docker Compose deployment
- Persistent data and backup directories
- Core V1 database schema
- Initial home screen

The built-in recipe library is intentionally not populated yet. Recipe-source/licensing decisions will be made before the ~250 built-in recipes are added.

## Run with Docker

    docker compose up --build -d

Then open:

    http://localhost:8080

API health check:

    http://localhost:8000/api/health

Docker Compose volumes/bind mounts are used so application data survives container recreation. Docker documents Compose as the recommended way to define services, networks, and volumes for a multi-container application.
