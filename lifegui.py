from queue import Empty
import random
from lifekeys import MessageKey as MK
from tkinter import Canvas, YES, BOTH, TOP

GROUND = "black"
OLD_LIFE = STILL = NEW_LIFE = "#FF0000"
PIXEL = "#0000FF"
# OLD_LIFE = "#882244"
# STILL = "#666666"


class Seeder:
    '''
    Initialiaze the seeder by setting the density, then run a seed method.
    '''
    density = 0

    @staticmethod
    def seedBoard(width, height):
        newboard = [[0 for i in range(width)] for j in range(height)]
        for x in range(0, width - 1):
            for y in range(0, height - 1):
                newboard[x][y] = (
                    random.randint(0, Seeder.density) // Seeder.density)
        return newboard

    @staticmethod
    def seedBoard2(width, height):
        newboard = [[0 for i in range(width)] for j in range(height)]
        for i in range(0, Seeder.density):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            newboard[y][x] = 1
        return newboard


class LifeView(Canvas):
    '''
    LifeView is derived to handle resize events specifically
    '''
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


class GuiComponent:
    '''
    The GUI events and logic is dispatched from the over arching object.
    '''
    def __init__(self, master, queue, endCommand, dim):
        self.master = master
        self.renderElements = queue
        self.width, self.height = dim

        self.px = self.py = 0

        # Set up the GUI
        self.master.protocol("WM_DELETE_WINDOW", endCommand)
        self.world = [
            [0 for i in range(self.width)] for i in range(self.height)]
        self.canvas = LifeView(
            self.master, width=self.width - 1, height=self.height - 1)
        self.initGUI(master, self.width, self.height)
        self.canvas.pack(side=TOP, expand=YES, fill=BOTH)

    def __exit__(self, type, value, trace):
        self.quit()

    def processIncoming(self):
        '''
        While world's computed and sent, render the cells
        '''
        while self.renderElements.qsize() > 0:
            drawMessage = self.renderElements.get(0)
            key, world = drawMessage

            if(MK.isKey(drawMessage, MK.WORLD)):
                self.world = world

            elif(MK.isKey(drawMessage, MK.AGENT)):
                self.px, self.py = world
        self.boardToImage()

    def clamp(self, lower, upper):
        '''
        Clamp values to lower and upper values if out of range
        '''
        for x in range(0, self.height - 1):
            for y in range(0, self.width - 1):
                if(self.world[x][y] > upper):
                    self.world[x][y] = upper
                elif(self.world[x][y] < lower):
                    self.world[x][y] = lower

    def add(self, world):
        '''
        Colour value changes.
        '''
        self.clamp(0, 2)
        for x in range(0, self.height - 1):
            for y in range(0, self.width - 1):
                if(self.world[x][y] == 2 and world[x][y] == 1):
                    self.world[x][y] = 3
                elif(self.world[x][y] and world[x][y]):
                    self.world[x][y] = 2
                elif(self.world[x][y] == 1 and world[x][y] == 0):
                    self.world[x][y] = 0
                elif(self.world[x][y] == 0 and world[x][y] == 1):
                    self.world[x][y] = 1
                else:
                    self.world[x][y] = 0

    def setPixel(self, color, position):
        '''
        Set alive cells to white, and dead ones to black
        TODO: update rectangle, rather than create
        '''
        x, y = position
        sx, sy = self.canvas.getScale()
        self.canvas.create_rectangle(
            x * sx, y * sy, (x + 1) * sx, (y + 1) * sy,
            fill=color, outline=color, tag="all")

    def boardToImage(self):
        '''
        Read world and render to the image
        '''
        self.canvas.delete("all")
        for x in range(0, self.height - 1):
            for y in range(0, self.width - 1):
                if(self.world[x][y] == 0):
                    self.setPixel(GROUND, (x, y))
                else:
                    self.setPixel(NEW_LIFE, (x, y))
        self.setPixel(PIXEL, (self.px, self.py))

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
        self.canvas.postscript(file="life.eps", colormode="color")
        from PIL import Image
        image = Image.open("life.eps")
        image.save("life.png")
        self.master.destroy()
