from .base import Scheduler

class RoundRobin(Scheduler):
    """Round Robin - time-sliced fair scheduling"""
    
    def __init__(self, quantum):
        self.queue = []
        self.quantum = quantum

    def add(self, p):
        self.queue.append(p)

    def next(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def empty(self):
        return len(self.queue) == 0

