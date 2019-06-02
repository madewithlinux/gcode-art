#!/usr/bin/env python3

# import math
from math import sin, cos, pi, sqrt, fmod


# all distances in mm!
r = 80
n_segments = 200
top_clip_distance = 870
wire_length = 630
max_feedrate = 600

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


class Turtle:

	def __init__(self):
		self.x = 0
		self.y = 0
		self.theta = 0
		# self.dir = 0
		# self.dirs = [(1,0), (0,1), (-1,0), (0,-1)]

	def turn(self, theta):
		self.theta = fmod(theta*pi/180 + self.theta, 2*pi)

	def move(self, dist):
		self.x += dist*cos(self.theta)
		self.y += dist*sin(self.theta)
		self.move_to(self.x,self.y)

	def move_to(self, x,y):
		a = wire_length - dist(anchor_A_x, anchor_A_y, x, y)
		b = wire_length - dist(anchor_B_x, anchor_B_y, x, y)
		print(f"G1 X{a} Y{b}")
		self.x = x
		self.y = y

	def set_angle(self, angle):
		self.angle = angle

