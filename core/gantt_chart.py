from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

class GanttChart:

    @staticmethod
    def generate(gantt_data, width=80, console=None):
        """
        Generate a text-based Gantt chart using Rich
        
        Args:
            gantt_data: List of dicts with 'pid', 'start', 'end'
            width: Maximum width of the chart
            console: Rich Console instance
        """
        if not gantt_data:
            return "No data to display"
        
        if console is None:
            console = Console()
        
        total_time = gantt_data[-1]['end']
        
        # Create visual timeline
        timeline = Text()
        
        # Color mapping for different processes
        colors = ['cyan', 'magenta', 'green', 'yellow', 'blue', 'red']
        pid_color_map = {}
        color_idx = 0
        
        for entry in gantt_data:
            pid = entry['pid']
            duration = entry['end'] - entry['start']
            
            # Assign color to process
            if pid not in pid_color_map:
                if pid == 'IDLE':
                    pid_color_map[pid] = 'dim white'
                else:
                    pid_color_map[pid] = colors[color_idx % len(colors)]
                    color_idx += 1
            
            # Create process block
            if duration > 0:
                block_text = str(pid).center(duration * 2)
                timeline.append(f"|{block_text}", style=f"bold {pid_color_map[pid]}")
        
        timeline.append("|", style="bold white")
        
        # Time markers
        time_text = Text()
        for entry in gantt_data:
            time_str = str(entry['start']).ljust((entry['end'] - entry['start']) * 2)
            time_text.append(time_str, style="dim cyan")
        time_text.append(str(gantt_data[-1]['end']), style="dim cyan")
        
        # Combine into panel
        gantt_display = Text()
        gantt_display.append_text(timeline)
        gantt_display.append("\n")
        gantt_display.append_text(time_text)
        
        console.print(Panel(gantt_display, title="Gantt Chart", border_style="blue", box=box.ROUNDED))
        
        return ""
    
    @staticmethod
    def generate_detailed(gantt_data, console=None):
        """Generate a detailed Gantt chart with exact timings using Rich"""
        if not gantt_data:
            return "No data to display"
        
        if console is None:
            console = Console()
        
        table = Table(title="Detailed Gantt Chart", border_style="blue", box=box.DOUBLE_EDGE)
        table.add_column("Process", style="cyan bold", justify="center")
        table.add_column("Start", style="magenta", justify="center")
        table.add_column("End", style="magenta", justify="center")
        table.add_column("Duration", style="green", justify="center")
        
        # Color mapping
        colors = ['cyan', 'magenta', 'green', 'yellow', 'blue', 'red']
        pid_color_map = {}
        color_idx = 0
        
        for entry in gantt_data:
            # Skip context switch markers in detailed view
            if entry.get('is_context_switch', False):
                continue
                
            pid = str(entry['pid'])
            start = entry['start']
            end = entry['end']
            duration = end - start
            
            # Assign color
            if pid not in pid_color_map:
                if pid == 'IDLE':
                    pid_color_map[pid] = 'dim white'
                else:
                    pid_color_map[pid] = colors[color_idx % len(colors)]
                    color_idx += 1
            
            # Color the PID
            colored_pid = f"[bold {pid_color_map[pid]}]{pid}[/bold {pid_color_map[pid]}]"
            
            table.add_row(
                colored_pid,
                str(start),
                str(end),
                str(duration)
            )
        
        console.print(table)
        return ""
    
    @staticmethod
    def generate_compact(gantt_data, console=None):
        """Generate a compact visual Gantt chart using Rich"""
        if not gantt_data:
            return "No data to display"
        
        if console is None:
            console = Console()
        
        # Color mapping for different processes
        colors = ['cyan', 'magenta', 'green', 'yellow', 'blue', 'red']
        pid_color_map = {}
        color_idx = 0
        
        chart_line = Text()
        time_positions = []
        current_pos = 0
        
        for entry in gantt_data:
            pid = str(entry['pid'])
            duration = entry['end'] - entry['start']
            
            # Assign color to process
            if pid not in pid_color_map:
                if pid == 'IDLE':
                    pid_color_map[pid] = 'dim white'
                else:
                    pid_color_map[pid] = colors[color_idx % len(colors)]
                    color_idx += 1
            
            # Create compact representation
            if duration == 1:
                block = f"[{pid[0] if pid else ' '}]"
            else:
                block = f"[{pid.center(min(len(pid) + 2, duration * 3 - 2))}]"
            
            chart_line.append(block, style=f"bold {pid_color_map[pid]}")
            
            # Track time positions
            time_positions.append((entry['start'], current_pos))
            current_pos += len(block)
        
        # Add final time
        time_positions.append((gantt_data[-1]['end'], current_pos))
        
        # Create time line
        time_line = Text()
        last_pos = 0
        for time_val, pos in time_positions:
            spacing = pos - last_pos
            time_line.append(str(time_val).ljust(spacing), style="dim cyan")
            last_pos = pos + len(str(time_val))
        
        # Display in panel
        display = Text()
        display.append_text(chart_line)
        display.append("\n")
        display.append_text(time_line)
        
        console.print(Panel(display, title="Compact Gantt Chart", border_style="yellow", box=box.ROUNDED))
        
        return ""

