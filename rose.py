#!/usr/bin/env python3

# import math
from math import sin, cos, pi, sqrt, fmod


# all distances in mm!
r = 200
n_segments = 800
top_clip_distance = 870
wire_length = 700
max_feedrate = 650

#
anchor_A_x = -top_clip_distance/2
anchor_B_x =  top_clip_distance/2
anchor_A_y = sqrt(wire_length**2 - (top_clip_distance/2)**2)
anchor_B_y = anchor_A_y

###
print(f"G28.3 ; set current position to 0,0")
print(f"G90   ; absolute mode")
print(f"M203 X{max_feedrate} Y{max_feedrate}")


def dist(x1,y1,x2,y2): return sqrt((x1-x2)**2 + (y1-y2)**2)
def move_to(x,y):
	a = wire_length - dist(anchor_A_x, anchor_A_y, x, y)
	b = wire_length - dist(anchor_B_x, anchor_B_y, x, y)
	print(f"G1 X{a} Y{b}")


move_to(0, 0)

k = 4/3.0
max_theta = 6*pi
for i in range(0,n_segments+1):
	theta = max_theta*i/n_segments
	theta += pi
	x = r*cos(k*theta)*cos(theta)
	y = r*cos(k*theta)*sin(theta)
	move_to(x, y)

move_to(0, 0)