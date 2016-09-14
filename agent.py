'''
In this Agent Package there are four fundemental sub-modules.

* Critic for learning feedback
* Learning module for learning goals and performance changes
* Performance module for knowledge and actions
* Problem generator for learning goals
'''
from queue import Queue, Empty


class AgentException(Exception):
    def __init__(self, message):
        super(AgentException, self).__init__(message)


class AgentManger:
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
    def __init__(
            self,
            standards,
            perceptions):
        self.stanards = stanards
        self.perceptions = perceptions


class LerningModule:
    def __init__(
            self,
            feedback,
            knowledge,
            changes,
            learning):
        self.feedback = feedback
        self.knowledge = knowledge
        self.changes = changes
        self.learning = learning


class ProblemModule:
    def __init__(
            self,
            learning,
            problems):
        self.learning = learning
        self.problems = problems


class PerformanceModule:
    def __init__(
            self,
            senses,
            changes,
            problems,
            knowledge,
            actions):
        self.senses = senses
        self.changes = changes
        self.problems = problems
        self.knowledge = knowledge
        self.actions = actions


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
            manager,
            sensorMask=None,
            actuatorMask=None,
            bodyMask=None):
        '''
        Create and supply a sensor arrangemnt for the n-types of sensors.
        Create and supply a actuators arrangemnt for the n-types of actuators.
        If a sensor and actuator arrangement is not supplied
        then they will be generated.
        '''
        if(type(sensorMask) != 'NoneType'):
            self.sensors = sensorMask
        else:
            self.generateSensorMask()

        if(type(actuatorMask) != 'NoneType'):
            self.actuators = actuatorMask
        else:
            self.generateActuatorMask()

        if(type(bodyMask) != 'NoneType'):
            self.body = bodyMask
        else:
            self.generateBodyMask()

    def setSensorMask(self, sensorMask):
        if(type(sensorMask) != 'NoneType'):
            self.sensorMask = sensorMask

    def getSensorMask(self):
        if(type(self.sensorMask) != 'NoneType'):
            return self.sensorMask
        else:
            return None

    def generateSensorMask(self):
        pass

    def setActuatorMask(self, actuatorMask):
        if(type(actuatorMask) != 'NoneType'):
            self.actuatorMask = actuatorMask

    def getActuatorMask(self):
        if(type(self.actuatorMask) != 'NoneType'):
            return self.actuatorMask
        else:
            return None

    def generateActuatorMask(self):
        pass

    def setBodyMask(self, actuatorMask):
        if(type(actuatorMask) != 'NoneType'):
            self.actuatorMask = actuatorMask

    def getBodyMask(self):
        if(type(self.actuatorMask) != 'NoneType'):
            return self.actuatorMask
        else:
            return None

    def generateBodyMask(self):
        pass

    def registerType(self, mode, value):
        self.manager.register(mode, value)
