# Scan through, copying 0s to second tape and erasing everything
0 0:B 0 B:0 R:R
0 1:B 0 B:B R:S
0 B:B 1 B:B L:L

# Copy 0s back to first tape
1 B:0 1 0:B L:L
1 B:B -3 B:B R:R




