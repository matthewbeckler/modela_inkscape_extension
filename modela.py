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
        self.commands.append("^DF;")
        self.commands.append("! 1;")
        self.commands.append("H;")
        self.commands.append("@ %d %d;" % (self.options.z_down, self.options.z_up))
        self.commands.append("V 30;F 30;\n")
	self.commands.append("Z 0 0 %d;" % self.options.z_up)

        # mostly borrowed from hgpl_output.py
        lastX = startX
        lastY = startY

        # find paths in layers
        i = 0
        layerPath = '//svg:g[@inkscape:groupmode="layer"]'
        for layer in svg.xpath(layerPath, namespaces=inkex.NSS):
            i += 1

            nodePath = ('//svg:g[@inkscape:groupmode="layer"][%d]/descendant::svg:path') % i
            for node in svg.xpath(nodePath, namespaces=inkex.NSS):
                # these next lines added from this patch to fix the transformation issues - http://launchpadlibrarian.net/36269154/hpgl_output.py.patch
                # possibly also want to try this code: https://bugs.launchpad.net/inkscape/+bug/600472/+attachment/1475310/+files/hpgl_output.py
                transforms = node.xpath("./ancestor-or-self::svg:*[@transform]",namespaces=inkex.NSS)
                matrix = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
                for parenttransform in transforms:
                    newmatrix = simpletransform.parseTransform(parenttransform.get("transform"))
                    matrix = simpletransform.composeTransform(matrix, newmatrix)

                d = node.get('d')
                if len(simplepath.parsePath(d)):
                    p = cubicsuperpath.parsePath(d)
                    simpletransform.applyTransformToPath(matrix, p) # this line is also from the transform-fixing patch mentioned above
                    cspsubdiv.cspsubdiv(p, self.options.flat)
                    for sp in p:
                        first = True
                        for csp in sp:
                            if first:
				x, y = self.conv_coords(csp[1][0], self.doc_height - csp[1][1])
			        self.commands.append("Z %d %d %d;" % (x, y, self.options.z_up))
                            first = False
                            x, y = self.conv_coords(csp[1][0], self.doc_height - csp[1][1])
                            self.commands.append("Z %d %d %d;" % (x, y, self.options.z_down))
			    lastX = x
			    lastY = y
			self.commands.append("Z %d %d %d;" % (lastX, lastY, self.options.z_up))

        self.commands.append("Z 0 0 %d;" % self.options.z_up)
        self.commands.append("H;")

if __name__ == "__main__":
    e = MyEffect()
    e.affect()

