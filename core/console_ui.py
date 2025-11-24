from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
from rich import box
from .simulator import SchedulingSimulator
from .gantt_chart import GanttChart

class ConsoleUI:
    """Interactive console interface for scheduling simulation"""
    
    def __init__(self, simulator, scheduler_name="Unknown"):
        self.simulator = simulator
        self.scheduler_name = scheduler_name
        self.step_count = 0
        self.console = Console()
        self.state_history = []  # Stack for undo functionality
        self.max_history = 50  # Keep last 50 states
    
    def clear_screen(self):
        """Clear the console screen"""
        self.console.clear()
    
    def save_state(self):
        """Save current simulator state for undo functionality"""
        import copy
        
        # Save process states
        process_states = []
        for p in self.simulator.processes:
            process_states.append({
                'remaining': p.remaining,
                'start_time': p.start_time,
                'finish_time': p.finish_time,
                'waiting_time': p.waiting_time,
                'turnaround_time': p.turnaround_time
            })
        
        state = {
            'current_time': self.simulator.current_time,
            'gantt_chart': copy.deepcopy(self.simulator.gantt_chart),
            'completed': list(self.simulator.completed),
            'process_index': self.simulator.process_index,
            'current_process': self.simulator.current_process,
            'time_slice_remaining': self.simulator.time_slice_remaining,
            'step_count': self.step_count,
            'process_states': process_states,
            'context_switches': self.simulator.context_switches,
            'last_process': self.simulator.last_process
        }
        
        self.state_history.append(state)
        
        # Keep only last max_history states
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
    
    def restore_state(self):
        """Restore previous simulator state (undo)"""
        if not self.state_history:
            return False
        
        state = self.state_history.pop()
        
        # Restore simulator state
        self.simulator.current_time = state['current_time']
        self.simulator.gantt_chart = state['gantt_chart']
        self.simulator.completed = state['completed']
        self.simulator.process_index = state['process_index']
        self.simulator.current_process = state['current_process']
        self.simulator.time_slice_remaining = state['time_slice_remaining']
        self.simulator.context_switches = state['context_switches']
        self.simulator.last_process = state['last_process']
        self.step_count = state['step_count']
        
        # Restore process states
        for i, p in enumerate(self.simulator.processes):
            p.remaining = state['process_states'][i]['remaining']
            p.start_time = state['process_states'][i]['start_time']
            p.finish_time = state['process_states'][i]['finish_time']
            p.waiting_time = state['process_states'][i]['waiting_time']
            p.turnaround_time = state['process_states'][i]['turnaround_time']
        
        # Need to restore scheduler queue state
        # Clear and rebuild scheduler queue
        if hasattr(self.simulator.scheduler, 'queue'):
            self.simulator.scheduler.queue.clear()
        elif hasattr(self.simulator.scheduler, 'processes'):
            self.simulator.scheduler.processes.clear()
        elif hasattr(self.simulator.scheduler, 'queues'):
            for q in self.simulator.scheduler.queues:
                if hasattr(q, 'queue'):
                    q.queue.clear()
                elif hasattr(q, 'processes'):
                    q.processes.clear()
        
        # Re-add processes that should be in queue
        for p in self.simulator.processes[:self.simulator.process_index]:
            if p not in self.simulator.completed and p != self.simulator.current_process:
                if p.arrival <= self.simulator.current_time:
                    self.simulator.scheduler.add(p)
        
        return True
    
    def display_header(self):
        """Display header with simulation info"""
        title = Text("CPU SCHEDULING ALGORITHM SIMULATOR\n", style="bold white", justify="center")
        title.append(f"Algorithm: {self.scheduler_name}", style="cyan")
        self.console.print(Panel(title, border_style="blue", padding=(1, 2), style="on blue"))
        self.console.print()
    
    def display_statistics(self):
        """Display final statistics"""
        results = self.simulator.get_results()
        
        if not results:
            self.console.print("[bold red]No completed processes yet.[/bold red]")
            return
        
        self.console.print()
        
        # Statistics Header
        header = Text("FINAL STATISTICS", style="bold white on blue", justify="center")
        self.console.print(Panel(header, border_style="blue", padding=(1, 2)))
        self.console.print()
        
        # Process Results Table
        table = Table(title="Process Execution Details", border_style="cyan", box=box.DOUBLE_EDGE)
        table.add_column("PID", style="cyan bold", justify="center")
        table.add_column("Arrival", style="magenta", justify="center")
        table.add_column("Burst", style="magenta", justify="center")
        table.add_column("Start", style="blue", justify="center")
        table.add_column("Finish", style="blue", justify="center")
        table.add_column("Waiting", style="yellow", justify="center")
        table.add_column("Turnaround", style="green", justify="center")
        
        for p in results['completed']:
            table.add_row(
                p.pid,
                str(p.arrival),
                str(p.burst),
                str(p.start_time),
                str(p.finish_time),
                str(p.waiting_time),
                str(p.turnaround_time)
            )
        
        self.console.print(table)
        self.console.print()
        
        # Summary Statistics
        summary = Table(border_style="green", box=box.ROUNDED, show_header=False)
        summary.add_column("Metric", style="bold cyan")
        summary.add_column("Value", style="bold yellow", justify="right")
        
        summary.add_row("Average Waiting Time", f"{results['avg_waiting_time']:.2f}")
        summary.add_row("Average Turnaround Time", f"{results['avg_turnaround_time']:.2f}")
        summary.add_row("Total Execution Time", f"{results['total_time']}")
        summary.add_row("Context Switches", f"{results['context_switches']}")
        
        # Calculate CPU utilization
        cpu_time = sum(p.burst for p in results['completed'])
        cpu_utilization = (cpu_time / results['total_time'] * 100) if results['total_time'] > 0 else 0
        summary.add_row("CPU Utilization", f"{cpu_utilization:.1f}%")
        
        self.console.print(Panel(summary, title="Summary", border_style="green", box=box.DOUBLE))
        self.console.print()
        
        # Detailed Gantt Chart
        GanttChart.generate_detailed(results['gantt_chart'], console=self.console)
    
    def build_layout(self):
        """Build the main layout for the simulation display"""
        layout = Layout()
        
        # Define layout structure
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=6)
        )
        
        # Split body into left and right
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        # Split left into status and queues
        layout["left"].split_column(
            Layout(name="status", size=10),
            Layout(name="queues")
        )
        
        # Split right into process table and gantt
        layout["right"].split_column(
            Layout(name="process_table"),
            Layout(name="gantt", size=8)
        )
        
        return layout
    
    def get_status_panel(self):
        """Get the status panel showing current execution"""
        state = self.simulator.get_state()
        
        # Time and Step Info
        info_text = Text()
        info_text.append("Current Time: ", style="bold cyan")
        info_text.append(f"{state['time']}", style="bold yellow")
        info_text.append("  |  ", style="dim")
        info_text.append("Step Count: ", style="bold cyan")
        info_text.append(f"{self.step_count}", style="bold yellow")
        
        # Currently Executing Process
        if state['current_process'] != 'IDLE':
            exec_info = Text("\n\nCurrently Executing: ", style="bold green")
            exec_info.append(state['current_process'], style="bold white on green")
            
            current_p = self.simulator.current_process
            if current_p:
                completed = current_p.burst - current_p.remaining
                progress_text = f"\nProgress: {completed}/{current_p.burst} ({completed*100//current_p.burst}%)"
                exec_info.append(progress_text, style="cyan")
            
            info_text.append("\n")
            info_text.append_text(exec_info)
        else:
            idle_text = Text("\n\nCPU IDLE", style="bold yellow on red")
            info_text.append("\n")
            info_text.append_text(idle_text)
        
        return Panel(info_text, title="Status", border_style="blue", box=box.ROUNDED)
    
    def get_queues_panel(self):
        """Get the queues panel showing waiting and completed processes"""
        state = self.simulator.get_state()
        
        queue_text = Text()
        queue_text.append("Waiting Queue:\n", style="bold yellow")
        
        if state['waiting_queue']:
            if isinstance(state['waiting_queue'][0], str) and 'Q' in state['waiting_queue'][0]:
                for queue_info in state['waiting_queue']:
                    queue_text.append(f"  {queue_info}\n", style="cyan")
            else:
                queue_str = ' -> '.join(map(str, state['waiting_queue']))
                queue_text.append(f"  {queue_str}\n", style="cyan")
        else:
            queue_text.append("  (empty)\n", style="dim")
        
        queue_text.append("\nCompleted Processes:\n", style="bold green")
        if state['completed']:
            completed_str = ', '.join(map(str, state['completed']))
            queue_text.append(f"  {completed_str}", style="green")
        else:
            queue_text.append("  (none)", style="dim")
        
        return Panel(queue_text, title="Queues", border_style="yellow", box=box.ROUNDED)
    
    def get_process_table_panel(self):
        """Get the process table panel"""
        all_processes = self.simulator.processes
        
        table = Table(border_style="blue", box=box.SIMPLE, show_header=True, header_style="bold cyan")
        table.add_column("PID", style="cyan bold", justify="center", width=8)
        table.add_column("Arr", style="magenta", justify="center", width=5)
        table.add_column("Burst", style="magenta", justify="center", width=6)
        table.add_column("Rem", style="yellow", justify="center", width=5)
        table.add_column("Status", justify="center", width=12)
        
        for p in all_processes:
            if p in self.simulator.completed:
                status = "[bold green]Done[/bold green]"
            elif p == self.simulator.current_process:
                status = "[bold green on white]Run[/bold green on white]"
            elif p.arrival <= self.simulator.current_time:
                status = "[bold yellow]Wait[/bold yellow]"
            else:
                status = "[dim]---[/dim]"
            
            table.add_row(
                p.pid,
                str(p.arrival),
                str(p.burst),
                str(p.remaining),
                status
            )
        
        return Panel(table, title="Process Table", border_style="blue", box=box.ROUNDED)
    
    def get_gantt_panel(self):
        """Get the gantt chart panel"""
        if not self.simulator.gantt_chart:
            return Panel(Text("No execution yet", style="dim"), title="Gantt Chart", border_style="yellow", box=box.ROUNDED)
        
        # Create a compact gantt representation
        colors = ['cyan', 'magenta', 'green', 'yellow', 'blue', 'red']
        pid_color_map = {}
        color_idx = 0
        
        chart_line = Text()
        time_line = Text()
        
        recent_entries = self.simulator.gantt_chart[-20:]  # Show last 20 entries (more to show CS markers)
        
        for entry in recent_entries:
            pid = str(entry['pid'])
            
            # Check if this is a context switch marker
            if entry.get('is_context_switch', False):
                chart_line.append("|CS|", style="bold red on white")
                continue
            
            if pid not in pid_color_map:
                if pid == 'IDLE':
                    pid_color_map[pid] = 'dim white'
                else:
                    pid_color_map[pid] = colors[color_idx % len(colors)]
                    color_idx += 1
            
            chart_line.append(f"[{pid:^4}]", style=f"bold {pid_color_map[pid]}")
            time_line.append(f"{entry['start']:^6}", style="dim")
        
        # Add end time
        non_cs_entries = [e for e in recent_entries if not e.get('is_context_switch', False)]
        if non_cs_entries:
            time_line.append(f"{non_cs_entries[-1]['end']:^6}", style="dim")
        
        # Add current time and context switches indicator
        info_line = Text()
        info_line.append(f"\nTime: {self.simulator.current_time}", style="bold yellow")
        info_line.append(f" | Context Switches: {self.simulator.context_switches}", style="bold cyan")
        info_line.append(" | ", style="dim")
        info_line.append("CS", style="bold red on white")
        info_line.append(" = Context Switch", style="dim")
        
        chart_display = Text()
        chart_display.append_text(chart_line)
        chart_display.append("\n")
        chart_display.append_text(time_line)
        chart_display.append_text(info_line)
        
        return Panel(chart_display, title="Gantt Chart (Recent)", border_style="yellow", box=box.ROUNDED)
    
    def get_commands_panel(self):
        """Get the commands panel"""
        commands_text = Text()
        commands_text.append("[ENTER]", style="bold yellow")
        commands_text.append(" Step forward  ", style="cyan")
        commands_text.append("[u]", style="bold yellow")
        commands_text.append(f" Undo ({len(self.state_history)})  ", style="cyan")
        commands_text.append("[r]", style="bold yellow")
        commands_text.append(" Run to completion  ", style="cyan")
        commands_text.append("[q]", style="bold yellow")
        commands_text.append(" Quit", style="cyan")
        
        return Panel(Align.center(commands_text), title="Commands", border_style="cyan", box=box.ROUNDED)
    
    def run_interactive(self):
        """Run interactive stepping mode"""
        while True:
            self.clear_screen()
            
            if not self.simulator.has_more_work():
                self.display_header()
                complete_text = Text("SIMULATION COMPLETE", style="bold green on white", justify="center")
                self.console.print(Panel(complete_text, border_style="green", padding=(1, 2)))
                self.console.print()
                self.display_statistics()
                break
            
            # Build layout
            layout = self.build_layout()
            
            # Fill layout with content
            header_text = Text()
            header_text.append("CPU SCHEDULING ALGORITHM SIMULATOR", style="bold white")
            header_text.append(f"\nAlgorithm: {self.scheduler_name}", style="cyan")
            layout["header"].update(Panel(header_text, border_style="blue", style="on blue"))
            
            layout["status"].update(self.get_status_panel())
            layout["queues"].update(self.get_queues_panel())
            layout["process_table"].update(self.get_process_table_panel())
            layout["gantt"].update(self.get_gantt_panel())
            layout["footer"].update(self.get_commands_panel())
            
            # Display the layout
            self.console.print(layout)
            self.console.print()
            
            choice = self.console.input("[bold cyan]Your choice:[/bold cyan] ").strip().lower()
            
            if choice == 'q':
                self.console.print("\n[bold yellow]Exiting simulation.[/bold yellow]\n")
                break
            elif choice == 'u':
                # Undo last step
                if self.restore_state():
                    continue
                else:
                    self.console.print("\n[bold yellow]No more states to undo![/bold yellow]")
                    self.console.input("[dim]Press ENTER to continue...[/dim]")
            elif choice == 'r':
                with Progress(
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(bar_width=40),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=self.console
                ) as progress:
                    total_burst = sum(p.remaining for p in self.simulator.processes 
                                     if p not in self.simulator.completed)
                    task = progress.add_task("[cyan]Running to completion...", total=total_burst)
                    
                    while self.simulator.has_more_work():
                        self.simulator.step()
                        self.step_count += 1
                        progress.advance(task)
                
                self.clear_screen()
                self.display_header()
                complete_text = Text("SIMULATION COMPLETE", style="bold green on white", justify="center")
                self.console.print(Panel(complete_text, border_style="green", padding=(1, 2)))
                self.console.print()
                self.display_statistics()
                break
            else:
                # Step forward (default action)
                self.save_state()  # Save state before stepping
                self.simulator.step()
                self.step_count += 1
    

