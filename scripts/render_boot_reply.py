#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

home = Path.home() / '.openclaw'
runs_file = home / 'subagents' / 'runs.json'
tasks_dir = home / 'workspace' / 'tasks'


try:
    from task_progress import parse_dt, compute_progress_icon
except Exception:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from task_progress import parse_dt, compute_progress_icon


def load_interrupted():
    if not runs_file.exists():
        return []
    try:
        runs = json.loads(runs_file.read_text()).get('runs', {}) or {}
        return [
            run.get('label') or run.get('task') or '未知任务'
            for run in runs.values()
            if not run.get('endedAt')
        ]
    except Exception:
        return []


def load_rows():
    progress_order = {
        '⬛': 0,
        '🟥': 1,
        '🟨': 2,
        '🟩': 3,
        '-': 4,
    }
    rows = []
    now = datetime.now(timezone.utc)
    if yaml is None or not tasks_dir.exists():
        return rows
    for path in sorted(tasks_dir.glob('*.yaml')):
        try:
            task = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        except Exception:
            continue
        if task.get('status') == 'Done':
            continue
        title = task.get('title') or path.stem
        status = task.get('status') or '-'
        agent = task.get('assignedRole') or '未分配'
        start = parse_dt(task.get('startedAt') or task.get('createdAt'))
        deadline = parse_dt(task.get('deadline'))
        progress = compute_progress_icon(start, deadline, now)
        priority_score = task.get('priorityScore')
        try:
            priority_score = int(priority_score)
        except Exception:
            priority_score = 999
        rows.append((
            progress_order.get(progress, 99),
            deadline is None,
            deadline or datetime.max.replace(tzinfo=timezone.utc),
            -priority_score,
            title,
            status,
            progress,
            agent,
        ))
    rows.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4]))
    return rows


def main():
    interrupted = load_interrupted()
    if interrupted:
        recovery_status = f'发现 {len(interrupted)} 个任务但未自动恢复'
        recovered_tasks = '无'
        not_recovered = '，'.join(interrupted)
    else:
        recovery_status = '未发现需恢复任务'
        recovered_tasks = '无'
        not_recovered = '无'

    print('## Boot恢复回复')
    print()
    print('### 任务恢复说明')
    print(f'- 恢复状态: {recovery_status}')
    print(f'- 恢复任务: {recovered_tasks}')
    print(f'- 未自动恢复: {not_recovered}')
    print()
    print('### 任务状态表格')
    print('| 任务Title | 状态 | 进度 | 执行Agent |')
    print('|---|---|---|---|')
    for *_, title, status, progress, agent in load_rows():
        print(f'| {title} | {status} | {progress} | {agent} |')


if __name__ == '__main__':
    main()
