# Support Desk AI Agent

Support desk agent that triages tickets, proposes macros/SLA, drafts replies, and keeps an auditable inbox workflow.

![CI](https://img.shields.io/badge/CI-pytest%20%7C%20ruff-22c55e)
![Python](https://img.shields.io/badge/python-3.11%2B-3b82f6)
![License](https://img.shields.io/badge/license-MIT-informational)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn backend.main:app --reload --port 8000
```

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest -q --cov=backend
```

## Docs

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Deployment](docs/deployment.md)

## License

MIT — see [LICENSE](LICENSE).
