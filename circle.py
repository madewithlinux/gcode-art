#!/usr/bin/env python3

# import math
from math import sin, cos, pi, sqrt


# all distances in mm!
r = 80
n_segments = 200
top_clip_distance = 880
wire_length = 600
max_feedrate = 500

#
anchor_A_x = -top_clip_distance/2
anchor_B_x =  top_clip_distance/2
anchor_A_y = sqrt(wire_length**2 - (top_clip_distance/2)**2)
anchor_B_y = anchor_A_y

###
print(f"G28.3")
print(f"G90")
print(f"M203 X{max_feedrate} Y{max_feedrate}")


def dist(x1,y1,x2,y2): return sqrt((x1-x2)**2 + (y1-y2)**2)
def move_to(x,y):
	a = wire_length - dist(anchor_A_x, anchor_A_y, x, y)
	b = wire_length - dist(anchor_B_x, anchor_B_y, x, y)
	print(f"G1 X{a} Y{b}")


move_to(r, 0)


for i in range(1,n_segments):
	x = r*cos(2*pi*i/n_segments)
	y = r*sin(2*pi*i/n_segments)
	move_to(x,y)

move_to(0, 0)