#!/bin/sh
set -eo pipefail

poetry run python src/initialize_database.py

exec "$@"
