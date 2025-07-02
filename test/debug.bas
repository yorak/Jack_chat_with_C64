10 print chr$(147);
20 print "serial debug test"
30 open 5,2,1,chr$(8)
40 rem main loop
50 print#5,"<c64-chat-ready>"
60 print "sent: test message"
90 rem check for any received data
100 get#5,a$
110 if a$<>"" then print "received: ";a$;" (";asc(a$);")"
120 goto 100
