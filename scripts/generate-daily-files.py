#!/usr/bin/env python3
"""
Generate today.md, this-week.md, and next-week.md files.

This script:
1. Normalizes dates in all task files
2. Calculates current week and next week dates
3. Archives completed tasks (moves them to completed/ folder)
4. Greps for tasks by specific dates
5. Generates the three daily files
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Import config and dates from same directory
from config import get_tasks_root, get_folder, get_link_format
from dates import get_week_dates

# Get directories from config
BASE_DIR = get_tasks_root()
TASKS_DIR = get_folder("tasks")
IDEAS_DIR = get_folder("ideas")
SCRIPTS_DIR = Path(__file__).parent

# Spanish translations
DIAS_SEMANA = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

MESES = {
    'January': 'enero',
    'February': 'febrero',
    'March': 'marzo',
    'April': 'abril',
    'May': 'mayo',
    'June': 'junio',
    'July': 'julio',
    'August': 'agosto',
    'September': 'septiembre',
    'October': 'octubre',
    'November': 'noviembre',
    'December': 'diciembre'
}

def run_command(cmd, cwd=None):
    """Run a shell command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd or BASE_DIR,
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def normalize_dates():
    """Run the normalize-dates.py script."""
    print("Normalizing dates...")
    stdout, stderr, code = run_command(f"python3 {SCRIPTS_DIR}/normalize-dates.py")
    print(stdout)
    if stderr:
        print(f"Error: {stderr}", file=sys.stderr)

def calculate_weeks():
    """Get week dates from dates module."""
    print("Calculating week dates...")
    dates = get_week_dates()
    print(f"Today: {dates['today_weekday']}, {dates['today_formatted']} ({dates['today']})")
    print(f"This week: {dates['this_week_start']} to {dates['this_week_end']}")
    print(f"Next week: {dates['next_week_start']} to {dates['next_week_end']}")
    return dates

def archive_completed_tasks():
    """Run the archive-tasks.py script."""
    print("\nArchiving completed tasks...")
    stdout, stderr, code = run_command(f"python3 {SCRIPTS_DIR}/archive-tasks.py")
    if stdout:
        # Skip the header line from archive-tasks.py since we already printed one
        lines = stdout.split('\n')
        for line in lines:
            if not line.startswith("==="):
                print(line)
    if stderr:
        print(f"Error: {stderr}", file=sys.stderr)

def get_tasks_for_date(date):
    """Get all tasks with a specific due date, excluding research tasks."""
    stdout, stderr, code = run_command(
        f"grep -l '^due: {date}$' *.md 2>/dev/null || true",
        cwd=TASKS_DIR
    )

    if not stdout:
        return []

    # Extract just the filenames without path and extension, excluding research tasks
    files = []
    for filename in stdout.split('\n'):
        if not filename:
            continue

        file_path = TASKS_DIR / filename

        # Check if this is a research task (has research-review or research-summary-needed tag)
        # Handle both single-line and multi-line YAML formats
        tags_stdout, _, _ = run_command(f"grep -E '^tags:|^  - research' \"{file_path}\"")
        if tags_stdout and ('research-review' in tags_stdout or 'research-summary-needed' in tags_stdout):
            continue  # Skip research tasks

        files.append(Path(filename).stem)

    return files

def get_overdue_tasks(today):
    """Get all overdue tasks (due before today), excluding research tasks."""
    # This is trickier - we need to grep for dates before today
    # For simplicity, grep for any due: field, then filter
    stdout, stderr, code = run_command(
        f"grep -h '^due: ' *.md 2>/dev/null || true",
        cwd=TASKS_DIR
    )

    if not stdout:
        return []

    # Now get the files for dates before today
    overdue = []
    today_date = datetime.strptime(today, '%Y-%m-%d')

    # Get all task files and check their dates
    stdout, stderr, code = run_command(
        f"grep -l '^due: ' *.md 2>/dev/null || true",
        cwd=TASKS_DIR
    )

    if not stdout:
        return []

    for filename in stdout.split('\n'):
        if not filename:
            continue

        file_path = TASKS_DIR / filename

        # Check if this is a research task (has research-review or research-summary-needed tag)
        # Handle both single-line and multi-line YAML formats
        tags_stdout, _, _ = run_command(f"grep -E '^tags:|^  - research' \"{file_path}\"")
        if tags_stdout and ('research-review' in tags_stdout or 'research-summary-needed' in tags_stdout):
            continue  # Skip research tasks

        # Get the due date from this file
        date_stdout, _, _ = run_command(f"grep '^due: ' \"{file_path}\"")
        if date_stdout:
            due_date_str = date_stdout.split('due: ')[1].strip()
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                if due_date < today_date:
                    filename = Path(file_path).stem
                    overdue.append((filename, due_date_str))
            except ValueError:
                # Invalid date format, skip
                pass

    return overdue

