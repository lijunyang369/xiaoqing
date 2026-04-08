#!/bin/bash
set -euo pipefail

openclaw gateway status >/dev/null 2>&1 || exit 1
python3 /home/lijunyang/.openclaw/workspace/scripts/render_boot_reply.py
