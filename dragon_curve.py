#!/usr/bin/env python3

from turtle import Turtle

t = Turtle()

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

dragonCurve(5, 10)

