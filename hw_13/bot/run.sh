#!/bin/bash

# Linux Command Bot Startup Script

echo "Starting Linux Command Bot..."

# Navigate to the root directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r bot/requirements.txt

# Run bot
echo "Launching bot..."
python3 -m bot.telegram_bot
