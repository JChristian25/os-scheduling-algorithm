from models.process import Process

class SchedulingSimulator:
    """Core simulation engine for CPU scheduling algorithms"""
    
    def __init__(self, scheduler, processes):
        self.scheduler = scheduler
        self.processes = sorted(processes, key=lambda p: p.arrival)
        self.current_time = 0
        self.gantt_chart = []
        self.completed = []
        self.process_index = 0
        self.current_process = None
        self.time_slice_remaining = 0
        self.context_switches = 0  # Track context switches
        self.last_process = None  # Track last running process for context switch detection
        
    def has_more_work(self):
        """Check if simulation has more work to do"""
        return (self.process_index < len(self.processes) or 
                not self.scheduler.empty() or 
                self.current_process is not None)
    
    def step(self):
        """Execute one time unit of simulation"""
        # Add newly arrived processes
        while (self.process_index < len(self.processes) and 
               self.processes[self.process_index].arrival <= self.current_time):
            arriving = self.processes[self.process_index]
            self.scheduler.add(arriving)
            self.process_index += 1
        
        # If no current process, get next from scheduler
        if self.current_process is None:
            self.current_process = self.scheduler.next()
            if self.current_process:
                # Detect context switch (switching from one process to another)
                if self.last_process is not None and self.last_process != self.current_process:
                    self.context_switches += 1
                    # Add context switch marker to Gantt chart
                    self.gantt_chart.append({
                        'pid': 'CS',
                        'start': self.current_time,
                        'end': self.current_time,
                        'is_context_switch': True
                    })
                
                # Set quantum for Round Robin
                if hasattr(self.scheduler, 'quantum'):
                    self.time_slice_remaining = self.scheduler.quantum
                else:
                    self.time_slice_remaining = float('inf')
                
                # Record start time if first execution
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time
        
        # Execute current process
        if self.current_process:
            # Add to Gantt chart
            if (not self.gantt_chart or 
                self.gantt_chart[-1]['pid'] != self.current_process.pid):
                self.gantt_chart.append({
                    'pid': self.current_process.pid,
                    'start': self.current_time,
                    'end': self.current_time + 1
                })
            else:
                self.gantt_chart[-1]['end'] = self.current_time + 1
            
            # Execute for 1 time unit
            self.current_process.remaining -= 1
            self.time_slice_remaining -= 1
            
            # Check if process completed
            if self.current_process.remaining == 0:
                self.current_process.finish_time = self.current_time + 1
                self.current_process.turnaround_time = (
                    self.current_process.finish_time - self.current_process.arrival
                )
                self.current_process.waiting_time = (
                    self.current_process.turnaround_time - self.current_process.burst
                )
                self.completed.append(self.current_process)
                self.last_process = self.current_process
                self.current_process = None
            # Check if time slice expired (Round Robin)
            elif self.time_slice_remaining == 0:
                self.scheduler.add(self.current_process)
                self.last_process = self.current_process
                self.current_process = None
        else:
            # CPU idle
            if (not self.gantt_chart or 
                self.gantt_chart[-1]['pid'] != 'IDLE'):
                self.gantt_chart.append({
                    'pid': 'IDLE',
                    'start': self.current_time,
                    'end': self.current_time + 1
                })
            else:
                self.gantt_chart[-1]['end'] = self.current_time + 1
        
        self.current_time += 1
        return self.current_process
    
    def run_to_completion(self):
        """Run entire simulation"""
        while self.has_more_work():
            self.step()
        return self.get_results()
    
    def get_results(self):
        """Get simulation results and statistics"""
        if not self.completed:
            return None
        
        avg_waiting = sum(p.waiting_time for p in self.completed) / len(self.completed)
        avg_turnaround = sum(p.turnaround_time for p in self.completed) / len(self.completed)
        
        return {
            'completed': self.completed,
            'gantt_chart': self.gantt_chart,
            'avg_waiting_time': avg_waiting,
            'avg_turnaround_time': avg_turnaround,
            'total_time': self.current_time,
            'context_switches': self.context_switches
        }
    
    def get_state(self):
        """Get current simulation state"""
        waiting_queue = []
        if hasattr(self.scheduler, 'queue'):
            waiting_queue = [p.pid for p in self.scheduler.queue]
        elif hasattr(self.scheduler, 'processes'):
            waiting_queue = [p.pid for p in self.scheduler.processes]
        elif hasattr(self.scheduler, 'queues'):
            for i, q in enumerate(self.scheduler.queues):
                if hasattr(q, 'queue') and q.queue:
                    waiting_queue.append(f"Q{i}: " + str([p.pid for p in q.queue]))
                elif hasattr(q, 'processes') and q.processes:
                    waiting_queue.append(f"Q{i}: " + str([p.pid for p in q.processes]))
        
        return {
            'time': self.current_time,
            'current_process': self.current_process.pid if self.current_process else 'IDLE',
            'remaining': self.current_process.remaining if self.current_process else 0,
            'waiting_queue': waiting_queue,
            'completed': [p.pid for p in self.completed]
        }

