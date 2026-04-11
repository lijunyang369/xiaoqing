#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path
import re

ROOT = Path('/home/lijunyang/.openclaw/workspace')
TASKS_MD = ROOT / 'TASKS.md'
ACTIVE_DIR = ROOT / 'tasks' / 'active'


def today_str():
    return datetime.now().strftime('%Y-%m-%d')


def next_task_id():
    prefix = datetime.now().strftime('T-%Y%m%d-')
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    nums = []
    for path in ACTIVE_DIR.glob(f'{prefix}*.md'):
        m = re.match(rf'{re.escape(prefix)}(\d+)$', path.stem)
        if m:
            nums.append(int(m.group(1)))
    n = max(nums, default=0) + 1
    return f'{prefix}{n:03d}'


def normalize_priority(priority: str) -> str:
    p = (priority or 'P1').upper()
    return p if p in {'P0', 'P1', 'P2', 'P3'} else 'P1'


def write_task_card(task_id: str, title: str, owner: str, priority: str, next_step: str, detail: str = ''):
    path = ACTIVE_DIR / f'{task_id}.md'
    content = f"""# TaskCard
- ID: {task_id}
- 名称: {title}
- 状态: Executing
- 优先级: {priority}
- 负责人: {owner}
- 创建时间: {today_str()}
- 截止时间: 未设置
- 进度: 0%
- 下一步: {next_step}
"""
    if detail:
        content += f"\n## 详细信息\n- **目标**: {detail}\n"
    path.write_text(content, encoding='utf-8')
    return path


def update_tasks_md(task_id: str, title: str, owner: str, priority: str, next_step: str):
    if not TASKS_MD.exists():
        TASKS_MD.write_text(
            "# 任务总览\n\n最后更新: {0}\n\n## 进行中任务\n\n| ID | 名称 | 状态 | 优先级 | 负责人 | 创建时间 | 截止时间 | 进度 | 下一步 |\n|----|------|------|--------|--------|----------|----------|------|--------|\n| *暂无* | | | | | | | | |\n\n## 已完成任务\n\n| ID | 名称 | 状态 | 完成时间 | 负责人 |\n|----|------|------|----------|--------|\n| *暂无* | | | | |\n".format(today_str()),
            encoding='utf-8'
        )

    content = TASKS_MD.read_text(encoding='utf-8')
    content = re.sub(r'最后更新: .*', f'最后更新: {today_str()} {datetime.now().strftime("%H:%M")}', content, count=1)
    row = f'| {task_id} | {title} | Executing | {priority} | {owner} | {today_str()} | 未设置 | 0% | {next_step} |'

    placeholder = '| *暂无* | | | | | | | | |'
    if placeholder in content:
        content = content.replace(placeholder, row)
    elif row not in content:
        marker = '|----|------|------|--------|--------|----------|----------|------|--------|'
        content = content.replace(marker, marker + '\n' + row, 1)

    TASKS_MD.write_text(content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Create a new active task card and attach it to TASKS.md')
    parser.add_argument('title')
    parser.add_argument('--owner', default='小青')
    parser.add_argument('--priority', default='P1')
    parser.add_argument('--next-step', default='继续推进')
    parser.add_argument('--detail', default='')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    task_id = next_task_id()
    priority = normalize_priority(args.priority)

    if args.dry_run:
        print(task_id)
        print(args.title)
        return

    path = write_task_card(task_id, args.title, args.owner, priority, args.next_step, args.detail)
    update_tasks_md(task_id, args.title, args.owner, priority, args.next_step)
    print(path)


if __name__ == '__main__':
    main()
