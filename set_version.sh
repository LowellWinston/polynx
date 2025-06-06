#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 NEW_VERSION"
  exit 1
fi

NEW_VERSION="$1"
INIT_PY="src/polynx/__init__.py"

# __init__.py (spaces style)
sed -i "" -E "s/^([[:space:]]*__version__[[:space:]]*=[[:space:]]*\")([^\"]+)(\".*)/\1$NEW_VERSION\3/" "$INIT_PY"

# pyproject.toml (spaces style)
sed -i "" -E "s/^([[:space:]]*version[[:space:]]*=[[:space:]]*\")([^\"]+)(\".*)/\1$NEW_VERSION\3/" pyproject.toml

# Update setup.py (version="...")
sed -i "" -E "s/(version\s*=\s*\").*(\")/\1$NEW_VERSION\2/" setup.py

echo "Version updated to $NEW_VERSION in $INIT_PY, pyproject.toml, and setup.py"


