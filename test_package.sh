#!/bin/bash

set -e  # Exit on error
set -o pipefail

PACKAGE_NAME="polynx"
DIST_DIR="dist"
VENV_DIR="../venv"

echo "🔧 Creating virtual environment..."
#python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

#echo "⬆️  Upgrading pip, setuptools, and wheel..."
#pip install --upgrade pip setuptools wheel

if [ ! -d "$DIST_DIR" ]; then
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
