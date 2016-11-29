#!/bin/bash -e

BIN_DIR=$(python -c "import os.path as p ; print p.dirname(p.realpath('${BASH_SOURCE[0]}'))")
PROJECT_ROOT=$(dirname "${BIN_DIR}")

cd "${PROJECT_ROOT}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
export PYTHONIOENCODING=utf-8

exec python CompanyInfoScraper $*