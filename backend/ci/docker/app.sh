#!/bin/bash

alembic upgrade head

uvicorn src.main:app --host 0.0.0.0 --port 8000
# gunicorn src.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
