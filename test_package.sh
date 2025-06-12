#!/bin/bash

set -e  # Exit on error
set -o pipefail

PACKAGE_NAME="polynx"
DIST_DIR="dist"
VENV_DIR="../venv"

#echo "🔧 Creating virtual environment..."
#python3 -m venv "$VENV_DIR"
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "🧪 Not inside a virtual environment. Activating $VENV_DIR..."
  source "$VENV_DIR/bin/activate"
else
  echo "🧪 Already inside a virtual environment: $VIRTUAL_ENV"
fi

# Extract version from setup.py
SETUP_VERSION=$(sed -nE "s/.*version\s*=\s*['\"]([0-9]+\.[0-9]+(\.[0-9]+)?)['\"].*/\1/p" setup.py)

REBUILD_NEEDED=false

if [ ! -d "$DIST_DIR" ]; then
    echo "📦 dist directory not found. Rebuilding..."
    REBUILD_NEEDED=true
else
    LATEST_FILE=$(ls -t $DIST_DIR/${PACKAGE_NAME}-*.whl 2>/dev/null | head -1)
    if [ -z "$LATEST_FILE" ]; then
        echo "📦 No existing wheel found. Rebuilding..."
        REBUILD_NEEDED=true
    else
        DIST_VERSION=$(echo "$LATEST_FILE" | sed -E "s|.*${PACKAGE_NAME}-([0-9]+\.[0-9]+(\.[0-9]+)?).*|\1|")

        if [ "$SETUP_VERSION" != "$DIST_VERSION" ]; then
            echo "🔁 Version mismatch: setup.py=$SETUP_VERSION, dist=$DIST_VERSION. Rebuilding..."
            REBUILD_NEEDED=true
        else
            echo "✅ Package version $SETUP_VERSION already built. Skipping rebuild."
        fi
    fi
fi

if [ "$REBUILD_NEEDED" = true ]; then
    echo "📦 Building package..."
    python3 -m build
fi

echo "📦 Looking for latest .whl file in $DIST_DIR..."
WHEEL_FILE=$(ls -t $DIST_DIR/${PACKAGE_NAME}-*.whl | head -n1)

if [ -z "$WHEEL_FILE" ]; then
    echo "❌ No wheel file found. Aborting."
    exit 1
fi

echo "Uninstalling existing package..."
pip uninstall polynx -y

echo "📥 Installing package: $WHEEL_FILE"
pip install "$WHEEL_FILE"

echo "🚀 Running example function test..."
python test_polynx.py

# OPTIONAL: Run your unit tests here
# echo "🧪 Running pytest..."
# pip install pytest
# pytest tests/

echo "🧹 Cleaning up..."
deactivate
#rm -rf "$VENV_DIR"

echo "✅ All tests passed. Ready for upload."
