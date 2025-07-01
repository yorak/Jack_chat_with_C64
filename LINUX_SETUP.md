# Linux Host Setup Guide

This guide covers setting up your Linux machine to communicate with the C64 LLM chat application.

## Prerequisites

- Ubuntu/Debian-based Linux distribution
- Serial port or USB-to-serial adapter
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

### Install VICE C64 Emulator (Optional)

For testing without real hardware:

```bash
sudo apt install vice
```

**Note:** Ubuntu's VICE package doesn't include the required ROM files (kernal, basic, drive, etc.). You'll need to obtain these separately and configure VICE to use them.

## Virtual Serial Port Setup

For testing and development, you'll need virtual serial ports to connect the C64 emulator and Python bridge.

### Install socat

```bash
sudo apt install socat
```

### Create Virtual Serial Port Pair

Run this command to create two connected virtual serial ports:
```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

This will output something like:
```
2024/01/15 10:23:45 socat[12345] N PTY is /dev/pts/3
2024/01/15 10:23:45 socat[12345] N PTY is /dev/pts/4
```

Note the two device paths - you'll use these for connecting VICE and the Python bridge.

### Test Virtual Ports

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

Install required Python packages:
```bash
pip install pyserial openai  # or your preferred LLM library
```

The Python bridge script (`c64_llm_bridge.py`) handles communication between the C64 and your LLM service. See the included script file for the complete implementation.

### Make Script Executable

```bash
chmod +x c64_llm_bridge.py
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

2. Start VICE with autostart:
   ```bash
   x64sc -autostartprgmode 1 chat.prg
   ```

3. Configure serial emulation in VICE:
   - Go to Settings → I/O Settings → RS232
   - Enable RS232 emulation
   - Set device to one of the virtual ports (e.g., `/dev/pts/3`)
   - Set baud rate to 2400

4. Update the Python bridge script to use the other virtual port (e.g., `/dev/pts/4`)

5. Run the Python bridge script
6. Test the connection

## Troubleshooting

### Serial Port Issues

Check port permissions:
```bash
ls -l /dev/ttyUSB0
```

Should show your user in the dialout group.

### Connection Problems

Monitor serial traffic:
```bash
sudo apt install interceptty
interceptty /dev/ttyUSB0 /tmp/intercept
```

### Python Dependencies

If you get import errors:
```bash
pip install --user pyserial openai
```

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