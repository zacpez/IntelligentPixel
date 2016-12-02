'''
In this Agent Package there are four fundemental sub-modules.

* Critic for learning feedback
* Learning module for learning goals and performance changes
* Performance module for knowledge and actions
* Problem generator for learning goals
'''
from collections import namedtuple
from lifekeys import MessageKey as MK
from lifekeys import ActionKey as AK
import math
from queue import Queue, Empty
import random
import sqlite3


VIEW_SIZE = 7
WIDTH = 128
HEIGHT = 128


def wrapWidth(i):

    return int(math.fmod(math.fmod(
        i, WIDTH - 1) + WIDTH - 1,
        WIDTH - 1))


def wrapHeight(i):

    return int(math.fmod(math.fmod(
        i, HEIGHT - 1) + HEIGHT - 1,
        HEIGHT - 1))


class AgentException(Exception):
    def __init__(self, message):
        super(AgentException, self).__init__(message)


class CriticModule:
    '''
    The critic module provides information on strategies over time.
    '''
    def __init__(self, queues):
        self.stanards = None
        self.perceptions = None
        self.feedback = None
        self.register(queues)
        self.applyStanards()

        # To be applied on run time WIP
        self.view_size = 7
        self.world_width = 128
        self.world_height = 128

    def register(self, queues):
        (self.stanards, self.perceptions, self.feedback) = queues

    def applyStanards(self):
        '''
        The critic modules require stanrd to compare to.
        Stanards come from outside the Agent.
        '''
        while(self.stanards.qsize() > 0):
            message = self.stanards.get(0)
            if(MK.isKey(message, MK.STANDARD)):
                self.apply(message[1])
            else:
                print(str(message[0]) + "in wrong queue")

    def process(self):
        while(self.perceptions.qsize() > 0):
            perception = self.perceptions.get(0)
            if(MK.isKey(perception, MK.PRECEPT)):
                feedback = self.critize(perception)
                self.feedback.put(feedback)

    def reshape(self, world, position):
        '''
        Extract the subsection of the world the agent calls its view.
        '''
        view = [
            [0 for i in range(self.view_size)] for j in range(self.view_size)]
        for y in range(0, len(view)):
            for x in range(0, len(view[0])):
                xpos = wrapWidth(x - 3)
                ypos = wrapHeight(y - 3)
                view[x][y] = world[xpos][ypos]

        return view

    def critize(self, perception):
        '''
        Determine whether the agent should handle more or less information.
        '''
        key, view, position, energy = perception

        feedback = (
            MK.FEEDBACK,
            self.reshape(view, position),
            position,
            energy)

        return feedback

    def apply(self, stanard):
        # Apply the standard
        setattr(self, stanard[0], stanard[1])
        pass


