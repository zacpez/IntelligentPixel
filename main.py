#!/usr/bin/python3.4
import math
import time
import threading
import random
from tkinter import *
try:
    from Queue import Queue, Empty
except:
    from queue import Queue, Empty

###
# Constants
###
# World Width
WIDTH = 128
# World Height
HEIGHT = 128
# Don't Change
KERNEL_SIZE = 3
# Seconds per update
LOOP_TIME = 0.5
# How much randoly spread Life to start with
DENSITY = 2000
# Life dies if less than or equal too
UNDER_POP = 1
# Life dies if greater than or equal too
OVER_POP = 4
GROUND = "black"
NEW_LIFE = "#FF0000"
OLD_LIFE = "#882244"
STILL = "#666666"


def initMessage():
    print("\033[1m\nMulti-threaded Conway's Game of Life\033[0m")
    print('+-+-+-+  Search Area: Holo 3X3')
    print('|#|#|#|')
    print('+-+-+-+  World Size: (' + str(WIDTH) + ' ' + str(HEIGHT) + ')')
    print('|#| |#|')
    print('+-+-+-+  Seed Size: ' + str(DENSITY))
    print('|#|#|#|')
    print('+-+-+-+  Life Tick: ' + str(LOOP_TIME) + ' seconds')


def seedBoard(width, height, density):
    newboard = [[0 for i in range(width)] for i in range(height)]
    for x in range(0, width - 1):
        for y in range(0, height - 1):
            newboard[x][y] = random.randint(0, density) // density
    return newboard


def seedBoard2(width, height, density):
    newboard = [[0 for i in range(width)] for i in range(height)]
    for i in range(0, density):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        newboard[x][y] = 1
    return newboard


class LifeView(Canvas):
    def __init__(self, master, **args):
        Canvas.__init__(self, master, **args)
        self.bind("<Configure>", self.onResize)
        self.width = master.winfo_reqwidth()
        self.oWidth = self.width
        self.height = master.winfo_reqheight()
        self.oHeight = self.height
        self.first = True

    def onResize(self, event):
        if(self.first):
            self.oWidth = event.width
            self.oHeight = event.height
            self.first = False
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)

    def getScale(self):
        return (self.width / self.oWidth, self.height / self.oHeight)


class GuiPart:

    def __init__(self, master, queue, endCommand):
        self.master = master
        self.queue = queue
        # Set up the GUI
        self.master.protocol("WM_DELETE_WINDOW", endCommand)
        self.convolution = [[0 for i in range(WIDTH)] for i in range(HEIGHT)]
        self.canvas = LifeView(self.master, width=WIDTH, height=HEIGHT)
        self.initGUI(master, WIDTH, HEIGHT)
        self.canvas.pack(side=TOP, expand=YES, fill=BOTH)

    def processIncoming(self):
        '''
        While convolutions are computed and sent, render them
        '''
        while self.queue.qsize():
            try:
                convolution = self.queue.get(0)
                self.add(convolution)
                if type(convolution) != 'NoneType':
                    self.boardToImage()
            except Empty:
                # No Image to render
                pass

    def clip(self, lower, upper):
        for x in range(1, WIDTH):
            for y in range(1, HEIGHT):
                if(self.convolution[x][y] > upper):
                    self.convolution[x][y] = upper
                elif(self.convolution[x][y] < lower):
                    self.convolution[x][y] = lower


    def add(self, convolution):
        self.clip(0, 2)
        for x in range(1, WIDTH):
            for y in range(1, HEIGHT):
                if(self.convolution[x][y] == 2 and convolution[x][y] == 1):
                    self.convolution[x][y] = 3
                elif(self.convolution[x][y] and convolution[x][y]):
                    self.convolution[x][y] = 2
                elif(self.convolution[x][y] == 1 and convolution[x][y] == 0):
                    self.convolution[x][y] = 0
                elif(self.convolution[x][y] == 0 and convolution[x][y] == 1):
                    self.convolution[x][y] = 1
                else:
                    self.convolution[x][y] = 0


    def setPixel(self, color, position):
        '''
        Set alive cells to white, and dead ones to black
        '''
        x, y = position
        sx, sy = self.canvas.getScale()
        c = self.canvas.create_rectangle(
            x * sx, y * sy, (x + 1) * sx, (y + 1) * sy,
            fill=color, outline=color, tag="all")

    def boardToImage(self):
        '''
        Read convolution and render to the image
        '''
        self.canvas.delete("all")
        for x in range(0, WIDTH - 1):
            for y in range(0, HEIGHT - 1):
                if(self.convolution[x][y] == 0):
                    self.setPixel(GROUND, (x, y))
                elif(self.convolution[x][y] == 1):
                    self.setPixel(NEW_LIFE, (x, y))
                elif(self.convolution[x][y] == 2):
                    self.setPixel(OLD_LIFE, (x, y))
                elif(self.convolution[x][y] == 3):
                    self.setPixel(STILL, (x, y))

    def initGUI(self, f, w, h):
        '''
        Center the Window on the display
        '''
        ws = f.winfo_screenwidth()
        hs = f.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        f.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.pixels = [[0 for i in range(ws)] for i in range(hs)]

    def quit(self):
        '''
        Clean GUI elements and window
        '''
        print('')
        self.master.destroy()


class ThreadedClient:

    def __init__(self, master):
        self.master = master
        self.world = seedBoard2(WIDTH, HEIGHT, DENSITY)

        # Create the convovle queue and populate with a world
        self.queue = Queue()
        self.queue.put(self.world)

        self._lifetime = 0
        self._oldMass = 0
        self._mass = 0
        self._growth = 0

        # Set up the GUI part
        self.gui = GuiPart(self.master, self.queue, self.endApplication)

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
            self._lifetime += 1
            self.world = self.convolve(self.world, WIDTH, HEIGHT)
            self._growth = self._mass - self._oldMass
            self.statusLine()
            self._oldMass = self._mass
            self._mass = 0
            self.queue.put(self.world)

    def statusLine(self):
        print('\r', end="         ")
        status = "         Age: " + str(self._lifetime) + " "
        status += "Mass: " + str(self._mass) + " "
        status += "Growth: " + str(self._growth) + "    "
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
        self._mass += newState
        return newState

    def wrapWidth(self, i):
        return (
            int(math.fmod(math.fmod(i, WIDTH - 1) + WIDTH - 1, WIDTH - 1)))

    def wrapHeight(self, i):
        return (
            int(math.fmod(math.fmod(i, HEIGHT - 1) + HEIGHT - 1, HEIGHT - 1)))

    # Wrapped edge Game of Life
    def convolve(self, instant, width, height):
        kernel = [[0 for i in range(KERNEL_SIZE)] for i in range(KERNEL_SIZE)]
        nextInstant = [[0 for i in range(width)] for i in range(height)]
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

    def endApplication(self):
        '''
        End the convolution loop
        '''
        self._running = False
        self.gui.quit()


def main():
    # Main Function
    window = Tk()
    window.title("Game of Life")
    try:
        initMessage()
        client = ThreadedClient(window)
        window.mainloop()
    except KeyboardInterrupt:
        window.destroy()

main()
