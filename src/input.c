#include <conio.h>
#include <string.h>
#include "input.h"
#include "display.h"

void input_init(void) {
}

int input_get_line(char* buffer, int max_length) {
    int pos = 0;
    int length = 0;
    char key;
    
    buffer[0] = '\0';
    display_cursor(1);
    
    while (1) {
        if (kbhit()) {
            key = cgetc();
            
            if (key == CR_CHAR) {
                buffer[length] = '\0';
                display_cursor(0);
                display_newline();
                return length;
            }
            
            input_process_key(key, buffer, &pos, &length, max_length - 1);
        }
    }
}

void input_process_key(char key, char* buffer, int* pos, int* length, int max_length) {
    int i;
    int cursor_x, cursor_y;
    
    display_get_cursor_pos(&cursor_x, &cursor_y);
    
    if (key == BACKSPACE_CHAR || key == DELETE_CHAR) {
        if (*pos > 0) {
            (*pos)--;
            (*length)--;
            
            for (i = *pos; i < *length; i++) {
                buffer[i] = buffer[i + 1];
            }
            buffer[*length] = '\0';
            
            display_cursor(0);
            gotoxy(cursor_x - (*length - *pos + 1), cursor_y);
            display_string(&buffer[*pos]);
            cputc(' ');
            gotoxy(cursor_x - 1, cursor_y);
            display_cursor(1);
        }
    }
    else if (key == 29) {
        if (*pos < *length) {
            (*pos)++;
            gotoxy(cursor_x + 1, cursor_y);
        }
    }
    else if (key == 157) {
        if (*pos > 0) {
            (*pos)--;
            gotoxy(cursor_x - 1, cursor_y);
        }
    }
    else if (key >= 32 && key <= 126 && *length < max_length) {
        for (i = *length; i > *pos; i--) {
            buffer[i] = buffer[i - 1];
        }
        buffer[*pos] = key;
        (*pos)++;
        (*length)++;
        buffer[*length] = '\0';
        
        display_cursor(0);
        display_string(&buffer[*pos - 1]);
        gotoxy(cursor_x + 1, cursor_y);
        display_cursor(1);
    }
}