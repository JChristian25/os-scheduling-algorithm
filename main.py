#!/usr/bin/env python3
"""
CPU Scheduling Algorithm Showcaser
Demonstrates FCFS, SJF, Round Robin, and Multi-Level Queue scheduling
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.prompt import Prompt, IntPrompt, Confirm
from models.process import Process
from schedulers import FCFS, SJF, RoundRobin, MLQ
from core import SchedulingSimulator, ConsoleUI

console = Console()

def create_sample_processes():
    """Create sample processes for demonstration"""
    return [
        Process(pid="P1", arrival=0, burst=5, queue_level=0),
        Process(pid="P2", arrival=1, burst=3, queue_level=0),
        Process(pid="P3", arrival=2, burst=8, queue_level=1),
        Process(pid="P4", arrival=3, burst=6, queue_level=0),
        Process(pid="P5", arrival=4, burst=2, queue_level=2),
    ]

def create_custom_processes():
    """Get custom processes from user input"""
    processes = []
    
    console.clear()
    header = Text("CREATE CUSTOM PROCESSES", style="bold white on blue", justify="center")
    console.print(Panel(header, border_style="blue", padding=(1, 2)))
    console.print()
    
    try:
        n = IntPrompt.ask("[bold cyan]Number of processes[/bold cyan]", default=3, console=console)
        console.print()
        
        for i in range(n):
            console.print(f"[bold yellow]Process {i+1}:[/bold yellow]")
            
            pid = Prompt.ask("  [cyan]PID (e.g., P1)[/cyan]", default=f"P{i+1}", console=console)
            arrival = IntPrompt.ask("  [cyan]Arrival time[/cyan]", default=0, console=console)
            burst = IntPrompt.ask("  [cyan]Burst time[/cyan]", default=5, console=console)
            queue_level = IntPrompt.ask("  [cyan]Queue level (0-2)[/cyan]", default=0, console=console)
            queue_level = max(0, min(2, queue_level))
            
            processes.append(Process(pid=pid, arrival=arrival, burst=burst, queue_level=queue_level))
            console.print()
        
        return processes
    except Exception as e:
        console.print(f"\n[bold red]Error creating processes: {e}[/bold red]")
        return None

def select_scheduler():
    """Let user select scheduling algorithm"""
    console.clear()
    header = Text("SELECT SCHEDULING ALGORITHM", style="bold white on magenta", justify="center")
    console.print(Panel(header, border_style="magenta", padding=(1, 2)))
    console.print()
    
    table = Table(border_style="cyan", box=box.ROUNDED)
    table.add_column("Option", style="bold yellow", justify="center")
    table.add_column("Algorithm", style="cyan")
    table.add_column("Description", style="dim")
    
    table.add_row("1", "FCFS", "First Come First Served")
    table.add_row("2", "SJF", "Shortest Job First")
    table.add_row("3", "RR", "Round Robin")
    table.add_row("4", "MLQ", "Multi-Level Queue")
    
    console.print(table)
    console.print()
    
    choice = Prompt.ask("[bold cyan]Your choice[/bold cyan]", choices=["1", "2", "3", "4"], default="1", console=console)
    
    if choice == '1':
        console.print("[green]Selected: FCFS[/green]")
        return FCFS(), "FCFS"
    elif choice == '2':
        console.print("[green]Selected: SJF[/green]")
        return SJF(), "SJF"
    elif choice == '3':
        quantum = IntPrompt.ask("[cyan]Enter time quantum[/cyan]", default=2, console=console)
        console.print(f"[green]Selected: Round Robin (quantum={quantum})[/green]")
        return RoundRobin(quantum=quantum), f"Round Robin (quantum={quantum})"
    elif choice == '4':
        console.print("\n[bold yellow]Configuring Multi-Level Queue:[/bold yellow]")
        console.print("  [cyan]Queue 0: FCFS[/cyan]")
        console.print("  [cyan]Queue 1: SJF[/cyan]")
        console.print("  [cyan]Queue 2: Round Robin[/cyan]")
        console.print()
        quantum = IntPrompt.ask("[cyan]Enter time quantum for Queue 2[/cyan]", default=2, console=console)
        
        queues = [FCFS(), SJF(), RoundRobin(quantum=quantum)]
        console.print(f"[green]Selected: MLQ (FCFS, SJF, RR(q={quantum}))[/green]")
        return MLQ(queues=queues), f"MLQ (FCFS, SJF, RR(q={quantum}))"
    else:
        console.print("[yellow]Invalid choice, using FCFS[/yellow]")
        return FCFS(), "FCFS"

def display_menu():
    """Display main menu"""
    console.clear()
    console.print()
    header = Text("CPU SCHEDULING ALGORITHM SHOWCASER", style="bold white on blue", justify="center")
    console.print(Panel(header, border_style="blue", padding=(1, 2)))
    console.print()
    
    table = Table(border_style="cyan", box=box.ROUNDED)
    table.add_column("Option", style="bold yellow", justify="center")
    table.add_column("Action", style="cyan")
    
    table.add_row("1", "Run with sample processes")
    table.add_row("2", "Create custom processes")
    table.add_row("3", "Exit")
    
    console.print(table)
    console.print()
    
    return Prompt.ask("[bold cyan]Your choice[/bold cyan]", choices=["1", "2", "3"], default="1", console=console)


def main():
    """Main program entry point"""
    console.clear()
    
    welcome = Text("Welcome to the CPU Scheduling Algorithm Showcaser!", style="bold cyan", justify="center")
    console.print(Panel(welcome, border_style="cyan", padding=(1, 2)))
    console.input("\n[dim]Press ENTER to start...[/dim]")
    
    while True:
        choice = display_menu()
        
        if choice == '3':
            console.clear()
            goodbye = Text("Thank you for using the scheduler showcaser!", style="bold green", justify="center")
            console.print()
            console.print(Panel(goodbye, border_style="green", padding=(1, 2)))
            break
        
        # Select scheduler FIRST
        scheduler, scheduler_name = select_scheduler()
        
        # Then get processes
        if choice == '1':
            processes = create_sample_processes()
            console.clear()
            console.print()
            
            # Display sample processes in a table
            proc_table = Table(title="Sample Processes", border_style="cyan", box=box.ROUNDED)
            proc_table.add_column("PID", style="cyan bold", justify="center")
            proc_table.add_column("Arrival", style="magenta", justify="center")
            proc_table.add_column("Burst", style="yellow", justify="center")
            proc_table.add_column("Queue Level", style="green", justify="center")
            
            for p in processes:
                proc_table.add_row(p.pid, str(p.arrival), str(p.burst), str(p.queue_level))
            
            console.print(proc_table)
            console.print()
            console.input("[dim]Press ENTER to continue...[/dim]")
        elif choice == '2':
            processes = create_custom_processes()
            if not processes:
                continue
        else:
            console.print("[bold red]Invalid choice[/bold red]")
            continue
        
        # Create simulator
        # Need to reset processes for fresh simulation
        fresh_processes = [
            Process(p.pid, p.arrival, p.burst, p.priority, p.queue_level) 
            for p in processes
        ]
        simulator = SchedulingSimulator(scheduler, fresh_processes)
        
        # Create UI and run in interactive mode
        ui = ConsoleUI(simulator, scheduler_name=scheduler_name)
        ui.run_interactive()
        
        console.print()
        console.input("[dim]Press ENTER to continue...[/dim]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]Simulation interrupted by user.[/bold yellow]")
        console.input("\n[dim]Press ENTER to exit...[/dim]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        import traceback
        console.print_exception()
        console.input("\n[dim]Press ENTER to exit...[/dim]")
        sys.exit(1)

