#!/bin/bash

# C64 LLM Chat Launcher Script
# Automatically sets up serial ports, starts Python bridge, and launches VICE

set -e

# Default values
SYSTEM_PROMPT=""
VICE_DELAY=3
DEBUG=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Automatically sets up serial loopback, starts Python bridge, and launches VICE C64 emulator"
    echo ""
    echo "OPTIONS:"
    echo "  -p, --prompt FILE     System prompt file for LLM"
    echo "  -d, --delay SEC       Delay before starting VICE (default: 3)"
    echo "  --debug               Enable debug output"
    echo "  -h, --help            Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                              # Basic usage"
    echo "  $0 -p prompts/system_prompt.txt # With custom system prompt"
    echo ""
    exit 0
}

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

cleanup() {
    log "Cleaning up..."
    
    # Kill socat if running
    if [[ -n "$SOCAT_PID" ]]; then
        kill $SOCAT_PID 2>/dev/null || true
        log "Stopped socat (PID: $SOCAT_PID)"
    fi
    
    # Kill Python bridge if running
    if [[ -n "$PYTHON_PID" ]]; then
        kill $PYTHON_PID 2>/dev/null || true
        log "Stopped Python bridge (PID: $PYTHON_PID)"
    fi
    
    # Kill VICE if running
    if [[ -n "$VICE_PID" ]]; then
        kill $VICE_PID 2>/dev/null || true
        log "Stopped VICE (PID: $VICE_PID)"
    fi
    
    log "Cleanup complete"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--prompt)
            SYSTEM_PROMPT="$2"
            shift 2
            ;;
        -d|--delay)
            VICE_DELAY="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Check prerequisites
log "Checking prerequisites..."

if ! command -v socat &> /dev/null; then
    error "socat not found. Install with: sudo apt install socat"
fi

if ! command -v x64sc &> /dev/null; then
    error "VICE (x64sc) not found. Install with: sudo apt install vice"
fi

if [[ ! -f "c64_llm_bridge.py" ]]; then
    error "c64_llm_bridge.py not found in current directory"
fi

if [[ ! -f "chatbas.prg" ]]; then
    error "chatbas.prg not found. Create it with: petcat -w2 -o chatbas.prg -- chat.bas"
fi

if [[ -n "$SYSTEM_PROMPT" && ! -f "$SYSTEM_PROMPT" ]]; then
    error "System prompt file not found: $SYSTEM_PROMPT"
fi

success "All prerequisites found"

# Create virtual serial ports and capture output
log "Creating virtual serial ports..."
SOCAT_LOG=$(mktemp)

# Start socat in background and capture its debug output
socat -d -d pty,raw,echo=0,clocal=1 pty,raw,echo=0,clocal=1 2>"$SOCAT_LOG" &
SOCAT_PID=$!

# Wait for socat to create the PTYs
sleep 1

# Parse the PTY paths from socat output
PTY1=$(grep "N PTY is" "$SOCAT_LOG" | head -n1 | awk '{print $NF}')
PTY2=$(grep "N PTY is" "$SOCAT_LOG" | tail -n1 | awk '{print $NF}')

if [[ -z "$PTY1" || -z "$PTY2" ]]; then
    error "Failed to detect PTY paths from socat output"
fi

success "Created virtual serial ports: $PTY1 <-> $PTY2"

# Start Python bridge
log "Starting Python LLM bridge on $PTY2..."
PYTHON_ARGS=("$PTY2")

if [[ -n "$SYSTEM_PROMPT" ]]; then
    PYTHON_ARGS+=("--system-prompt" "$SYSTEM_PROMPT")
fi

if [[ $DEBUG == true ]]; then
    PYTHON_ARGS+=("--debug")
fi

python3 c64_llm_bridge.py "${PYTHON_ARGS[@]}" &
PYTHON_PID=$!

success "Python bridge started (PID: $PYTHON_PID)"

# Wait for Python bridge to initialize
log "Waiting ${VICE_DELAY}s for Python bridge to initialize..."
sleep $VICE_DELAY

# Start VICE with the C64 program
log "Starting VICE C64 emulator with chatbas.prg..."
x64sc -rsuser -rsdev1 "$PTY1" -rsuserbaud 1200 -autostartprgmode 1 chatbas.prg &
VICE_PID=$!

success "VICE started (PID: $VICE_PID)"
log "Serial connection: VICE ($PTY1) <-> Python Bridge ($PTY2)"

if [[ -n "$SYSTEM_PROMPT" ]]; then
    log "Using system prompt: $SYSTEM_PROMPT"
fi

log "C64 LLM Chat is running!"
log "Press Ctrl+C to stop all processes"

# Wait for VICE to exit
wait $VICE_PID
log "VICE exited"

# Clean up temp file
rm -f "$SOCAT_LOG"