#include <conio.h>
#include <peekpoke.h>
#include "display.h"

#define SCREEN_WIDTH 40
#define SCREEN_HEIGHT 25
#define CURSOR_CHAR 32
#define CURSOR_COLOR 1

static int cursor_x = 0;
static int cursor_y = 0;
static int cursor_visible = 0;

void display_init(void) {
    clrscr();
    cursor_x = 0;
    cursor_y = 0;
    cursor_visible = 0;
}

void display_char(char c) {
    if (c == '\n' || c == '\r') {
        display_newline();
    } else if (c >= 32 && c <= 126) {
        cputc(c);
        cursor_x++;
        if (cursor_x >= SCREEN_WIDTH) {
            display_newline();
        }
    }
}

void display_string(const char* str) {
    while (*str) {
        display_char(*str++);
    }
}

void display_cursor(int show) {
    cursor_visible = show;
    if (show) {
        gotoxy(cursor_x, cursor_y);
        cputc(CURSOR_CHAR);
        gotoxy(cursor_x, cursor_y);
        revers(1);
        cputc(' ');
        revers(0);
    } else {
        gotoxy(cursor_x, cursor_y);
        cputc(' ');
    }
}

void display_newline(void) {
    cursor_x = 0;
    cursor_y++;
    if (cursor_y >= SCREEN_HEIGHT) {
        cursor_y = SCREEN_HEIGHT - 1;
    }
    gotoxy(cursor_x, cursor_y);
}

void display_clear_screen(void) {
    clrscr();
    cursor_x = 0;
    cursor_y = 0;
}

void display_set_cursor_pos(int x, int y) {
    cursor_x = x;
    cursor_y = y;
    gotoxy(cursor_x, cursor_y);
}

void display_get_cursor_pos(int* x, int* y) {
    *x = cursor_x;
    *y = cursor_y;
}