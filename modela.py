#!/usr/bin/env python
import inkex, cubicsuperpath, simplepath, simplestyle, cspsubdiv
import simplepath
import simplestyle
import simpletransform

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
        self.OptionParser.add_option("-f", "--flatness", action="store", type="float", dest="flat", default=0.2,
                                     help="Minimum flatness of the subdivided curves")


    def output(self):
        """ This method is called last, and outputs the self.commands list to the file. """
        #print "\n".join(self.commands)
        for i in range(0, len(self.commands)):
            print self.commands[i]

    def conv_coords(self, x, y):
        """ Returns the point as (x, y) in roland coordinates. """
        return (self.options.device_origin_x + ( x / self.doc_width ) * self.options.device_width, self.options.device_origin_y + ( y / self.doc_height ) * self.options.device_height)

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
        self.commands.append("H")
        self.commands.append("@ %d %d" % (self.options.z_down, self.options.z_up))
        self.commands.append("V 30;F 30\n")

        # mostly borrowed from hgpl_output.py
        lastX = startX
        lastY = startY

        # find paths in layers
        i = 0
        layerPath = '//svg:g[@inkscape:groupmode="layer"]'
        for layer in svg.xpath(layerPath, namespaces=inkex.NSS):
            i += 1
            
#            transform = layer.get('transform')
#            self.trans_matrix = None
#            if transform:
#                self.trans_matrix = simpletransform.parseTransform(str(transform))

            nodePath = ('//svg:g[@inkscape:groupmode="layer"][%d]/descendant::svg:path') % i
            for node in svg.xpath(nodePath, namespaces=inkex.NSS):
                d = node.get('d')
                if len(simplepath.parsePath(d)):
                    p = cubicsuperpath.parsePath(d)
                    cspsubdiv.cspsubdiv(p, self.options.flat)
                    for sp in p:
                        first = True
                        for csp in sp:
                            cmd = "PD"
                            if first:
                                cmd = "PU"
                            first = False
                            x, y = self.conv_coords(csp[1][0], self.doc_height - csp[1][1])
                            self.commands.append("%s %d %d" % (cmd, x, y))

        self.commands.append("PU 0 0")

if __name__ == "__main__":
    e = MyEffect()
    e.affect()

