from .base import Scheduler

class FCFS(Scheduler):
    """First Come First Served - processes in arrival order"""
    
    def __init__(self):
        self.queue = []

    def add(self, p):
        self.queue.append(p)

    def next(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def empty(self):
        return len(self.queue) == 0

