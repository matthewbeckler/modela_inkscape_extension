#!/usr/bin/env python
import sys
import os
import inkex
import simplepath
import simplestyle
import simpletransform

import Bezier

class MyEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.commands = []
        self.trans_matrix = None
        self.OptionParser.add_option("-w", "--device_width", action="store", type="int", dest="device_width", default=10000,
                                     help="Output width")
        self.OptionParser.add_option("--device_height", action="store", type="int", dest="device_height", default=10000,
                                     help="Output height")
        self.OptionParser.add_option("-x", "--device_origin_x", action="store", type="int", dest="device_origin_x", default=0,
                                     help="Origin x-coordinate")
        self.OptionParser.add_option("-y", "--device_origin_y", action="store", type="int", dest="device_origin_y", default=0,
                                     help="Origin y-coordinate")
        self.OptionParser.add_option("-u", "--z_axis_up", action="store", type="int", dest="z_up", default=100,
                                     help="Z-axis 'up'")
        self.OptionParser.add_option("-d", "--z_axis_down", action="store", type="int", dest="z_down", default=-30,
                                     help="Z-axis 'down'")
        self.OptionParser.add_option("-n", "--bezier_points", action="store", type="int", dest="bezier_points", default=100,
                                     help="Number of points for Bezier curve linearization")


    def output(self):
        """ This method is called laste, and outputs the self.commands list to the file. """
        #print "\n".join(self.commands)
        for i in range(1, len(self.commands)):
            if self.commands[i-1] == self.commands[i]:
                continue
            print self.commands[i]

    def conv(self, x, y):
        if self.trans_matrix:
            xt = self.trans_matrix[0][0]*x + self.trans_matrix[0][1]*y + self.trans_matrix[0][2]
            yt = self.trans_matrix[1][0]*x + self.trans_matrix[1][1]*y + self.trans_matrix[1][2]
        else:
            xt = x
            yt = y
        newX = self.options.device_origin_x + ( xt / self.doc_width ) * self.options.device_width
        newY = self.options.device_origin_y + ( yt / self.doc_height ) * self.options.device_height

        return newX, newY

    def coord(self, x, y, z):
        """ Returns the point as text (Z x y z) in roland coordinates. Uses self.rol_width, self.rol_height, self.rol_originX, and self.rol_originY. """
        newX, newY = self.conv(x, y)
        return "Z " + str(int(newX)) + " " + str(int(newY)) + " " + str(z)

    def effect(self):
        """ This method is called first, and sets up the self.commands list for later output. """
        startX = 0
        startY = 0
        startZ = self.options.z_up

        svg = self.document.getroot()
        # find document width and height, used to scale down
        self.doc_width = inkex.unittouu(svg.get('width'))
        self.doc_height = inkex.unittouu(svg.get('height'))

        # add header
        self.commands.append("^DF")
        self.commands.append("! 1")
        self.commands.append("V 64;F 64")
        self.commands.append(self.coord(startX, startY, startZ))
        self.commands.append("V 64;F 64")
        self.commands.append("V 30;F 30\n")

        # mostly borrowed from hgpl_output.py
        lastX = startX
        lastY = startY

        # find paths in layers
        i = 0
        layerPath = '//svg:g[@inkscape:groupmode="layer"]'
        for layer in svg.xpath(layerPath, namespaces=inkex.NSS):
            i += 1
            
            transform = layer.get('transform')
            self.trans_matrix = None
            if transform:
                self.trans_matrix = simpletransform.parseTransform(str(transform))

            nodePath = ('//svg:g[@inkscape:groupmode="layer"][%d]/descendant::svg:path') % i
            for path in svg.xpath(nodePath, namespaces=inkex.NSS):
                style = path.get('style')
                if style:
                    style = simplestyle.parseStyle(style)
                    if style['fill'] != 'none':
                        self.commands.append("fill: " + style['fill'])

                d = path.get('d')
                sp = simplepath.parsePath(d)
                if len(sp):
                    # loop over all points
                    for cmd, points in sp:
                        if cmd == "M": # move-to
                            #self.commands.append(repr(cmd) + " " + repr(points))
                            # first, raise head
                            self.commands.append(self.coord(lastX, lastY, self.options.z_up))
                            # move to new place
                            startX = points[0] # keep track of start in case we get a "Z" = closepath
                            startY = points[1]
                            lastX = startX
                            lastY = startY
                            self.commands.append(self.coord(lastX, lastY, self.options.z_up))
                            # lower head
                            self.commands.append(self.coord(lastX, lastY, self.options.z_down))
                        elif cmd == "L": # line-to
                            lastX = points[0]
                            lastY = points[1]
                            self.commands.append(self.coord(lastX, lastY, self.options.z_down))
                        elif cmd == "Z": # closepath
                            # move back to the starting point of this path
                            lastX = startX
                            lastY = startY
                            self.commands.append(self.coord(lastX, lastY, self.options.z_down))
                        elif cmd == "C": # cubic bezier curve
                            #self.commands.append(repr(cmd) + " " + repr(points))
                            interp_points = Bezier.eval_cubic_bezier(self.options.bezier_points,
                                                                     (lastX, lastY),
                                                                     (points[0], points[1]),
                                                                     (points[2], points[3]),
                                                                     (points[4], points[5]))
                            for x, y in interp_points:
                                self.commands.append(self.coord(x, y, self.options.z_down))
                            lastX = points[4]
                            lastY = points[5]
                        else:
                            self.commands.append("unknown " + repr(cmd) + " " + repr(points))
                    
                    self.commands.append(self.coord(lastX, lastY, self.options.z_up))
                    self.commands.append("")
        self.commands.append("Z 0 0 " + str(self.options.z_up))
        self.commands.append("V 0;F 0\n")

if __name__ == "__main__":
    e = MyEffect()
    e.affect()

