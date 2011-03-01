#!/usr/bin/env python

import pygame
from pygame.locals import *

screen_mode = (600, 600)
color_black = 0,0,0
color_gray = 200,200,200
color_white = 255,255,255

class ModelaSimulator:
    def __init__(self, filename):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_mode)
        pygame.display.set_caption("Pygame intro")
        self.quit = False

        self.cmds = []
        with open(filename, "r") as fid:
            for line in fid:
                line = line.strip()
                if line.startswith("Z"):
                    cmd, x, y, z = line.split()
                    x = int(x)
                    y = int(y)
                    z = int(z)
                    self.cmds.append((cmd, x, y, z))
        self.cmd_index = 0
        self.old_x = self.cmds[0][1] / 10
        self.old_y = self.cmds[0][2] / 10

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
            draw_color = color_black if (cmd[3] < 0) else color_gray
            pygame.draw.line(self.screen, draw_color, (self.old_x, self.old_y), (cmd[1] / 10, cmd[2] / 10))
            self.old_x = cmd[1] / 10
            self.old_y = cmd[2] / 10

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

