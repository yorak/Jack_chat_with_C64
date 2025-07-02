# Linux Host Setup Guide

This guide covers setting up your Linux machine to communicate with the emulated C64 LLM chat application.

## Prerequisites

- Ubuntu/Debian-based Linux distribution
- Python 3.x installed

## Install Development Tools

### Install CC65 Cross-Compiler

```bash
sudo apt update
sudo apt install cc65
```

Verify installation:
```bash
cl65 --version
```

### Install VICE C64 Emulator

For testing without real hardware:

```bash
sudo apt install vice
```

**Note:** Ubuntu's VICE package doesn't include the required ROM files (kernal, basic, drive, etc.). You'll need to obtain these separately and configure VICE to use them and/or set symbolic links with names VICE expects.

## Virtual Serial Port Setup

For testing and development, you'll need virtual serial ports to connect the C64 emulator and Python bridge.

### Install socat

```bash
sudo apt install socat
```

### Create Virtual Serial Port Pair

Run this command to create two connected virtual serial ports:
```bash
socat -d -d pty,raw,echo=0,clocal=1 pty,raw,echo=0,clocal=1
```

This will output something like:
```
2024/01/15 10:23:45 socat[12345] N PTY is /dev/pts/3
2024/01/15 10:23:45 socat[12345] N PTY is /dev/pts/4
```

Note the two device paths - you'll use these for connecting VICE and the Python bridge.

### Test Virtual Ports (Optional)

Open two terminals and test the connection:
- Terminal 1: `screen /dev/pts/3 2400`
- Terminal 2: `screen /dev/pts/4 2400`

Type in one terminal - it should appear in the other. Press `Ctrl+A` then `K` to exit screen.

### For Real Hardware

If using actual C64 hardware, you'll need:
- Physical serial cable connection
- Add your user to dialout group: `sudo usermod -a -G dialout $USER`
- Use actual serial device like `/dev/ttyUSB0`

## Python LLM Bridge Script

### Create Virtual Environment (Recommended)

Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install required Python packages:
```bash
pip install -r requirements.txt
```

The Python bridge script (`c64_llm_bridge.py`) handles communication between the C64 and your LLM service.

### Configure API Key

Copy the example environment file and add your API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Make Script Executable

```bash
chmod +x c64_llm_bridge.py
chmod +x run_c64_chat.sh
```

### Activate Virtual Environment

Before running the scripts, activate the virtual environment:

```bash
source venv/bin/activate
```

Alternatively, install the requirements globally (not recommended):

```bash
pip install -r requirements.txt
```

### Usage

#### Basic Usage

Run with default settings:
```bash
./c64_llm_bridge.py
```

Specify serial port:
```bash
./c64_llm_bridge.py /dev/pts/4
# or
./c64_llm_bridge.py --port /dev/pts/4
```

#### Advanced Options

Custom system prompt:
```bash
./c64_llm_bridge.py --system-prompt system_prompt.txt
```

Custom baud rate and timeout:
```bash
./c64_llm_bridge.py --baud 2400 --timeout 5
```

Disable automatic greeting:
```bash
./c64_llm_bridge.py --no-auto-message
```

Combined options:
```bash
./c64_llm_bridge.py /dev/pts/4 -s system_prompt.txt -b 1200 -t 3
```

#### Available Command Line Options

- **Serial port**: Positional argument or `-p/--port`
- **`-s/--system-prompt`**: Path to custom system prompt file
- **`-b/--baud`**: Baud rate (default: 1200)
- **`-t/--timeout`**: Idle timeout in seconds (default: 3)
- **`--no-auto-message`**: Disable automatic greeting after timeout
- **`--debug`**: Enable verbose debug output
- **`-h/--help`**: Show detailed help with examples

#### Get Help

View all available options:
```bash
./c64_llm_bridge.py --help
```

## Building the C64 Application

Convert the BASIC program to PRG format:

```bash
petcat -w2 -o chatbas.prg -- chat.bas
```

### Creating a Disk Image (Optional)

For real hardware or disk-based emulation:

```bash
c1541 -format "chat disk",cd d64 chat.d64 -attach chat.d64 -write chatbas.prg chat
```

## Testing Setup

### With Real C64

1. Connect C64 serial port to your Linux machine
2. Load `chat.prg` on your C64
3. Run the Python bridge script: `./c64_llm_bridge.py`
4. Run the C64 program
5. Start chatting!

### With VICE Emulator

#### Manual Setup

1. Start the virtual serial ports:
   ```bash
   socat -d -d pty,raw,echo=0,clocal=1 pty,raw,echo=0,clocal=1
   ```
   Note the two device paths (e.g., `/dev/pts/3` and `/dev/pts/4`)

2. Run the Python bridge script with one virtual port:
   ```bash
   ./c64_llm_bridge.py /dev/pts/4
   ```
   
   Or with custom options:
   ```bash
   ./c64_llm_bridge.py /dev/pts/4 --system-prompt prompts/system_prompt.txt --timeout 5
   ```

3. Start VICE with the other virtual port (in another terminal):
   ```bash
   x64sc -rsuser -rsdev1 /dev/pts/3 -rsuserbaud 1200 -autostartprgmode 1 chatbas.prg
   ```

4. Test the connection

## Automated Setup (Recommended)

For convenience, use the provided launcher script that handles everything automatically.

**Important:** Activate the virtual environment first:

```bash
source venv/bin/activate
```

Then run the launcher:

```bash
# Basic usage - sets up ports, starts bridge, launches VICE
./run_c64_chat.sh

# With custom system prompt
./run_c64_chat.sh --prompt prompts/system_prompt.txt

# Get help
./run_c64_chat.sh --help
```

The launcher script:
- Creates virtual serial ports with socat
- Starts the Python bridge automatically
- Launches VICE with the correct configuration
- Handles cleanup when you exit

## Alternative LLM Services

The bridge script can be adapted for other LLM services:

- **Ollama**: Replace OpenAI calls with local Ollama API
- **Anthropic Claude**: Use the Anthropic Python SDK
- **Google Gemini**: Use the Google AI SDK
- **Local models**: Connect to local inference servers

## Performance Tips

- Use shorter system prompts to reduce response time
- Set reasonable token limits (100-200 tokens work well)
- Consider using streaming responses for longer texts
- Buffer responses to handle C64's slower processing
