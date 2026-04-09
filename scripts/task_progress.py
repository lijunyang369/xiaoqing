#!/usr/bin/env python3
from __future__ import annotations

from datetime import date, datetime, timezone


def parse_dt(value):
    if value in (None, 'null'):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    try:
        text = str(value)
        dt = datetime.fromisoformat(text.replace('Z', '+00:00'))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def compute_progress_icon(start, deadline, now=None):
    now = now or datetime.now(timezone.utc)
    if not start or not deadline or deadline <= start:
        return '-'
    ratio = (now - start).total_seconds() / (deadline - start).total_seconds()
    if ratio < 1 / 3:
        return '🟩'
    if ratio < 2 / 3:
        return '🟨'
    if ratio < 1:
        return '🟥'
    return '⬛'
