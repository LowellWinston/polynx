#!/bin/bash

set -e  # Exit on error
set -o pipefail

VENV_DIR="../venv"

source "$VENV_DIR/bin/activate"
twine upload dist/*
