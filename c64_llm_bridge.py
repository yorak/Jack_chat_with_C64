#!/usr/bin/env python3
"""
C64 LLM Bridge Script

This script acts as a bridge between the C64 chat application and LLM services.
It handles the serial communication protocol and forwards messages to your
preferred LLM API.
"""

import serial
import time
import openai  # or your preferred LLM library
import sys
import os
import argparse
from dotenv import load_dotenv

# ANSI color codes for debug output
class Colors:
    RED = '\033[91m'      # Serial incoming
    GREEN = '\033[92m'    # Serial outgoing  
    YELLOW = '\033[93m'   # LLM request
    BLUE = '\033[94m'     # LLM response
    MAGENTA = '\033[95m'  # System messages
    CYAN = '\033[96m'     # Debug info
    WHITE = '\033[97m'    # Normal text
    RESET = '\033[0m'     # Reset color

def debug_print(message, color=Colors.WHITE):
    print(f"{color}{message}{Colors.RESET}")

def debug_serial_in(data):
    debug_print(f"[SERIAL IN] {repr(data)}", Colors.RED)

def debug_serial_out(data):
    debug_print(f"[SERIAL OUT] {repr(data)}", Colors.GREEN)

def debug_llm_request(message):
    debug_print(f"[LLM REQUEST] {message}", Colors.YELLOW)

def debug_llm_response(response):
    debug_print(f"[LLM RESPONSE] {response}", Colors.BLUE)

def debug_system(message):
    debug_print(f"[SYSTEM] {message}", Colors.MAGENTA)

# Configuration
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 1200
HANDSHAKE_STRING = "<C64-CHAT-READY>"
NEW_INPUT_STRING = "<C64-CHAT-MSG>"
ACK_C64 = b"\x06"  # ASCII ACK character
EOM_C64 = b"\x04"  # ASCII EOF character
REPEAT_ACK_TIMES = 6
IDLE_TIMEOUT_SECONDS = 3  # Send auto-message after this many seconds of silence
CONFIG_FILE = ".c64_llm_config"


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="C64 LLM Bridge - Serial communication bridge between C64 and LLM services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Use default serial port
  %(prog)s /dev/pts/4                   # Use specific serial port
  %(prog)s -p /dev/pts/4 -s prompt.txt # Use custom port and system prompt
  %(prog)s --timeout 5 --baud 2400     # Custom timeout and baud rate

Environment Variables:
  OPENAI_API_KEY     - OpenAI API key (required)
  SYSTEM_PROMPT_FILE - Default system prompt file path
        """
    )
    
    parser.add_argument('port', nargs='?', default=DEFAULT_SERIAL_PORT,
                        help=f'Serial port to use (default: {DEFAULT_SERIAL_PORT})')
    parser.add_argument('-p', '--port', dest='port_override', 
                        help='Serial port (alternative to positional argument)')
    parser.add_argument('-s', '--system-prompt', dest='system_prompt_file',
                        help='Path to system prompt file')
    parser.add_argument('-b', '--baud', type=int, default=BAUD_RATE,
                        help=f'Baud rate (default: {BAUD_RATE})')
    parser.add_argument('-t', '--timeout', type=float, default=IDLE_TIMEOUT_SECONDS,
                        help=f'Idle timeout in seconds (default: {IDLE_TIMEOUT_SECONDS})')
    parser.add_argument('--no-auto-message', action='store_true',
                        help='Disable automatic greeting after timeout')
    parser.add_argument('--debug', action='store_true',
                        help='Enable verbose debug output')
    
    args = parser.parse_args()
    
    # Handle port override
    if args.port_override:
        args.port = args.port_override
    
    return args

def load_system_prompt(system_prompt_file=None):
    """Load system prompt from file if specified"""
    # Command line argument takes precedence over environment variable
    if not system_prompt_file:
        system_prompt_file = os.getenv('SYSTEM_PROMPT_FILE')
    
    if system_prompt_file:
        if not os.path.exists(system_prompt_file):
            print(f"Error: System prompt file '{system_prompt_file}' not found.")
            sys.exit(1)
        
        try:
            with open(system_prompt_file, 'r') as f:
                prompt = f.read().strip()
                if not prompt:
                    print(f"Error: System prompt file '{system_prompt_file}' is empty.")
                    sys.exit(1)
                debug_system(f"Loaded system prompt from {system_prompt_file}")
                return prompt
        except Exception as e:
            print(f"Error reading system prompt file '{system_prompt_file}': {e}")
            sys.exit(1)
    
    # Default system prompt
    return "You are a helpful assistant. Keep responses concise and under 200 characters when possible."

def setup_openai():
    """Setup OpenAI API key from environment"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        debug_system("ERROR: OPENAI_API_KEY not found in environment")
        debug_system("Please create .env file with your API key")
        return False
    
    openai.api_key = api_key
    debug_system("OpenAI API key loaded from environment")
    return True

