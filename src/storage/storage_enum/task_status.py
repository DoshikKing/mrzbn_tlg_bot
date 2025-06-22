from enum import Enum


class Status(Enum):
    NEW, PROCESS, FINISH = range(3)