class LearningModule:
    def __init__(self, queues):
        self.feedback = None
        self.knowledge = None
        self.changes = None
        self.learning = None
        self.register(queues)

        self.action = AK.STAY
        self.lastAction = AK.STAY
        self.lastState = [
            [0 for i in range(VIEW_SIZE)] for j in range(VIEW_SIZE)]
        self.nextState = [
            [0 for i in range(VIEW_SIZE)] for j in range(VIEW_SIZE)]

        self.db = sqlite3.connect('agent.db')
        cursor = self.db.cursor()
        cursor.execute('''select * from stateaction''')
        cursor.fetchone()
        self.fields = [col[0] for col in cursor.description]
        cursor.close()

        self.db.row_factory = self.rowfactory

    def register(self, queues):
        (self.feedback, self.knowledge, self.changes,
         self.learning) = queues

    def rowfactory(self, cursor, row):
        Row = namedtuple("Row", self.fields)
        return Row(*row)

    def encode(self, message):
        Row = namedtuple("Row", self.fields)

        # prev_state
        ps = 0
        for row in message[0]:
            for cell in row:
                ps <<= 1
                ps |= cell

        # prev_action
        pa = message[1]

        # curr_state
        cs = 0
        for row in message[2]:
            for cell in row:
                cs <<= 1
                cs |= cell

        # curr_action
        ca = message[3]

        # energy_delta
        ed = message[4]

        return Row(ps, pa, cs, ca, ed)

    def store(self, row):
        cursor = self.db.cursor()
        cursor.execute(
            'insert into stateaction values (?, ?, ?, ?, ?)', row)
        self.db.commit()
        cursor.close()

    def getSample(self):
        cursor = self.db.cursor()
        cursor.execute(
            '''select * from stateaction order by random() limit 30''')
        self.db.commit()
        return cursor.fetchall()

    def learn(self, row):
        '''
        Take processed senses and records to determine actions
        '''
        ls, la, view, position, energy = row

        self.predictWorld(view)
        valid, invalid = self.avaiableActions()

        if(len(invalid[0]) == 1):
            self.changes.put((MK.KILL, (
                invalid[1][0],
                invalid[1][1])))
            energy += 10

        elif(len(invalid[0]) > 1):
            energy -= 5

        else:
            energy -= 1

        print(str(position) + ": " + str(invalid[1]))

        self.changes.put((MK.ENERGY, energy))

        self.action = valid[0]
        stat = self.encode((ls, la, view, self.action, energy))
        entries = self.getSample()
        smallest = 99999999999999999

        for other in entries:
            dist = self.distance(stat, other)

            if(smallest > dist):
                prevS, prevA, currS, currA, engergy = other
                smallest = dist
                self.action = currA

        entry = self.encode((ls, la, view, self.action, energy))
        self.store(entry)

    def predictWorld(self, view):
        '''
        Hard coded logic, WIP
        Operations should be discovered with a flexible kernel,
        such as adjustiong kernel size, and sum patterns.
        '''
        for row in range(1, len(view) - 1):
            for cell in range(1, len(view[row]) - 1):
                kernel = sum([
                    view[row - 1][cell - 1],
                    view[row - 1][cell],
                    view[row - 1][cell + 1],
                    view[row][cell - 1],
                    view[row][cell + 1],
                    view[row + 1][cell - 1],
                    view[row + 1][cell],
                    view[row + 1][cell + 1]])

                self.nextState[row][cell] = self.cellAlive(
                    view[row][cell], kernel)

    def cellAlive(self, cell, kernel):
        '''
        Hard coded decision tree logic, WIP
        Comparitor object should be discovered, by selecting values
        v1 and v2 for live and kernel respectively.
        '''
        live = 0
        if(cell == 1):
            if(kernel > 1 and kernel < 4):
                live = 1
        else:
            if(kernel == 3):
                live = 1

        return live

    def avaiableActions(self):
        '''
        Check for possible moves in the next state.
        '''
        valid = []
        invalid = []
        position = (3, 3)
        kill = (0, 0)

        for action in [AK.STAY, AK.RIGHT, AK.DOWN, AK.LEFT, AK.UP]:
            px, py = {
                str(AK.STAY): lambda x: (x[0], x[1]),
                str(AK.UP): lambda x: (x[0], x[1] + 1),
                str(AK.DOWN): lambda x: (x[0], x[1] - 1),
                str(AK.LEFT): lambda x: (x[0] - 1, x[1]),
                str(AK.RIGHT): lambda x: (x[0] + 1, x[1])
            }[str(action)](position)

            if(self.nextState[px][py] != 1):
                valid.append(action)
            else:
                invalid.append(action)
                kill = (px - 3, py - 3)

            if(len(invalid) != 1):
                random.shuffle(valid)

        return (valid, (invalid, kill))

    def process(self):
        while(self.feedback.qsize() > 0):
            message = self.feedback.get(0)

            if(MK.isKey(message, MK.FEEDBACK)):
                key, view, position, energy = message

                self.learn(
                    (self.lastState,
                        self.lastAction,
                        view,
                        position,
                        energy))
                self.lastState = view

        while(self.knowledge.qsize() > 0):
            message = self.knowledge.get(0)

            if(MK.isKey(message, MK.KNOWLEDGE)):
                self.learn(message)

        self.changes.put((MK.CHANGE, self.action))
        self.lastAction = self.action

    def stateSim(self, state, other):

        s = int(state)
        o = int(other)
        sims = simo = 0
        while(s != 0 or o != 0):
            if(s & 0x1):
                sims += 1

            if(o & 0x1):
                simo += 1

            s >>= 1
            o >>= 1

        return sims - simo

    def actionSim(self, action, other):

        return 1 if (action == other) else 0

    def energySim(self, energy, other):

        return(energy - other)

    def distance(self, stateAction, other):

        dist = 0
        dist += math.pow(self.stateSim(stateAction[0], other[0]), 2)

        ns = 0
        for row in self.nextState:
            for cell in row:
                ns <<= 1
                ns |= cell

        dist += math.pow(self.stateSim(stateAction[2], ns), 2)
        dist += math.pow(self.actionSim(stateAction[1], other[1]), 2)
        dist += math.pow(self.energySim(stateAction[4], other[4]), 2)

        return math.sqrt(dist)


class ProblemModule:
    def __init__(self, queues):

        self.learning = None
        self.problems = None
        self.register(queues)

    def register(self, queues):

        (self.learning, self.problems) = queues

    def process(self):
        '''
        Generate abstract like problems to fill out untested situations.
        '''
        while(self.learning.qsize() > 0):
            message = self.learning.get(0)

            if(MK.isKey(message, MK.LEARN)):
                self.problems.put((MK.PROBLEM, message[1]))


