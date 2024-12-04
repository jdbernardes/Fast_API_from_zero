#!/bin/sh

#Run alembic migrations
poetry run alembic upgrade head

#Start Uvicorn Server
poetry run uvicorn --host 0.0.0.0 --port 8000 fast_api_from_zero.app:app