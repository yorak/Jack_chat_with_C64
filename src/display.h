#ifndef DISPLAY_H
#define DISPLAY_H

void display_init(void);
void display_char(char c);
void display_string(const char* str);
void display_cursor(int show);
void display_newline(void);
void display_clear_screen(void);
void display_set_cursor_pos(int x, int y);
void display_get_cursor_pos(int* x, int* y);

#endif