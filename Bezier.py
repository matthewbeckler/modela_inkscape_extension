#!/usr/bin/env python
# Code to evaluate cubic and quadratic Bezier curves
# Using "Forward Difference" method as explained at:
# http://www.drdobbs.com/184403417

def eval_quad_bezier(num_points, B0, B1, B2):
    """ Returns num_points between B0 and B2, based on control point B1. """

    # sanity checks
    if num_points < 2:
        raise Exception("num_points must be >= 2")

    # compute polynomial coefficients from Bezier points
    ax = B0[0] + -2 * B1[0] + B2[0]
    ay = B0[1] + -2 * B1[1] + B2[1]
    bx = -2 * B0[0] + 2 * B1[0]
    by = -2 * B0[1] + 2 * B1[1]
    cx = B0[0]
    cy = B0[1]

    # set the number of steps and step size
    num_steps = num_points - 1
    h = 1.0 / num_steps

    # compute forward differences from Bezier points and "h"
    pointX = cx
    pointY = cy
    firstFDX = ax * pow(h, 2) + bx * h
    firstFDY = ay * pow(h, 2) + by * h
    secondFDX = 2 * ax * pow(h, 2)
    secondFDY = 2 * ay * pow(h, 2)

    # compute points at each step
    vertices = []
    vertices.append( (pointX, pointY) )
    for i in range(num_steps):
        pointX += firstFDX
        pointY += firstFDY
        firstFDX += secondFDX
        firstFDY += secondFDY
        vertices.append( (pointX, pointY) )

    return vertices

def eval_cubic_bezier(num_points, B0, B1, B2, B3):
    """ Returns num_points points between B0 and B3, based on control points B1 and B2. """

    # sanity checks
    if num_points < 2:
        raise Exception("num_points must be >= 2")

    # compute polynomial coefficients from Bezier points
    ax = -B0[0] + 3 * B1[0] - 3 * B2[0] + B3[0]
    ay = -B0[1] + 3 * B1[1] - 3 * B2[1] + B3[1]
    bx = 3 * B0[0] + -6 * B1[0] + 3 * B2[0]
    by = 3 * B0[1] + -6 * B1[1] + 3 * B2[1]
    cx = -3 * B0[0] + 3 * B1[0]
    cy = -3 * B0[1] + 3 * B1[1]
    dx = B0[0]
    dy = B0[1]

    # set the number of steps and step size
    num_steps = num_points - 1
    h = 1.0 / num_steps

    # compute forward differences from Bezier points and "h"
    pointX = dx
    pointY = dy
    firstFDX = ax * pow(h, 3) + bx * pow(h, 2) + cx * h
    firstFDY = ay * pow(h, 3) + by * pow(h, 2) + cy * h
    secondFDX = 6 * ax * pow(h, 3) + 2 * bx * pow(h, 2)
    secondFDY = 6 * ay * pow(h, 3) + 2 * by * pow(h, 2)
    thirdFDX = 6 * ax * pow(h, 3)
    thirdFDY = 6 * ay * pow(h, 3)

    # compute points at each step
    vertices = []
    vertices.append( (pointX, pointY) )
    for i in range(num_steps):
        pointX += firstFDX
        pointY += firstFDY
        firstFDX += secondFDX
        firstFDY += secondFDY
        secondFDX += thirdFDX
        secondFDY += thirdFDY
        vertices.append( (pointX, pointY) )

    return vertices

if __name__ == "__main__":
#    for x, y in eval_cubic_bezier(100, (0, 0), (0, 10), (10, 0), (10, 10)):
#        print x, y
    for x, y in eval_quad_bezier(100, (0, 0), (5, 10), (10, 0)):
        print x, y
