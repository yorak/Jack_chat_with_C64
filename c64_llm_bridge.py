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

# Configuration
SERIAL_PORT = "/dev/ttyUSB0"  # Adjust to your port
BAUD_RATE = 2400
HANDSHAKE_STRING = "C64_CHAT_READY"

# Configure your LLM API
openai.api_key = "your-api-key-here"  # Replace with your actual API key

def main():
    """Main communication loop"""
    print("C64 LLM Bridge - Starting...")
    
    try:
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} bps...")
        
        # Wait for C64 handshake
        print("Waiting for C64 to connect...")
        while True:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if HANDSHAKE_STRING in line:
                print("C64 connected!")
                ser.write(b"CONNECTED\r\n")
                ser.flush()
                break
        
        # Main chat loop
        print("Chat session started. Press Ctrl+C to exit.")
        while True:
            try:
                # Read message from C64
                message = ser.readline().decode('ascii', errors='ignore').strip()
                if message:
                    print(f"C64: {message}")
                    
                    # Get LLM response
                    print("Getting LLM response...")
                    response = get_llm_response(message)
                    print(f"LLM: {response}")
                    
                    # Send response to C64 with EOF marker
                    ser.write(response.encode('ascii', errors='ignore'))
                    ser.write(b'\x04')  # EOF character
                    ser.flush()
                    
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Error in chat loop: {e}")
                
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
        print("Check your serial port configuration and permissions.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

def get_llm_response(message):
    """
    Get response from LLM service.
    Replace this function with your preferred LLM implementation.
    """
    try:
        # OpenAI ChatGPT example
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Keep responses concise and under 200 characters when possible."},
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
        
    except openai.error.AuthenticationError:
        return "Error: Invalid API key. Please check your OpenAI configuration."
    except openai.error.RateLimitError:
        return "Error: Rate limit exceeded. Please try again later."
    except openai.error.APIError as e:
        return f"Error: API error - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_ollama_response(message):
    """
    Alternative implementation for local Ollama server.
    Uncomment and modify as needed.
    """
    # import requests
    # 
    # try:
    #     response = requests.post('http://localhost:11434/api/generate', 
    #         json={
    #             'model': 'llama2',
    #             'prompt': message,
    #             'stream': False
    #         })
    #     return response.json()['response']
    # except Exception as e:
    #     return f"Ollama error: {str(e)}"
    pass

def get_anthropic_response(message):
    """
    Alternative implementation for Anthropic Claude.
    Uncomment and modify as needed.
    """
    # import anthropic
    # 
    # client = anthropic.Anthropic(api_key="your-anthropic-key")
    # 
    # try:
    #     response = client.messages.create(
    #         model="claude-3-sonnet-20240229",
    #         max_tokens=200,
    #         messages=[{"role": "user", "content": message}]
    #     )
    #     return response.content[0].text
    # except Exception as e:
    #     return f"Claude error: {str(e)}"
    pass

if __name__ == "__main__":
    main()