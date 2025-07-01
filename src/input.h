#ifndef INPUT_H
#define INPUT_H

#include "protocol.h"

void input_init(void);
int input_get_line(char* buffer, int max_length);
void input_process_key(char key, char* buffer, int* pos, int* length, int max_length);

#endif