def get_research_tasks():
    """Get all research tasks (research-review or research-summary-needed tags)."""
    # Get files with research tags
    stdout, stderr, code = run_command(
        f"grep -l 'research-review\\|research-summary-needed' *.md 2>/dev/null || true",
        cwd=TASKS_DIR
    )

    if not stdout:
        return []

    files = []
    for filename in stdout.split('\n'):
        if filename:
            files.append(Path(filename).stem)

    return files

def get_in_progress_ideas():
    """Get all ideas with status: in progress."""
    stdout, stderr, code = run_command(
        f"grep -l '^status: in progress$' *.md 2>/dev/null || true",
        cwd=IDEAS_DIR
    )

    if not stdout:
        return []

    files = []
    for filename in stdout.split('\n'):
        if filename:
            files.append(Path(filename).stem)

    return files

def generate_days_between(start_date, end_date):
    """Generate list of dates between start and end (inclusive)."""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)

    return days

def format_date_header(date):
    """Format date as 'Lunes, 12 de enero' (Spanish)."""
    weekday_en = date.strftime('%A')
    month_en = date.strftime('%B')
    day = date.day

    weekday_es = DIAS_SEMANA.get(weekday_en, weekday_en)
    month_es = MESES.get(month_en, month_en)

    return f"{weekday_es}, {day} de {month_es}"

def format_week_range(start_date, end_date):
    """Format week range as 'del 5 al 11 de enero' (Spanish)."""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    start_month_es = MESES.get(start.strftime('%B'), start.strftime('%B'))
    end_month_es = MESES.get(end.strftime('%B'), end.strftime('%B'))

    if start_month_es == end_month_es:
        return f"del {start.day} al {end.day} de {end_month_es}"
    else:
        return f"del {start.day} de {start_month_es} al {end.day} de {end_month_es}"


def format_link(filename, folder=None):
    """Format a link based on the configured link format."""
    link_format = get_link_format()
    if link_format == "markdown":
        if folder:
            return f"[{filename}]({folder}/{filename}.md)"
        return f"[{filename}]({filename}.md)"
    else:
        # Default to obsidian wiki-links
        return f"[[{filename}]]"

def generate_today_md(dates):
    """Generate today.md file."""
    print("\nGenerating today.md...")

    today = dates['today']
    today_datetime = datetime.strptime(today, '%Y-%m-%d')

    # Get tasks
    overdue = get_overdue_tasks(today)
    due_today = get_tasks_for_date(today)
    research = get_research_tasks()
    ideas = get_in_progress_ideas()

    # Generate content
    content = f"---\ndate: {today}\n---\n"
    content += f"# Hoy - {format_date_header(today_datetime)}\n\n"

    if overdue:
        content += "## Atrasadas\n"
        for filename, due_date in overdue:
            content += f"- [ ] {format_link(filename, 'tasks')} (due: {due_date})\n"
        content += "\n"

    content += "## Tareas\n"
    if due_today:
        for filename in due_today:
            content += f"- [ ] {format_link(filename, 'tasks')}\n"
    content += "\n"

    if ideas:
        content += "## Ideas en progreso\n"
        for filename in ideas:
            content += f"- {format_link(filename, 'ideas')}\n"
        content += "\n"

    if research:
        content += "## Investigación\n"
        for filename in research:
            content += f"- [ ] {format_link(filename, 'tasks')}\n"

    # Write file
    with open(BASE_DIR / "today.md", 'w') as f:
        f.write(content)

    print(f"  - {len(overdue)} overdue task(s)")
    print(f"  - {len(due_today)} task(s) due today")
    print(f"  - {len(research)} research task(s)")
    print(f"  - {len(ideas)} in-progress idea(s)")

