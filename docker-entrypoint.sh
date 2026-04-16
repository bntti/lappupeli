#!/bin/sh
set -eo pipefail

uv run python src/initialize_database.py

exec "$@"
