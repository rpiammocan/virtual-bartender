# Local Development

## Backend

From `backend/`:

```text
python -m venv .venv
```

Windows:

```text
.venv\Scripts\activate
```

macOS/Linux:

```text
source .venv/bin/activate
```

Then:

```text
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API:
- http://127.0.0.1:8000/api/health
- http://127.0.0.1:8000/docs

## Frontend

From `frontend/`:

```text
npm install
npm run dev
```

The frontend is currently a presentation scaffold; API-connected screens are the next UI milestone.

## Data

For local development, the SQLite database should ultimately live under the project's persistent `data/` directory. Do not commit the database, backups, or personal recipe data to source control.
