# C64 LLM Chat Console

A Commodore 64 application written that enables real-time chat communication with Large Language Models (LLMs) over hardware serial connection.

## Overview

This application transforms your C64 into a terminal for chatting with modern AI assistants. It uses the built-in serial port to communicate at 1200 bps with a host computer running an LLM interface.

## Features

- **Serial Communication**: 1200 bps serial connection via C64's built-in UART
- **Real-time Display**: Shows LLM responses character-by-character as they arrive
- **BASIC-style Input**: Inline editing with blinking cursor, just like C64 BASIC
- **Protocol Handshake**: Sends identification string on startup
- **Flow Control**: Handles end-of-transmission and message boundaries properly
- **Seamless Chat**: No prefixes or labels - pure conversational flow

## Hardware Requirements

- Commodore 64 with working serial port (or emulate it)
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

- **Baud Rate**: 1200 bps
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Flow Control**: None (software controlled)

## Building

This version uses C64 BASIC - no compilation needed!

### Converting BASIC to PRG Format

To convert the BASIC text file to a C64 program file:

```bash
petcat -w2 -o chatbas.prg -- chat.bas
```

### For Emulation (Recommended)

The PRG format is convenient for emulation as it can be run directly:

```bash
x64sc -autostartprgmode 1 chatbas.prg
```

### For Real Hardware or Disk-based Emulation

To create a .d64 disk image with the BASIC program:

```bash
c1541 -format "chat disk",cd d64 chat.d64 -attach chat.d64 -write chatbas.prg chat
```

## Usage

1. Load the program: `LOAD "CHAT",8`
2. Connect serial cable to host computer  
3. Run: `RUN`
4. Wait for "CONNECTED" message (dots appear while connecting)
5. LLM responses appear directly on screen
6. After LLM finishes (EOF), type your message and press RETURN
7. Continue the conversation

The experience feels like having a conversation directly in BASIC, with the AI's words appearing naturally followed by your familiar BASIC prompt.

## File Structure

- `chat.bas` - BASIC program for C64 LLM communication
- `c64_llm_bridge.py` - Python bridge script for LLM communication  
- `LINUX_SETUP.md` - Linux host setup instructions
- `instructions_socat.md` - Virtual serial port setup

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
