#!/bin/bash
# Build script for Render deployment

# Upgrade pip and install wheel first
pip install --upgrade pip wheel setuptools

# Install all dependencies
pip install --no-cache-dir -r requirements.txt 