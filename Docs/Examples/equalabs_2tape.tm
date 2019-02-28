# Copy As to second tape
0 a:B 0 X:a R:R
0 b:B 0 b:B R:S
0 B:B 1 B:B L:L

# Erase an A for every B
1 b:a 1 X:B L:L
1 X:a 1 X:a L:S
1 X:B 1 X:B L:S

# End conditions: change the below to decide if you want =, <, >, etc
1 b:B -2 b:B S:S
1 B:a -2 B:a S:S
1 B:B -1 B:B S:S


