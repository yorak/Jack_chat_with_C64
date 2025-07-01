CC = cl65
TARGET = c64
PROGRAM = chat

SRCDIR = src

SOURCES = $(SRCDIR)/main.c $(SRCDIR)/serial.c $(SRCDIR)/display.c $(SRCDIR)/input.c

CFLAGS = -t $(TARGET) -O

.PHONY: all clean

all: $(PROGRAM).prg

$(PROGRAM).prg: $(SOURCES) | build
	$(CC) $(CFLAGS) -o $@ $(SOURCES)
	mv $(SRCDIR)/*.o build/ 2>/dev/null || true

build:
	mkdir -p build

clean:
	rm -f $(SRCDIR)/*.o build/*.o $(PROGRAM).prg chat.d64

install: $(PROGRAM).prg
	cp $(PROGRAM).prg /tmp/

disk: $(PROGRAM).prg
	c1541 -format diskname,id d64 chat.d64 -attach chat.d64 -write chat.prg chat

.PHONY: install disk