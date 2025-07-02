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

Compile the C64 program:

```bash
cl65 -t c64 -o chat.prg main.c serial.c display.c input.c
```

## Testing Setup

### With Real C64

1. Connect C64 serial port to your Linux machine
2. Load `chat.prg` on your C64
3. Run the Python bridge script: `./c64_llm_bridge.py`
4. Run the C64 program
5. Start chatting!

### With VICE Emulator

1. Start the virtual serial ports:
   ```bash
   socat -d -d pty,raw,echo=0 pty,raw,echo=0
   ```
   Note the two device paths (e.g., `/dev/pts/3` and `/dev/pts/4`)

2. Start VICE with serial configuration:
   ```bash
   x64sc -rsuser1 /dev/pts/3 -rsuserbaud 1200 chat.bas
   ```
   
   Or manually:
   ```bash
   x64sc
   ```
   Then configure serial emulation in VICE:
   - Go to Settings → I/O Settings → RS232
   - Enable RS232 emulation  
   - Set device to one of the virtual ports (e.g., `/dev/pts/3`)
   - Set baud rate to 1200
   - Paste the .bas code to emulated C64 Basic prompt
   - Write `RUN` to code to emulated C64 Basic prompt

3. Run the Python bridge script with the other virtual port:
   ```bash
   ./c64_llm_bridge.py /dev/pts/4
   ```
   
   Or with custom options:
   ```bash
   ./c64_llm_bridge.py /dev/pts/4 --system-prompt c64_prompt.txt --timeout 5
   ```

4. Test the connection

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
