#!/usr/bin/env python3

from math import sin, cos, pi, sqrt, fmod
from gcode import PolargraphKinematics, CartesianKinematics
from image_kinematics import ImageKinematics

r = 260
n_segments = 1600
kinematics = ImageKinematics(
    PolargraphKinematics(
        top_clip_distance=870,
        wire_length=650,
        max_feedrate=750,
    ),
    1080, 2 * r)

kinematics.move(0, 0)

k = 4 / 3.0
max_theta = 6 * pi
for i in range(0, n_segments + 1):
    theta = max_theta * i / n_segments
    theta += pi
    x = r * cos(k * theta) * cos(theta)
    y = r * cos(k * theta) * sin(theta)
    kinematics.move(x, y)

kinematics.move(0, 0)

# kinematics.print_gcode()
kinematics.to_file("rose.g")
