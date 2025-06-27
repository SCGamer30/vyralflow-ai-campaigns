#!/bin/bash
# Build script for Render deployment

# Set environment variables to prefer binary wheels
export PIP_NO_BUILD_ISOLATION=1
export PIP_PREFER_BINARY=1

# Upgrade pip and install wheel first
pip install --upgrade pip wheel setuptools

# Install specific packages first to avoid dependency conflicts
pip install --only-binary :all: pydantic==2.5.0 || {
    echo "Failed to install pydantic from wheel, trying different version..."
    pip install pydantic==2.4.2
}

# Install all dependencies
pip install --no-cache-dir -r requirements.txt 