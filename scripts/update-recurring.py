#!/usr/bin/env python3
"""
Update recurring tasks that have been marked as completed.

For each recurring task WITH a completed: field:
1. Calculate next due date based on recurrence type
2. Update due: field in frontmatter
3. Remove completed: field from frontmatter
4. Add completion entry to ## History section

Recurring tasks WITHOUT completed: field are NOT touched,
even if overdue - they should appear in "Atrasadas" until
the user explicitly marks them as done.
"""

import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path

from config import get_folder


def calculate_next_due(current_due, recurrence, recurrence_day=None):
    """Calculate next due date based on recurrence type."""
    today = datetime.now().date()
    due_date = datetime.strptime(current_due, '%Y-%m-%d').date()

    if recurrence == 'daily':
        next_due = due_date + timedelta(days=1)
    elif recurrence == 'weekly':
        next_due = due_date + timedelta(weeks=1)
    elif recurrence == 'biweekly':
        next_due = due_date + timedelta(weeks=2)
    elif recurrence == 'monthly':
        if recurrence_day:
            next_due = due_date + relativedelta(months=1)
            try:
                next_due = next_due.replace(day=int(recurrence_day))
            except ValueError:
                pass
        else:
            next_due = due_date + relativedelta(months=1)
    elif recurrence == 'quarterly':
        next_due = due_date + relativedelta(months=3)
    elif recurrence == 'yearly':
        next_due = due_date + relativedelta(years=1)
    else:
        next_due = due_date + timedelta(weeks=1)

    # If next_due is still in the past, keep advancing until it's in the future
    while next_due <= today:
        if recurrence == 'daily':
            next_due += timedelta(days=1)
        elif recurrence == 'weekly':
            next_due += timedelta(weeks=1)
        elif recurrence == 'biweekly':
            next_due += timedelta(weeks=2)
        elif recurrence == 'monthly':
            next_due += relativedelta(months=1)
        elif recurrence == 'quarterly':
            next_due += relativedelta(months=3)
        elif recurrence == 'yearly':
            next_due += relativedelta(years=1)
        else:
            next_due += timedelta(weeks=1)

    return next_due.strftime('%Y-%m-%d')


def parse_frontmatter(content):
    """Parse YAML frontmatter from content."""
    if not content.startswith('---'):
        return None, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    frontmatter = parts[1].strip()
    body = parts[2]

    return frontmatter, body


def update_frontmatter(frontmatter, new_due):
    """Update due: field and remove completed: field from frontmatter."""
    lines = frontmatter.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('due:'):
            new_lines.append(f'due: {new_due}')
        elif line.startswith('completed:'):
            # Remove completed: field
            continue
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)


def add_history_entry(body, completed_date):
    """Add completion entry to History section."""
    history_pattern = r'(## History\n)(.*?)(?=\n## |\Z)'

    if '## History' in body:
        def replace_history(match):
            header = match.group(1)
            existing = match.group(2)
            new_entry = f'- {completed_date}: Completado\n'
            return header + new_entry + existing

        body = re.sub(history_pattern, replace_history, body, flags=re.DOTALL)
    else:
        body = body.rstrip() + f'\n\n## History\n- {completed_date}: Completado\n'

    return body


def process_recurring_tasks():
    """Process recurring tasks that have been marked as completed."""
    tasks_dir = get_folder("tasks")
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')

    updated = []

    for task_file in tasks_dir.glob('*.md'):
        content = task_file.read_text()

        frontmatter, body = parse_frontmatter(content)
        if not frontmatter:
            continue

        # Must be a recurring task
        if 'recurrence:' not in frontmatter:
            continue

        # Must have completed: field (user marked it as done)
        if 'completed:' not in frontmatter:
            continue

        # Extract completed date
        completed_match = re.search(r'^completed:\s*(\d{4}-\d{2}-\d{2})', frontmatter, re.MULTILINE)
        if not completed_match:
            continue

        completed_date = completed_match.group(1)

        # Extract due date
        due_match = re.search(r'^due:\s*(\d{4}-\d{2}-\d{2})', frontmatter, re.MULTILINE)
        if not due_match:
            continue

        due_str = due_match.group(1)

        # Extract recurrence type
        recurrence_match = re.search(r'^recurrence:\s*(\w+)', frontmatter, re.MULTILINE)
        if not recurrence_match:
            continue

        recurrence = recurrence_match.group(1).lower()

        # Extract recurrence_day if present
        recurrence_day = None
        day_match = re.search(r'^recurrence_day:\s*(\d+)', frontmatter, re.MULTILINE)
        if day_match:
            recurrence_day = day_match.group(1)

        # Calculate next due date
        next_due = calculate_next_due(due_str, recurrence, recurrence_day)

        # Update frontmatter (new due, remove completed)
        new_frontmatter = update_frontmatter(frontmatter, next_due)

        # Add history entry
        new_body = add_history_entry(body, completed_date)

        # Write updated content
        new_content = f'---\n{new_frontmatter}\n---{new_body}'
        task_file.write_text(new_content)

        updated.append({
            'file': task_file.name,
            'completed': completed_date,
            'new_due': next_due,
            'recurrence': recurrence
        })

    return updated


def main():
    """Main function."""
    print("Checking completed recurring tasks...")

    updated = process_recurring_tasks()

    if updated:
        print(f"Updated {len(updated)} recurring task(s):\n")
        for task in updated:
            print(f"  - {task['file']}")
            print(f"    Completada: {task['completed']} → Próxima: {task['new_due']} ({task['recurrence']})")
    else:
        print("No completed recurring tasks to update.")

    return updated


if __name__ == "__main__":
    main()
