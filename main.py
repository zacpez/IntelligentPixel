#!/usr/bin/python3.4
from agent import Agent
from lifegui import GuiComponent, Seeder
import math
from lifekeys import MessageKey as MK
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
LOOP_TIME = 0.4

SEC_TO_MS = 1000

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
        self.kernel = [[0 for i in range(KERNEL_SIZE)] for j in range(KERNEL_SIZE)]
        self.world = Seeder.seedBoard2(WIDTH, HEIGHT)
        # Create the world queue and populate with a world
        self.renderQueue = Queue()
        self.fix = Queue()
        self.renderQueue.put((MK.WORLD, self.world))

        self.lifetime = 0
        self.oldMass = 0
        self.mass = 0
        self.growth = 0

        # Set up the GUI part
        dim = (WIDTH, HEIGHT)
        self.gui = GuiComponent(self.master, self.renderQueue, self.end, dim)

        # Set up the worker thread
        self._running = True
        self.thread = threading.Thread(target=self.simulationLoop)
        self.thread.daemon = True
        self.thread.start()
        self.guiLoop()

    def guiLoop(self):
        '''
        Check every LOOP_TIME ms if there is something new in the queue.
        '''
        self.gui.processIncoming()
        if not self._running:
            import sys
            self.master.destroy()
            sys.exit(1)
        self.master.after(int(LOOP_TIME*100), self.guiLoop)

    def simulationLoop(self):
        '''
        Basic convolution loop
        '''
        self.agent = Agent(self.renderQueue, self.fix)
        while self._running:
            time.sleep(LOOP_TIME)

            self.lifetime += 1
            self.world = self.convolve(WIDTH, HEIGHT)
            self.agent.senses.put((MK.SENSES, self.world))
            self.agent.actOnce()
            self.renderQueue.put((MK.WORLD, self.world))

            if(self.fix.qsize() > 0):
                message = self.fix.get(0)
                key, pos = message

                if(MK.isKey(message, MK.KILL)):
                    self.world[pos[0]][pos[1]] = 0

            self.growth = self.mass - self.oldMass
            self.statusLine(self.agent.energy)
            self.oldMass = self.mass
            self.mass = 0

    def statusLine(self, energy):
        print('\r', end="         ")
        status =  "Energy: " + str(energy) + " "
        status += "Age: " + str(self.lifetime) + " "
        status += "World Mass: " + str(self.mass) + " "
        status += "World Growth: " + str(self.growth) + " "
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
    def convolve(self, width, height):
        nextInstant = [[0 for i in range(width)] for j in range(height)]
        for xpos in range(0, WIDTH - 1):
            for ypos in range(0, HEIGHT - 1):
                left = self.wrapWidth(xpos - 1)
                right = self.wrapWidth(xpos + 1)
                top = self.wrapWidth(ypos + 1)
                bot = self.wrapWidth(ypos - 1)
                self.kernel[0][0] = (
                    self.world[left][top])
                self.kernel[0][1] = (
                    self.world[left][ypos])
                self.kernel[0][2] = (
                    self.world[left][bot])
                self.kernel[1][0] = (
                    self.world[xpos][top])
                self.kernel[1][1] = (
                    self.world[xpos][ypos])
                self.kernel[1][2] = (
                    self.world[xpos][bot])
                self.kernel[2][0] = (
                    self.world[right][top])
                self.kernel[2][1] = (
                    self.world[right][ypos])
                self.kernel[2][2] = (
                    self.world[right][bot])

                nextInstant[xpos][ypos] = self.kernelWeight(self.kernel)
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
