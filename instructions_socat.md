You can create virtual serial ports using `socat`. This tool creates a bidirectional data relay between two endpoints.

Install socat:
```bash
sudo apt install socat
```

Create the virtual serial port pair:
```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

This will output something like:
```
2024/01/15 10:23:45 socat[12345] N PTY is /dev/pts/3
2024/01/15 10:23:45 socat[12345] N PTY is /dev/pts/4
```

Now you can connect to these ports:
- Terminal 1: `screen /dev/pts/3 9600`
- Terminal 2: `screen /dev/pts/4 9600`

Whatever you type in one terminal will appear in the other.

Note: The `-d -d` flags provide debug output showing the created PTY devices. You can remove them once you verify it works. The `raw` option disables terminal processing, and `echo=0` prevents local echo.
