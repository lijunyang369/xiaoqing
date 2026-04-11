#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path('/home/lijunyang/.openclaw/workspace')
REGISTRY = ROOT / 'config' / 'agent-role-registry.json'


def load_registry():
    return json.loads(REGISTRY.read_text(encoding='utf-8'))


def build_task(role: str, body: str) -> str:
    registry = load_registry()
    roles = registry.get('roles', {})
    if role not in roles:
        valid = ', '.join(sorted(roles.keys()))
        raise SystemExit(f'Unknown role: {role}. Valid roles: {valid}')

    protocol = roles[role].get('protocol')
    if not protocol:
        raise SystemExit(f'Role {role} has no protocol path in registry')

    return f"请先阅读 `{protocol}`，然后执行以下任务：\n\n{body.strip()}"


def main():
    if len(sys.argv) < 3:
        raise SystemExit('Usage: build_spawn_task.py <role> <task-body>')

    role = sys.argv[1]
    body = ' '.join(sys.argv[2:])
    print(build_task(role, body))


if __name__ == '__main__':
    main()
