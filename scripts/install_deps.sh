#!/bin/bash

# Install dependencies properly with build tools

echo "🔧 Installing dependencies with build tools..."

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Upgrade pip and install build tools first
echo "📦 Installing build tools..."
pip install --upgrade pip
pip install setuptools wheel build

# Install dependencies
echo "📥 Installing project dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "Now you can start services with:"
echo "   ./start_all.sh"