class PerformanceModule:
    def __init__(self, queues):

        self.sense = None
        self.changes = None
        self.problems = None
        self.knowledge = None
        self.actuators = None
        self.register(queues)

    def register(self, queues):

        (self.sense, self.changes, self.problems,
         self.knowledge, self.actuators) = queues

    def process(self):
        '''
        Take changes that the learning module provides, and information from
        the senses to perform actions.
        '''
        while(self.changes.qsize() > 0):
            message = self.changes.get(0)

            key, action = message

            if(MK.isKey(message, MK.CHANGE)):
                self.actuators.put((MK.ACTIONS, action))

            elif(MK.isKey(message, MK.KILL)):
                self.actuators.put((MK.KILL, action))

            elif(MK.isKey(message, MK.ENERGY)):
                self.actuators.put((MK.ENERGY, action))

        while(self.sense.qsize() > 0):
            message = self.sense.get(0)

            if(MK.isKey(message, MK.SENSE)):
                self.actuators.put((MK.ACTIONS, message[1]))


class Agent:
    '''
    Agnets are composed of two substantial segments, the learning segment,
    and the performace segment. To feed each segment with inputs,
    we use sensors. And to act outside of the agent we use actuators.

    sensorTypes is used across agent that have the same types of sensors
    actuatorTypes is used across agents that have the same types of actuators
    '''
    def __init__(
            self,
            draw,
            fix,
            senses=Queue(),
            actions=Queue(),
            standards=Queue()):
        '''
        Create and supply a sensor arrangemnt for the n-types of sensors.
        Create and supply a actuators arrangemnt for the n-types of actuators.
        If a sensor and actuator arrangement is not supplied
        then they will be generated.
        '''
        self.initQueues(senses, actions, standards)
        self.position = (50, 50)
        self.energy = 100
        self.draw = draw
        self.fix = fix
        self.lastEnergy = 0

        # to be removed, WIP
        self.world_width = 128
        self.world_height = 128

        self.draw.put((MK.AGENT, self.position))

    def initQueues(self, senses, actions, standards):
        '''
        Create an dispurse the message queues among the agent modules.
        '''
        self.senses = senses
        self.actions = actions
        self.standards = standards
        self.sense = Queue()
        changes = Queue()
        problems = Queue()
        knowledge = Queue()
        learning = Queue()
        feedback = Queue()
        self.actuators = Queue()
        self.perceptions = Queue()

        self.performance = self.register(
            PerformanceModule, [self.sense, changes, problems,
                                knowledge, self.actuators])

        self.learning = self.register(
            LearningModule, [feedback, knowledge, changes, learning])

        self.critic = self.register(
            CriticModule, [self.standards, self.perceptions, feedback])

        self.problem = self.register(
            ProblemModule, [learning, problems])

    def register(self, moduleType, queues=[]):
        '''
        Give each modules the neccessary message passing queues,
        respective to their purpose.
        '''
        return moduleType(queues)

    def statusLine(self):
        print("Energy:" + str(self.energy) + "")

    def processIncoming(self):
        '''
        For each module at each state, process data once.
        '''
        self.critic.process()
        self.learning.process()
        self.problem.process()
        self.performance.process()

    def move(self, action):
        '''
        Given ActionKey perform the position change.
        '''
        self.position = {
            AK.STAY: lambda x: x,
            AK.UP: lambda x: (
                wrapWidth(x[0]), wrapHeight(x[1] + 1)),
            AK.DOWN: lambda x: (
                wrapWidth(x[0]), wrapHeight(x[1] - 1)),
            AK.LEFT: lambda x: (
                wrapWidth(x[0] - 1), wrapHeight(x[1])),
            AK.RIGHT: lambda x: (
                wrapWidth(x[0] + 1), wrapHeight(x[1]))
        }[action](self.position)

    def senseOnce(self, input):
        '''
        The Agent's senses need to be multiplexed into the critic,
        and performance modules, at independant times.
        '''
        key, world = input

        # self.sense.put((MK.SENSE, world, self.position, energy_delta))
        self.perceptions.put((MK.PRECEPT, world, self.position, self.energy))

    def actOnce(self):
        '''
        The world provides state transition triggers, method
        actOnce is one transition for the agent.
        '''
        while(self.senses.qsize() > 0):
            message = self.senses.get(0)
            if(MK.isKey(message, MK.SENSES)):
                self.senseOnce(message)

        self.processIncoming()
        self.lastEnergy = self.energy

        while(self.actuators.qsize() > 0):
            message = self.actuators.get(0)

            if(MK.isKey(message, MK.KILL)):
                print(str(self.position) + " : " + str(message[1]))
                xpos = self.position[0] + message[1][0]
                ypos = self.position[1] + message[1][1]
                msg = (MK.KILL, (xpos, ypos))
                self.fix.put(msg)

            elif(MK.isKey(message, MK.ACTIONS)):
                self.move(message[1])
                self.draw.put((MK.AGENT, self.position))

            elif(MK.isKey(message, MK.ENERGY)):
                self.energy = message[1]
