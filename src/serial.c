#include <conio.h>
#include <peekpoke.h>
#include "serial.h"

#define ACIA_DATA    0xDE08
#define ACIA_STATUS  0xDE09
#define ACIA_COMMAND 0xDE0A
#define ACIA_CONTROL 0xDE0B

#define STATUS_TX_EMPTY 0x10
#define STATUS_RX_FULL  0x08

void serial_init(void) {
    POKE(ACIA_CONTROL, 0x1F);
    POKE(ACIA_COMMAND, 0x09);
}

void serial_send_char(char c) {
    while (!(PEEK(ACIA_STATUS) & STATUS_TX_EMPTY)) {
    }
    POKE(ACIA_DATA, c);
}

void serial_send_string(const char* str) {
    while (*str) {
        serial_send_char(*str++);
    }
}

char serial_read_char(void) {
    while (!(PEEK(ACIA_STATUS) & STATUS_RX_FULL)) {
    }
    return PEEK(ACIA_DATA);
}

int serial_data_available(void) {
    return (PEEK(ACIA_STATUS) & STATUS_RX_FULL) ? 1 : 0;
}

void serial_handshake(void) {
    serial_send_string(HANDSHAKE_STRING);
    
    while (1) {
        char c = serial_read_char();
        if (c == 'C') {
            break;
        }
    }
}