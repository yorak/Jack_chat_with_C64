# C64 LLM Chat Console

A Commodore 64 application written in C that enables real-time chat communication with Large Language Models (LLMs) over hardware serial connection.

## Overview

This application transforms your C64 into a terminal for chatting with modern AI assistants. It uses the built-in serial port to communicate at 2400 bps with a host computer running an LLM interface.

## Features

- **Serial Communication**: 2400 bps serial connection via C64's built-in UART
- **Real-time Display**: Shows LLM responses character-by-character as they arrive
- **BASIC-style Input**: Inline editing with blinking cursor, just like C64 BASIC
- **Protocol Handshake**: Sends identification string on startup
- **Flow Control**: Handles EOF and message boundaries properly
- **Seamless Chat**: No prefixes or labels - pure conversational flow

## Hardware Requirements

- Commodore 64 with working serial port
- Serial cable (DB-25 or appropriate adapter)
- Host computer with serial port or USB-to-serial adapter
- Null modem cable if connecting directly between computers

## Protocol

### Startup Sequence
1. C64 application sends identification string: `"C64_CHAT_READY\r\n"`
2. Waits for acknowledgment from host
3. Enters chat mode

### Chat Flow
1. **Receive Mode**: Display incoming characters from LLM response directly to screen
2. **End Detection**: Stops on EOF, adds extra newline, shows blinking cursor
3. **Input Mode**: BASIC-style line editing with cursor movement and backspace
4. **Send**: Transmits user message on RETURN and continues conversation

## Serial Configuration

- **Baud Rate**: 2400 bps
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Flow Control**: None (software controlled)

## Building

Requires CC65 compiler suite:

```bash
make
```

Or manually:
```bash
cl65 -t c64 -o chat.prg main.c serial.c display.c input.c
```

### Creating a Disk Image

To create a .d64 disk image for use with VICE or real hardware:

```bash
make disk
```

This creates `chat.d64` with the program file ready to load.

## Usage

1. Load the program: `LOAD "CHAT.PRG",8,1`
2. Connect serial cable to host computer
3. Run: `RUN`
4. Wait for "CONNECTED" message
5. LLM responses appear directly on screen
6. After LLM finishes (extra newline + blinking cursor), type and edit your message
7. Press RETURN to send and continue the conversation

The experience feels like having a conversation directly in BASIC, with the AI's words appearing naturally followed by your familiar blinking cursor prompt.

## File Structure

- `main.c` - Main program loop and initialization
- `serial.c` - Serial communication routines
- `display.c` - Screen output and cursor management
- `input.c` - BASIC-style line input with editing
- `protocol.h` - Communication protocol definitions

## Host Computer Setup

The host computer needs:
- Serial port configured for 2400 bps, 8N1
- LLM interface software (Python script, etc.)
- Proper handling of the C64's identification string

## Limitations

- Maximum message length: 1000 characters
- No file transfer capabilities
- Text-only communication
- Requires stable serial connection

## Future Enhancements

- Support for higher baud rates (9600 bps)
- Message history buffer
- Configuration save/load
- Status indicators
- Error recovery mechanisms