def generate_this_week_md(dates):
    """Generate this-week.md file."""
    print("\nGenerating this-week.md...")

    # Get dates
    today = dates['today']
    tomorrow = dates['tomorrow']
    week_start = dates['this_week_start']
    week_end = dates['this_week_end']

    # Check if there are any days left this week
    tomorrow_date = datetime.strptime(tomorrow, '%Y-%m-%d')
    week_end_date = datetime.strptime(week_end, '%Y-%m-%d')

    # Get overdue tasks
    overdue = get_overdue_tasks(today)

    if tomorrow_date > week_end_date:
        print("  - No days remaining this week")
        content = f"---\nweek_start: {week_start}\nweek_end: {week_end}\n---\n"
        content += f"# Esta semana - Semana {format_week_range(week_start, week_end)}\n\n"
        if overdue:
            content += "## Atrasadas\n"
            for filename, due_date in overdue:
                content += f"- [ ] {format_link(filename, 'tasks')} (due: {due_date})\n"
            content += "\n"
        content += "No quedan tareas esta semana.\n"
        with open(BASE_DIR / "this-week.md", 'w') as f:
            f.write(content)
        return

    # Get days between tomorrow and week end
    days = generate_days_between(tomorrow, week_end)

    # Generate content
    content = f"---\nweek_start: {week_start}\nweek_end: {week_end}\n---\n"
    content += f"# Esta semana - Semana {format_week_range(week_start, week_end)}\n\n"

    # Add overdue section if there are overdue tasks
    if overdue:
        content += "## Atrasadas\n"
        for filename, due_date in overdue:
            content += f"- [ ] {format_link(filename, 'tasks')} (due: {due_date})\n"
        content += "\n"

    total_tasks = 0
    for day in days:
        day_str = day.strftime('%Y-%m-%d')
        tasks = get_tasks_for_date(day_str)

        if tasks:
            content += f"## {format_date_header(day)}\n"
            for filename in tasks:
                content += f"- [ ] {format_link(filename, 'tasks')}\n"
            content += "\n"
            total_tasks += len(tasks)

    # Write file
    with open(BASE_DIR / "this-week.md", 'w') as f:
        f.write(content)

    print(f"  - {total_tasks} task(s) across {len(days)} day(s)")

def generate_next_week_md(dates):
    """Generate next-week.md file."""
    print("\nGenerating next-week.md...")

    # Get dates
    today = dates['today']
    week_start = dates['next_week_start']
    week_end = dates['next_week_end']

    # Get overdue tasks
    overdue = get_overdue_tasks(today)

    # Get days
    days = generate_days_between(week_start, week_end)

    # Generate content
    content = f"---\nweek_start: {week_start}\nweek_end: {week_end}\n---\n"
    content += f"# Próxima semana - Semana {format_week_range(week_start, week_end)}\n\n"

    # Add overdue section if there are overdue tasks
    if overdue:
        content += "## Atrasadas\n"
        for filename, due_date in overdue:
            content += f"- [ ] {format_link(filename, 'tasks')} (due: {due_date})\n"
        content += "\n"

    total_tasks = 0
    for day in days:
        day_str = day.strftime('%Y-%m-%d')
        tasks = get_tasks_for_date(day_str)

        if tasks:
            content += f"## {format_date_header(day)}\n"
            for filename in tasks:
                content += f"- [ ] {format_link(filename, 'tasks')}\n"
            content += "\n"
            total_tasks += len(tasks)

    # Write file
    with open(BASE_DIR / "next-week.md", 'w') as f:
        f.write(content)

    print(f"  - {total_tasks} task(s) across {len(days)} day(s)")

def main():
    """Main function."""
    print("=== Generating Daily Task Files ===\n")

    # Step 1: Normalize dates
    normalize_dates()

    # Step 2: Calculate weeks
    dates = calculate_weeks()

    # Step 3: Archive completed tasks
    archive_completed_tasks()

    # Step 4: Generate files
    generate_today_md(dates)
    generate_this_week_md(dates)
    generate_next_week_md(dates)

    print("\n=== Done! ===")

if __name__ == "__main__":
    main()
