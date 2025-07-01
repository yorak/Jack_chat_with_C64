#ifndef SERIAL_H
#define SERIAL_H

#include "protocol.h"

void serial_init(void);
void serial_send_char(char c);
void serial_send_string(const char* str);
char serial_read_char(void);
int serial_data_available(void);
void serial_handshake(void);

#endif