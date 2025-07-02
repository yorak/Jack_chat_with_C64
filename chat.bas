05 rem ## indicate program is running ##
10 print chr$(147);
20 print chr$(18);: rem reverse on
25 print "it is eerily quiet ";
30 print chr$(146);: rem reverse off
35 rem ## try to initiate serial conn ##
40 open 5,2,1,chr$(8)
45 print#5,"<c64-chat-ready>"
50 rem wait approximately 3 seconds
55 for i=1 to 1800: next i
60 get#5,a$: if a$=chr$(6) then print : goto 80
65 print ".";
70 goto 45
80 rem ## main chat loop ##
90 get#5,a$
100 if a$<>"" then print chr$(5);a$;chr$(156);
110 if a$=chr$(4) then print : print chr$(159);: goto 130
120 goto 90
130 rem input mode
140 input msg$
150 if msg$<>"" then print#5,"<c64-chat-msg>";msg$
160 goto 90

