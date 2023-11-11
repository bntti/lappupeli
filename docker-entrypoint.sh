#!/bin/sh
set -eo pipefail

poetry run python lappupeli/initialize_database.py

exec "$@"
