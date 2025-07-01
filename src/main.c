#include <conio.h>
#include <stdio.h>
#include <string.h>
#include "protocol.h"
#include "serial.h"
#include "display.h"
#include "input.h"

static char input_buffer[INPUT_BUFFER_SIZE];

void receive_llm_response(void) {
    char c;
    
    while (1) {
        if (serial_data_available()) {
            c = serial_read_char();
            
            if (c == EOF_CHAR) {
                display_newline();
                break;
            }
            
            display_char(c);
        }
    }
}

void send_user_message(const char* message) {
    serial_send_string(message);
    serial_send_char(CR_CHAR);
    serial_send_char(LF_CHAR);
}

int main(void) {
    int message_length;
    int retry_count = 0;
    int delay_count = 0;
    
    display_init();
    serial_init();
    input_init();
    
    display_string("c64 llm chat\n");
    display_string("connecting");
    
    while (1) {
        serial_send_string(HANDSHAKE_STRING);
        display_string(".");
        
        delay_count = 0;
        while (delay_count < 30000) {
            if (serial_data_available()) {
                char c = serial_read_char();
                if (c == 'C' || c == 'c') {
                    display_string(" connected!\n\n");
                    goto connected;
                }
            }
            delay_count++;
        }
    }
    
connected:
    while (1) {
        receive_llm_response();
        
        message_length = input_get_line(input_buffer, INPUT_BUFFER_SIZE);
        
        if (message_length > 0) {
            send_user_message(input_buffer);
        }
    }
    
    return 0;
}