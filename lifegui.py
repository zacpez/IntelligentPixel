from queue import Empty
import random
from tkinter import Canvas, YES, BOTH, TOP

GROUND = "black"
NEW_LIFE = "#FF0000"
OLD_LIFE = "#882244"
STILL = "#666666"


class Seeder:
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

    def __init__(self, master, queue, endCommand, dim):
        self.master = master
        self.queue = queue
        self.width, self.height = dim
        # Set up the GUI
        self.master.protocol("WM_DELETE_WINDOW", endCommand)
        self.convolution = [
            [0 for i in range(self.width)] for i in range(self.height)]
        self.canvas = LifeView(
            self.master, width=self.width, height=self.height)
        self.initGUI(master, self.width, self.height)
        self.canvas.pack(side=TOP, expand=YES, fill=BOTH)

    def __exit__(self, type, value, trace):
        self.quit()

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

    def clamp(self, lower, upper):
        '''
        Clamp values to lower and upper values if out of range
        '''
        for x in range(1, self.height):
            for y in range(1, self.width):
                if(self.convolution[x][y] > upper):
                    self.convolution[x][y] = upper
                elif(self.convolution[x][y] < lower):
                    self.convolution[x][y] = lower

    def add(self, convolution):
        self.clamp(0, 2)
        for x in range(1, self.height):
            for y in range(1, self.width):
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
        self.canvas.create_rectangle(
            x * sx, y * sy, (x + 1) * sx, (y + 1) * sy,
            fill=color, outline=color, tag="all")

    def boardToImage(self):
        '''
        Read convolution and render to the image
        '''
        self.canvas.delete("all")
        for x in range(0, self.height - 1):
            for y in range(0, self.width - 1):
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
        self.canvas.postscript(file="life.eps", colormode="color")
        from PIL import Image
        image = Image.open("life.eps")
        image.save("life.png")
        self.master.destroy()