def main():
    """Main communication loop"""
    debug_system("C64 LLM Bridge - Starting...")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Load environment variables
    load_dotenv()
    debug_system("Environment variables loaded with python-dotenv")
    
    # Setup OpenAI API
    if not setup_openai():
        return 1
    
    debug_system(f"Using serial port: {args.port}")
    debug_system(f"Baud rate: {args.baud}")
    debug_system(f"Idle timeout: {args.timeout} seconds")
    
    try:
        # Open serial connection with minimal buffering
        ser = serial.Serial(
            port=args.port, 
            baudrate=args.baud, 
            timeout=0.1,
            write_timeout=0.1,
            inter_byte_timeout=0.1
        )
        # Disable input/output buffering
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        debug_system(f"Listening on {args.port} at {args.baud} bps...")
        
        # Chat history and system prompt
        system_prompt = load_system_prompt(args.system_prompt_file)
        chat_history = [{"role": "system", "content": system_prompt}]
        debug_system(f"System prompt: {system_prompt[:100]}{'...' if len(system_prompt) > 100 else ''}")
        
        # Main loop (waiting for handshake, then handling chat messages)
        debug_system("Waiting for C64 to connect...")
        chat_buffer = ""
        last_message_time = time.time()
        auto_message_sent = False
        auto_message_inserted = False
        handshake_completed = False  # Track if handshake was already processed
        

        
        while True:
            try:
                # Check for handshake string - always process it to allow reconnection
                if HANDSHAKE_STRING in chat_buffer:
                    handshake_completed = False
                    debug_system("C64 connected!")
                    # Send ACK
                    time.sleep(0.2)
                    for i in range(REPEAT_ACK_TIMES):
                        response = ACK_C64
                        debug_serial_out(response)
                        ser.write(response)
                        ser.flush()
                        time.sleep(0.33)
                        
                    debug_system("Chat session (re)started. Press Ctrl+C to exit.")
                    last_message_time = time.time()
                    auto_message_sent = False
                    handshake_completed = True
                    # Reset chat history on handshake
                    chat_history = [{"role": "system", "content": system_prompt}]
                    debug_system("Chat history reset")
                    chat_buffer = ""
                    continue
                
                # Read available data character by character
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
                    # Debug output for each character as it arrives
                    for char in data:
                        debug_print(f"[CHAR IN] {repr(char)} (0x{ord(char):02x})", Colors.CYAN)
                    chat_buffer += data
                    
                # Check for complete message (wait for \r)
                if '\r' in chat_buffer:
                    message = chat_buffer.strip()
                    if message:
                        if NEW_INPUT_STRING in message:
                            if not auto_message_inserted:
                                debug_serial_in(f"Complete message: {repr(message)}")
                            else:
                                auto_message_inserted = False
                                
                            message = message.replace(NEW_INPUT_STRING,"")                   
                            
                            # Add user message to chat history
                            chat_history.append({"role": "user", "content": message})
                            
                            # Get streaming LLM response with history
                            debug_system("Getting streaming LLM response...")
                            debug_llm_request(message)
                            response = stream_llm_response_with_history(chat_history, ser)
                            debug_llm_response(response)
                            
                            # Add assistant response to chat history
                            chat_history.append({"role": "assistant", "content": response})
                            
                            # Send EOF marker after streaming is complete
                            debug_serial_out(EOM_C64)
                            ser.write(EOM_C64)  # EOF character
                            ser.flush()
                        else:
                            debug_serial_in(f"Discarding malformed input: {repr(message)}")
                    
                    chat_buffer = ""
                
                # Check for idle timeout and inject auto-message if needed (only after handshake)
                current_time = time.time()
                if (not args.no_auto_message and handshake_completed and not auto_message_sent and 
                    current_time - last_message_time > args.timeout):
                    
                    debug_system(f"No message for {args.timeout} seconds - injecting auto-message")                    
                    # Inject auto-prompt into chat_buffer to be processed by existing logic
                    auto_prompt = NEW_INPUT_STRING + "Say a brief, friendly greeting to start a conversation. Keep it under 50 characters."
                    chat_buffer = auto_prompt + "\r"
                    auto_message_sent = True
                    auto_message_inserted = True
                    continue

                
                time.sleep(0.01)  # Prevent busy waiting
                    
            except KeyboardInterrupt:
                debug_system("Shutting down...")
                break
            except Exception as e:
                debug_system(f"Error in chat loop: {e}")
                import traceback
                traceback.print_exc()
                
    except serial.SerialException as e:
        debug_system(f"Serial port error: {e}")
        debug_system("Check your serial port configuration and permissions.")
    except Exception as e:
        debug_system(f"Unexpected error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()
            debug_system("Serial port closed.")

def stream_llm_response_with_history(chat_history, serial_port):
    """
    Stream response from LLM service with full chat history, sending words as they arrive.
    """
    try:
        # OpenAI ChatGPT streaming example with history
        response_stream = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            max_tokens=200,
            temperature=0.7,
            stream=True
        )
        
        full_response = ""
        current_word = ""
        
        for chunk in response_stream:
            if chunk.choices[0].delta.get('content'):
                content = chunk.choices[0].delta.content
                full_response += content
                
                # Process character by character
                for char in content:
                    if char.isspace():  # Space, newline, tab, etc.
                        if current_word:
                            # Send the complete word
                            word_bytes = current_word.upper().encode('ascii', errors='ignore')
                            debug_serial_out(word_bytes)
                            serial_port.write(word_bytes)
                            serial_port.flush()
                            current_word = ""
                        
                        # Send the space/whitespace
                        space_byte = char.upper().encode('ascii', errors='ignore')
                        debug_serial_out(space_byte)
                        serial_port.write(space_byte)
                        serial_port.flush()
                        
                        # Small delay between words for C64 processing
                        time.sleep(0.1)
                    else:
                        current_word += char
        
        # Send any remaining word
        if current_word:
            word_bytes = current_word.upper().encode('ascii', errors='ignore')
            debug_serial_out(word_bytes)
            serial_port.write(word_bytes)
            serial_port.flush()
        
        return full_response.strip().upper()
        
    except openai.error.AuthenticationError:
        error_msg = "Error: Invalid API key. Please check your OpenAI configuration."
        serial_port.write(error_msg.encode('ascii', errors='ignore'))
        return error_msg
    except openai.error.RateLimitError:
        error_msg = "Error: Rate limit exceeded. Please try again later."
        serial_port.write(error_msg.encode('ascii', errors='ignore'))
        return error_msg
    except openai.error.APIError as e:
        error_msg = f"Error: API error - {str(e)}"
        serial_port.write(error_msg.encode('ascii', errors='ignore'))
        return error_msg
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        serial_port.write(error_msg.encode('ascii', errors='ignore'))
        return error_msg

if __name__ == "__main__":
    sys.exit(main() or 0)
