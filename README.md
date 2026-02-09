# PixelFort

Photo NAS system for family photo backup and management.

## Features
- FastAPI backend
- SQLAlchemy ORM with SQLite
- Docker containerization
- Environment-based configuration

## Setup
```bash
cp .env.example .env
docker-compose up -d
```

## Development
```bash
docker-compose -f docker-compose.dev.yml up
