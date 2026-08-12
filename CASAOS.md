# CasaOS Deployment

Virtual Bartender remains local-first. The CasaOS package is prepared so the same local source tree can later be deployed on CasaOS.

CasaOS supports importing external Docker Compose applications, and its current app-store source format is Compose-based with `x-casaos` metadata.

## Intended deployment

1. Copy the project folder to the CasaOS host.
2. Set persistent paths if desired:

```text
APP_DATA_DIR=/path/to/virtual-bartender/data
APP_BACKUP_DIR=/path/to/virtual-bartender/backups
WEB_PORT=8080
```

3. Import/use `casaos/docker-compose.yml`.
4. Open Virtual Bartender from CasaOS or browse to the configured port.

Personal data remains in the mounted data/backups directories, not inside disposable containers.
