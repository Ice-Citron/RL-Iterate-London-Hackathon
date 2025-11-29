#!/bin/bash
# Start Training Script
# Usage: ./scripts/start_training.sh [dev|h100|tiny]

set -e

CONFIG=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "Security Agent RLAIF Training"
echo "=============================================="
echo "Config: $CONFIG"
echo "Project: $PROJECT_DIR"
echo ""

# Check environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not set"
    echo "Please set it in your environment or .env file"
    exit 1
fi

# Check if judge server is running
echo "Checking judge server..."
if ! curl -s http://localhost:8088/health > /dev/null 2>&1; then
    echo "Judge server not running!"
    echo ""
    echo "Start it in another terminal with:"
    echo "  cd $PROJECT_DIR"
    echo "  uvicorn server:app --host 127.0.0.1 --port 8088"
    echo ""
    exit 1
fi
echo "Judge server: OK"

# Run training
echo ""
echo "Starting training with config: $CONFIG"
echo "=============================================="

cd "$PROJECT_DIR"
python -m src.training.orchestrator --config "$CONFIG"
