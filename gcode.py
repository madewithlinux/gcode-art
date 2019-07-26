#!/usr/bin/env python3

from math import sin, cos, pi, sqrt, fmod
from abc import abstractmethod, ABCMeta

import numpy as np


def dist(x1, y1, x2, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class Kinematics(metaclass=ABCMeta):
    @abstractmethod
    def move(self, x: float, y: float):
        pass

    @abstractmethod
    def travel(self, x: float, y: float):
        pass

    @property
    @abstractmethod
    def gcode(self) -> [str]:
        pass

    def to_file(self, filename):
        with open(filename, 'w') as f:
            f.writelines(s + '\n' for s in self.gcode)

    def print_gcode(self):
        for s in self.gcode:
            print(s)


class NullKinematics(Kinematics):
    def move(self, x: float, y: float):
        pass

    def travel(self, x: float, y: float):
        pass

    @property
    def gcode(self) -> [str]:
        return ["NullKinematics"]

    def to_file(self, filename):
        pass

    def print_gcode(self):
        for s in self.gcode:
            print(s)


class CartesianKinematics(Kinematics):
    def __init__(self):
        self._gcode = []

    def move(self, x, y):
        self._gcode.append(f'G1 X{x} Y{y}')

    def travel(self, x, y):
        # TODO: pen up
        self._gcode.append(f'G0 X{x} Y{y}')
        # TODO: pen down

    @property
    def gcode(self):
        return self._gcode


class PolargraphKinematics(Kinematics):
    def __init__(self,
                 *,
                 top_clip_distance: int,
                 wire_length: int,
                 max_feedrate: int,
                 max_acceleration: int):
        self.top_clip_distance = top_clip_distance
        self.wire_length = wire_length
        self.max_feedrate = max_feedrate
        self.max_acceleration = max_acceleration  # 200 is good?

        self.anchor_A_x = -top_clip_distance / 2
        self.anchor_B_x = top_clip_distance / 2
        self.anchor_A_y = sqrt(wire_length ** 2 - (top_clip_distance / 2) ** 2)
        self.anchor_B_y = self.anchor_A_y

        self.current_position = (0, 0)
        self.split_threshold = 5  # mm

        self._gcode = [
            "G92 X0 Y0 ; set current position to 0,0",
            "G90       ; absolute mode",
            "M211 S0   ; disable software endstops (to allow negative axis moves)",
            "M205 X2 Y2   ; max marlin-jerk",
            f"M201 X{max_acceleration} Y{max_acceleration}  ; max acceleration",
            f"M203 X{max_feedrate} Y{max_feedrate}",
        ]

    @property
    def gcode(self):
        return self._gcode

    def _move_internal(self, x, y):
        a = self.wire_length - dist(self.anchor_A_x, self.anchor_A_y, x, y)
        b = self.wire_length - dist(self.anchor_B_x, self.anchor_B_y, x, y)
        self._gcode.append(f"G1 X{a} Y{b} F{self.max_feedrate}")

    def move(self, x, y):
        # plan out a spaced out list of points along our route to visit
        line_length = dist(x, y, self.current_position[0], self.current_position[1])
        num_splits = int(line_length // self.split_threshold)

        xs = np.linspace(self.current_position[0], x, num_splits, endpoint=False)
        ys = np.linspace(self.current_position[1], y, num_splits, endpoint=False)

        for x1, y1 in zip(xs, ys):
            self._move_internal(x1, y1)

        # finally, explicitly move to where we were told to go
        self._move_internal(x, y)
        self.current_position = (x, y)

    def travel(self, x, y):
        # TODO: pen up
        self.move(x, y)
        # TODO: pen down


class Turtle:
    def __init__(self, kinematics: Kinematics):
        self.kinematics = kinematics
        self.x = 0
        self.y = 0
        self.theta = 0

    def turn(self, theta):
        self.theta = fmod(theta * pi / 180 + self.theta, 2 * pi)

    def move(self, dist):
        self.x += dist * cos(self.theta)
        self.y += dist * sin(self.theta)
        self.move_to(self.x, self.y)

    def move_to(self, x, y):
        self.kinematics.move(x, y)
        self.x = x
        self.y = y

    def set_angle(self, angle):
        self.angle = angle
