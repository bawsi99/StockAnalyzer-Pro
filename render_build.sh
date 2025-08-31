#!/bin/bash
# Custom build script for Render deployment

set -e  # Exit on error

echo "Starting custom build script for Stock Analyzer Pro..."

# Create a requirements file without the problematic packages
echo "Creating modified requirements file..."
grep -v "catboost\|torch\|jupyter\|ipython\|y-py" backend/requirements.txt > requirements_safe.txt

# Install the safe requirements
echo "Installing safe requirements..."
pip install -r requirements_safe.txt

# Install pre-built wheels for PyTorch (CPU only)
echo "Installing PyTorch (CPU only)..."
pip install torch==2.2.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Install CatBoost with no dependencies
echo "Installing CatBoost without dependencies..."
pip install --no-deps catboost==1.2.5

echo "Build completed successfully!"
