#!/usr/bin/python3.4

view = [[0, 1], [1, 1]]

vs = 0
for row in view:
    for cell in row:
        vs <<= 1
        vs |= cell

print(vs)
