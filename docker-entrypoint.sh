#!/bin/sh
set -eo pipefail

uv run python lappupeli/initialize_database.py

exec "$@"
