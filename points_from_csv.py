#!/usr/bin/env python3

# import math
from math import sin, cos, pi, sqrt, fmod


# all distances in mm!
width = 500
n_segments = 1600
top_clip_distance = 870
wire_length = 650
max_feedrate = 750

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

points = []
xmax = 0
ymax = 0
import csv
with open('/home/j0sh/Documents/code/tsp-art/code/points.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
    	x = float(row[0])
    	y = float(row[1])
    	points.append((x,y))
    	xmax = max(xmax, x)
    	ymax = max(ymax, y)

def move_to_normalized(x,y):
	x /= xmax
	x -= 0.5
	x *= width

	y = ymax - y
	y /= ymax
	y -= 0.5
	y *= width
	
	move_to(x,y)

for x,y in points:
	move_to_normalized(x,y)


move_to(0, 0)