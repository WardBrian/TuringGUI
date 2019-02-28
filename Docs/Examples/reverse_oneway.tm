#Turing machine that reverses lists input
#Phase 0: Mark the first entry. a is 0, b is 1
0 0 1 a R
0 1 1 b R
0 B -3 B R
#Phase 1:  Move forward to first blank and write #
1   1   1   1  R
1   0   1   0  R
1   B   2   #  L
#Phase 2:  Move left until you find 0, 1 or blank
2   0   3   X  R
2   1   4   X  R
2   B   5   B  R
2   X   2   X  L
# 2.1: If you found the first character, replace it with a blank instead of an X
2   a   3   B  R
2   b   4   B  R
#Phase 3a:  Found 0, move right to blank, then left to #
3   0   3   0  R
3   1   3   1  R
3   X   3   X  R
3   #   3   #  R
3   B   6   0  L
6   0   6   0  L
6   1   6   1  L
6   #   2   #  L
#Phase 3b, Found 1
4   0   4   0  R
4   1   4   1  R
4   X   4   X  R
4   #   4   #  R
4   B   6   1  L
#Cleanup phase
5   X   5   B  R
5   #   -3  B  R

