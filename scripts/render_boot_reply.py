#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from pathlib import Path

home = Path.home() / '.openclaw'
runs_file = home / 'subagents' / 'runs.json'
tasks_dir = home / 'workspace' / 'tasks' / 'active'


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


def parse_markdown_task(content):
    """从Markdown任务文件中解析字段"""
    task = {}
    
    # 解析ID和名称
    id_match = re.search(r'- ID: (.+)', content)
    if id_match:
        task['id'] = id_match.group(1).strip()
    
    name_match = re.search(r'- 名称: (.+)', content)
    if name_match:
        task['title'] = name_match.group(1).strip()
    
    status_match = re.search(r'- 状态: (.+)', content)
    if status_match:
        task['status'] = status_match.group(1).strip()
    
    agent_match = re.search(r'- 负责人: (.+)', content)
    if agent_match:
        task['agent'] = agent_match.group(1).strip()
    
    created_match = re.search(r'- 创建时间: (.+)', content)
    if created_match:
        task['createdAt'] = created_match.group(1).strip()
    
    deadline_match = re.search(r'- 截止时间: (.+)', content)
    if deadline_match:
        deadline_str = deadline_match.group(1).strip()
        if deadline_str != '未设置':
            task['deadline'] = deadline_str
    
    return task


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
    
    if not tasks_dir.exists():
        return rows
    
    for path in sorted(tasks_dir.glob('*.md')):
        try:
            content = path.read_text(encoding='utf-8')
            task = parse_markdown_task(content)
        except Exception:
            continue
        
        # 跳过已完成的任务
        status = task.get('status', '')
        if status in ['Done', 'Completed']:
            continue
        
        title = task.get('title') or path.stem
        agent = task.get('agent') or '未分配'
        
        # 解析时间
        start = parse_dt(task.get('createdAt'))
        deadline = parse_dt(task.get('deadline'))
        
        # 计算进度
        progress = compute_progress_icon(start, deadline, now)
        
        # 优先级处理（简化，从文件名或内容中提取）
        priority_score = 999  # 默认低优先级
        
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

    rows = load_rows()

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
    if not rows:
        print('| 无 | - | - | - |')
        return
    for *_, title, status, progress, agent in rows:
        print(f'| {title} | {status} | {progress} | {agent} |')


if __name__ == '__main__':
    main()
