#!/usr/bin/env python3
"""
Update recurring tasks that are due today or overdue.

For each recurring task:
1. Check if due date is today or in the past
2. Calculate next due date based on recurrence type
3. Update due: field in frontmatter
4. Add completion entry to ## History section
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
            # Use specific day of month
            next_due = due_date + relativedelta(months=1)
            try:
                next_due = next_due.replace(day=int(recurrence_day))
            except ValueError:
                # Day doesn't exist in month (e.g., 31 in February)
                pass
        else:
            next_due = due_date + relativedelta(months=1)
    elif recurrence == 'quarterly':
        next_due = due_date + relativedelta(months=3)
    elif recurrence == 'yearly':
        next_due = due_date + relativedelta(years=1)
    else:
        # Unknown recurrence, default to weekly
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


def update_frontmatter_due(frontmatter, new_due):
    """Update due: field in frontmatter."""
    lines = frontmatter.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('due:'):
            new_lines.append(f'due: {new_due}')
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)


def add_history_entry(body, completed_date):
    """Add completion entry to History section."""
    history_pattern = r'(## History\n)(.*?)(?=\n## |\Z)'

    if '## History' in body:
        # Add entry after ## History heading
        def replace_history(match):
            header = match.group(1)
            existing = match.group(2)
            new_entry = f'- {completed_date}: Completado\n'
            return header + new_entry + existing

        body = re.sub(history_pattern, replace_history, body, flags=re.DOTALL)
    else:
        # Create History section at the end
        body = body.rstrip() + f'\n\n## History\n- {completed_date}: Completado\n'

    return body


def process_recurring_tasks():
    """Process all recurring tasks and update those that are due."""
    tasks_dir = get_folder("tasks")
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')

    updated = []

    # Find all markdown files in tasks/
    for task_file in tasks_dir.glob('*.md'):
        content = task_file.read_text()

        frontmatter, body = parse_frontmatter(content)
        if not frontmatter:
            continue

        # Check if it's a recurring task
        if 'recurrence:' not in frontmatter:
            continue

        # Extract due date
        due_match = re.search(r'^due:\s*(\d{4}-\d{2}-\d{2})', frontmatter, re.MULTILINE)
        if not due_match:
            continue

        due_str = due_match.group(1)
        due_date = datetime.strptime(due_str, '%Y-%m-%d').date()

        # Skip if due date is in the future
        if due_date > today:
            continue

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

        # Update frontmatter
        new_frontmatter = update_frontmatter_due(frontmatter, next_due)

        # Add history entry
        new_body = add_history_entry(body, due_str)

        # Write updated content
        new_content = f'---\n{new_frontmatter}\n---{new_body}'
        task_file.write_text(new_content)

        updated.append({
            'file': task_file.name,
            'old_due': due_str,
            'new_due': next_due,
            'recurrence': recurrence
        })

    return updated


def main():
    """Main function."""
    print("Checking recurring tasks...")

    updated = process_recurring_tasks()

    if updated:
        print(f"Updated {len(updated)} recurring task(s):\n")
        for task in updated:
            print(f"  - {task['file']}")
            print(f"    {task['old_due']} → {task['new_due']} ({task['recurrence']})")
    else:
        print("No recurring tasks needed updating.")

    return updated


if __name__ == "__main__":
    main()
