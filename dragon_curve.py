#!/usr/bin/env python3

from gcode import Turtle, PolargraphKinematics
from image_kinematics import ImageKinematics

t = Turtle(
    # PolargraphKinematics(
    #     top_clip_distance=870,
    #     wire_length=630,
    #     max_feedrate=600,
    # )
    ImageKinematics(
    PolargraphKinematics(
        top_clip_distance=1350,
        wire_length=900,
        max_feedrate=5000,
        max_acceleration=25,
    ),
    1080, 600)
)


def dragonCurve(order, length):
    t.turn(order * 45)
    dragonCurveRecursive(order, length, 1)


def dragonCurveRecursive(order, length, sign):
    if order == 0:
        t.move(length)
    else:
        rootHalf = (1 / 2) ** (1 / 2)
        dragonCurveRecursive(order - 1, length * rootHalf, 1)
        t.turn(sign * -90)
        dragonCurveRecursive(order - 1, length * rootHalf, -1)


# t.move_to(-100, 0)
# t.set_angle(0)
# dragonCurve(4, 200)
# t.move_to(-100, 0)
# t.set_angle(0)
# dragonCurve(5, 200)
t.move_to(-300, 0)
t.set_angle(0)
dragonCurve(10, 600)
# t.move_to(0, 0)
# t.set_angle(0)


# t.kinematics.print_gcode()
t.kinematics.to_file("dragon_curve.g")