from .base import Scheduler

class MLQ(Scheduler):
    def __init__(self, queues):
        """
        queues = [
            FCFS(),
            SJF(),
            RoundRobin(quantum=4)
        ]
        """
        self.queues = queues

    def add(self, p):
        level = p.queue_level
        self.queues[level].add(p)

    def next(self):
        for q in self.queues:
            if not q.empty():
                return q.next()
        return None

    def empty(self):
        return all(q.empty() for q in self.queues)

