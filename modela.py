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
        self.OptionParser.add_option("-u", "--z_axis_up", action="store", type="int", dest="z_up", default=-1400, help="Z-axis 'up'")
        self.OptionParser.add_option("-d", "--z_axis_down", action="store", type="int", dest="z_down", default=-1600, help="Z-axis 'down'")
        self.OptionParser.add_option("-c", "--feed_rate_cutting", action="store", type="float", dest="feed_rate_cutting", default="1.0", help="Feed rate for cutting")
        self.OptionParser.add_option("-m", "--feed_rate_moving", action="store", type="float", dest="feed_rate_moving", default="1.0", help="Feed rate for moving")
        self.OptionParser.add_option("-f", "--flatness", action="store", type="float", dest="flat", default=0.2, help="Minimum flatness of the subdivided curves")

    def output(self):
        """ This method is called last, and outputs the self.commands list to the file. """
        #print "\n".join(self.commands)
        for i in range(0, len(self.commands)):
            print self.commands[i]

    def conv_coords(self, x, y):
        """ Returns the point as (x, y) in roland coordinates. """
        return (( x / self.doc_width ) * 6000, ( y / self.doc_height ) * 4000)

    def effect(self):
        """ This method is called first, and sets up the self.commands list for later output. """
        svg = self.document.getroot()
        # find document width and height, used to scale down
        self.doc_width = inkex.unittouu(svg.get('width'))
        self.doc_height = inkex.unittouu(svg.get('height'))

        # add header
        self.commands.append("^DF;")
        self.commands.append("! 1;")
        self.commands.append("H;")
        self.commands.append("@ %d %d;" % (self.options.z_down, self.options.z_up))
        self.commands.append("V {0};F {0};\n".format(self.options.feed_rate_moving))
        self.commands.append("Z 0 0 %d;" % self.options.z_up)

        # mostly borrowed from hgpl_output.py
        lastX = 0
        lastY = 0

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
                                self.commands.append("V {0};F {0};".format(self.options.feed_rate_cutting))
                            first = False
                            x, y = self.conv_coords(csp[1][0], self.doc_height - csp[1][1])
                            self.commands.append("Z %d %d %d;" % (x, y, self.options.z_down))
                            lastX = x
                            lastY = y
                        self.commands.append("V {0};F {0};".format(self.options.feed_rate_moving))
                        self.commands.append("Z %d %d %d;" % (lastX, lastY, self.options.z_up))

        self.commands.append("Z 0 0 %d;" % self.options.z_up)
        self.commands.append("H;")

if __name__ == "__main__":
    e = MyEffect()
    e.affect()

