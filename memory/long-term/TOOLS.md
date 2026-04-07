# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Browser / Chrome Relay

- 运行结构：Windows 11 宿主机 + WSL 内 OpenClaw。
- 默认安全路径：公开页 / 无登录页优先走 WSL 自管浏览器（`openclaw` profile）。
- 真实 Windows 浏览器态：优先走 `chrome-relay` remote CDP。
- 当前已验证可用端点：`http://172.31.208.1:9223`。
- 诊断顺序固定：Windows 本地 CDP → WSL `curl` 到端点 → `openclaw browser --browser-profile chrome-relay status/tabs` → 最小浏览器烟雾测试。
- Windows 侧接口探测优先用 `curl.exe`，避免 PowerShell `curl` 别名带来的交互干扰。
- 旧的 `9222` 直连尝试与 `18792` 临时转发层不作为当前默认维护路径。
