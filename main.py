#!/usr/bin/python3.4
from agent import Agent
from lifegui import GuiPart, Seeder
import math
import threading
import time
from tkinter import *
from queue import Queue, Empty

'''
Constants
'''
# World Width
WIDTH = 128
# World Height
HEIGHT = 128
# Don't Change
KERNEL_SIZE = 3
# Seconds per update
LOOP_TIME = 0.2
# How much life is spread
DENSITY = 2000
# Life dies if less than or equal too
UNDER_POP = 1
# Life dies if greater than or equal too
OVER_POP = 4


def initMessage():
    print("\033[1m\nMulti-threaded Conway's Game of Life\033[0m")
    print('+-+-+-+  Search Area: Holo 3X3')
    print('|#|#|#|')
    print('+-+-+-+  World Size: (' + str(WIDTH) + ' ' + str(HEIGHT) + ')')
    print('|#| |#|')
    print('+-+-+-+  Seed Size: ' + str(DENSITY))
    print('|#|#|#|')
    print('+-+-+-+  Life Tick: ' + str(LOOP_TIME) + ' seconds')


class GameofLife:

    def __init__(self, master):
        self.master = master
        Seeder.density = DENSITY
        self.world = Seeder.seedBoard2(WIDTH, HEIGHT)
        self.a = Agent()
        # Create the convovle queue and populate with a world
        self.queue = Queue()
        self.queue.put(self.world)

        self.lifetime = 0
        self.oldMass = 0
        self.mass = 0
        self.growth = 0

        # Set up the GUI part
        dim = (WIDTH, HEIGHT)
        self.gui = GuiPart(self.master, self.queue, self.end, dim)

        # Set up the worker thread
        self._running = True
        self.thread = threading.Thread(target=self.workerThread)
        self.thread.daemon = True
        self.thread.start()
        self.loop()

    def loop(self):
        '''
        Check every LOOP_TIME ms if there is something new in the queue.
        '''
        self.gui.processIncoming()
        if not self._running:
            import sys
            self.master.destroy()
            sys.exit(1)
        self.master.after(int(LOOP_TIME * 100), self.loop)

    def workerThread(self):
        '''
        Basic convolution loop
        '''
        while self._running:
            time.sleep(LOOP_TIME)
            self.lifetime += 1
            self.world = self.convolve(self.world, WIDTH, HEIGHT)
            self.growth = self.mass - self.oldMass
            self.statusLine()
            self.oldMass = self.mass
            self.mass = 0
            self.queue.put(self.world)

    def statusLine(self):
        print('\r', end="         ")
        status = "         Age: " + str(self.lifetime) + " "
        status += "Mass: " + str(self.mass) + " "
        status += "Growth: " + str(self.growth) + "    "
        print(status, end="")

    def kernelWeight(self, kernel):
        newState = 0
        sum = kernel[0][0] + kernel[0][1] + kernel[0][2] + \
            kernel[1][0] + kernel[1][2] + \
            kernel[2][0] + kernel[2][1] + kernel[2][2]

        if (kernel[1][1] == 1):
            if(sum > UNDER_POP and sum < OVER_POP):
                newState = 1
        else:
            if(sum == 3):
                newState = 1
        self.mass += newState
        return newState

    def wrapWidth(self, i):
        return (
            int(math.fmod(math.fmod(i, WIDTH - 1) + WIDTH - 1, WIDTH - 1)))

    def wrapHeight(self, i):
        return (
            int(math.fmod(math.fmod(i, HEIGHT - 1) + HEIGHT - 1, HEIGHT - 1)))

    # Wrapped edge Game of Life
    def convolve(self, instant, width, height):
        kernel = [[0 for i in range(KERNEL_SIZE)] for j in range(KERNEL_SIZE)]
        nextInstant = [[0 for i in range(width)] for j in range(height)]
        for xpos in range(0, WIDTH - 1):
            for ypos in range(0, HEIGHT - 1):
                left = self.wrapWidth(xpos - 1)
                right = self.wrapWidth(xpos + 1)
                top = self.wrapWidth(ypos + 1)
                bot = self.wrapWidth(ypos - 1)
                kernel[0][0] = (
                    instant[left][top])
                kernel[0][1] = (
                    instant[left][ypos])
                kernel[0][2] = (
                    instant[left][bot])
                kernel[1][0] = (
                    instant[xpos][top])
                kernel[1][1] = (
                    instant[xpos][ypos])
                kernel[1][2] = (
                    instant[xpos][bot])
                kernel[2][0] = (
                    instant[right][top])
                kernel[2][1] = (
                    instant[right][ypos])
                kernel[2][2] = (
                    instant[right][bot])

                nextInstant[xpos][ypos] = self.kernelWeight(kernel)
        return nextInstant

    def end(self):
        '''
        End the convolution loop
        '''
        self._running = False
        self.gui.quit()


def main():
    # Main Function
    window = Tk()
    window.title("An Intelligent Pixel")
    try:
        initMessage()
        client = GameofLife(window)
        window.mainloop()
    except KeyboardInterrupt:
        window.destroy()

main()
