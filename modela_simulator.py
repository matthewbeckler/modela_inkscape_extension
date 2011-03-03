#!/usr/bin/env python

import pygame
from pygame.locals import *

screen_mode = (580, 400)
color_black = 0,0,0
color_gray = 200,200,200
color_white = 255,255,255

class ModelaSimulator:
    def __init__(self, filename):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_mode)
        pygame.display.set_caption("Modela simulator")
        self.quit = False

        self.cmds = []
        z_max = -10000
        z_min =  10000
        with open(filename, "r") as fid:
            for line in fid:
                line = line.strip().strip(";")
                if line.startswith("Z"):
                    cmd, x, y, z = line.split()
                    x = int(x) / 10
                    y = screen_mode[1] - (int(y) / 10)
                    z = int(z)
                    z_max = max(z, z_max)
                    z_min = min(z, z_min)
                    self.cmds.append((cmd, x, y, z))
        self.cmd_index = -1
        self.old_x = 0
        self.old_y = screen_mode[1] - 0
        self.z_mid = int((z_max + z_min) / 2.0)

        self.screen.fill(color_white)
        pygame.display.flip()

        self.clock = pygame.time.Clock()

    def update(self):
        return

    def draw(self):
        if self.cmd_index == len(self.cmds) - 1:
            pass
        else:
            self.cmd_index += 1
            cmd = self.cmds[self.cmd_index]
            draw_color = color_black if (cmd[3] < self.z_mid) else color_gray
            pygame.draw.line(self.screen, draw_color, (self.old_x, self.old_y), (cmd[1], cmd[2]))
            self.old_x = cmd[1]
            self.old_y = cmd[2]

        pygame.display.flip()

    def mainLoop(self):
        while not self.quit:
            #handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit = True
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: %s filename" % sys.argv[0]
        sys.exit(1)
    sim = ModelaSimulator(sys.argv[1])
    sim.mainLoop()

