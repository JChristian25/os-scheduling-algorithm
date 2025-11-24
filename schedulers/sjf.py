from .base import Scheduler

class SJF(Scheduler):
    """Shortest Job First - prioritizes shortest burst time"""
    
    def __init__(self):
        self.processes = []

    def add(self, p):
        # Insert process in sorted order by burst time
        self.processes.append(p)
        # Sort by burst time (ascending)
        self.processes.sort(key=lambda x: x.burst)

    def next(self):
        if self.processes:
            return self.processes.pop(0)
        return None

    def empty(self):
        return len(self.processes) == 0

