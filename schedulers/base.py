from abc import ABC, abstractmethod

class Scheduler(ABC):
    """Base class for all scheduling algorithms"""
    
    @abstractmethod
    def add(self, process):
        """Add a process to the scheduler"""
        pass
    
    @abstractmethod
    def next(self):
        """Get the next process to execute"""
        pass
    
    @abstractmethod
    def empty(self):
        """Check if scheduler has no processes"""
        pass

