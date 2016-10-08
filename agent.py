'''
In this Agent Package there are four fundemental sub-modules.

* Critic for learning feedback
* Learning module for learning goals and performance changes
* Performance module for knowledge and actions
* Problem generator for learning goals
'''
from queue import Queue, Empty
import sqlite3


class AgentException(Exception):
    def __init__(self, message):
        super(AgentException, self).__init__(message)


class AgentManager:
    def __init__(self):
        self.sensors = []
        self.actuators = []

    def register(self, mode, value):
        if(mode == 'sensor'):
            self.sensors.append(value)
        elif(mode == 'actuator'):
            self.actuators.append(value)
        else:
            raise AgentException("Unknown mode type")


class CriticModule:
    def __init__(self, queues):
        self.stanards = None
        self.perceptions = None
        self.feedback = None
        self.register(queues)
        self.applyStanards()

    def register(self, queues):
        (self.stanards, self.perceptions, self.feedback) = queues

    def applyStanards(self):
        '''
        The critic modules require stanrd to compare to.
        Stanards come from outside the Agent.
        '''
        while self.stanards.qsize():
            try:
                self.apply(self.stanards.get(0))
            except Empty:
                # No Satanard in queue
                pass

    def process(self):
        while self.perceptions.qsize():
            try:
                perception = self.perceptions.get(0)
                feedback = self.critize(perception)
                self.feedback.put(feedback)
            except Empty:
                # Nonthing to get
                pass

    def critize(self, perception):
        feedback = ""
        return feedback

    def apply(self, stanard):
        # Apply the standard
        pass


class LearningModule:
    def __init__(self, queues):
        self.feedback = None
        self.knowledge = None
        self.changes = None
        self.learning = None
        self.register(queues)

    def register(self, queues):
        (self.feedback, self.knowledge, self.changes,
         self.learning) = queues


class ProblemModule:
    def __init__(self, queues):
        self.learning = None
        self.problems = None
        self.register(queues)

    def register(self, queues):
        (self.learning, self.problems) = queues


class PerformanceModule:
    def __init__(self, queues):
        self.senses = None
        self.changes = None
        self.problems = None
        self.knowledge = None
        self.actions = None
        self.register(queues)

    def register(self, queues):
        (self.senses, self.changes, self.problems,
         self.knowledge, self.actions) = queues


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
            manager=AgentManager(),
            senses=Queue(),
            actions=Queue(),
            standards=Queue()):
        '''
        Create and supply a sensor arrangemnt for the n-types of sensors.
        Create and supply a actuators arrangemnt for the n-types of actuators.
        If a sensor and actuator arrangement is not supplied
        then they will be generated.
        '''
        self.senses = senses
        self.actions = actions
        self.standards = standards
        changes = Queue()
        problems = Queue()
        knowledge = Queue()
        learning = Queue()
        feedback = Queue()
        self.perceptions = Queue()
        self.performance = self.register(
            PerformanceModule, [self.senses, changes, problems,
                                knowledge, self.actions])
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
        module = moduleType(queues)
        return module

    def senseOnce(self, input):
        '''
        The Agent's senses need to be multiplexed into the critic,
        and performance modules, at independant times. 
        '''
        self.sense.put(input)
        self.perceptions.put(input)
