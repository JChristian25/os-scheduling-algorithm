class Process:
    def __init__(self, pid, arrival, burst, priority=0, queue_level=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.priority = priority
        self.queue_level = queue_level
        
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
