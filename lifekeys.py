'''
Shared Life Key comparitor
'''


class LifeKey:
    @staticmethod
    def isKey(tup, key):
        return (tup[0] == key)


'''
Message Keys are used to identify the type of messages being
passed on the queues between simulation modules.
'''


class MessageKey(LifeKey):
    WORLD = 0x0001
    AGENT = 0x0002
    SENSE = 0x0004
    ACTUATE = 0x0008
    STANDARD = 0x0010
    PRECEPT = 0x0020
    FEEDBACK = 0x0040
    KNOWLEDGE = 0x0080
    CHANGE = 0x0100
    LEARN = 0x0200
    PROBLEM = 0x0400
    KILL = 0x0800
    ENERGY = 0x1000
    SENSES = 0xF000
    ACTIONS = 0xE000


'''
Action Keys are used to identify the type of actions being
performed.
'''


class ActionKey(LifeKey):
    STAY = 0x0000
    UP = 0x0001
    DOWN = 0x0002
    LEFT = 0x0004
    RIGHT = 0x0008
