#!/bin/bash
# Start both servers for the LLM-Judge system
#
# Usage:
#   ./start_servers.sh          # Start both servers
#   ./start_servers.sh tools    # Start only tool server
#   ./start_servers.sh judge    # Start only judge server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

start_tool_server() {
    echo -e "${GREEN}Starting Tool Server on port 8081...${NC}"
    uvicorn src.mcp_server.http_server:app --host 127.0.0.1 --port 8081 &
    TOOL_PID=$!
    echo "Tool Server PID: $TOOL_PID"
    sleep 2
}

start_judge_server() {
    echo -e "${GREEN}Starting Judge Server on port 8080...${NC}"
    uvicorn server:app --host 127.0.0.1 --port 8080 &
    JUDGE_PID=$!
    echo "Judge Server PID: $JUDGE_PID"
}

case "${1:-all}" in
    tools)
        start_tool_server
        wait $TOOL_PID
        ;;
    judge)
        start_judge_server
        wait $JUDGE_PID
        ;;
    all)
        echo -e "${YELLOW}Starting both servers...${NC}"
        echo ""
        start_tool_server
        start_judge_server
        echo ""
        echo -e "${GREEN}Both servers started!${NC}"
        echo "  Tool Server:  http://127.0.0.1:8081"
        echo "  Judge Server: http://127.0.0.1:8080"
        echo ""
        echo "Press Ctrl+C to stop both servers"
        wait
        ;;
    *)
        echo "Usage: $0 [tools|judge|all]"
        exit 1
        ;;
esac
