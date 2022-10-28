#!/bin/bash
set -eo pipefail

poetry run invoke initialize-database

exec "$@"
