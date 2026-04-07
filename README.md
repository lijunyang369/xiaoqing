# OpenClaw Workspace

重新组织后的工作区目录结构。

## 目录说明

- `memory/` - 记忆层
  - `long-term/` - 长期记忆（MEMORY.md, TASKS.md, TOOLS.md, IDENTITY.md, SOUL.md, USER.md）
  - `daily/` - 每日记忆（YYYY-MM-DD.md）
- `projects/` - 项目代码
  - `graphrag-mvp/` - GraphRAG MVP 项目
  - `xiaoqing/` - 其他项目
- `skills/` - 技能文件
- `scripts/` - 工具脚本
- `config/` - 配置文件模板
- `docs/` - 文档
- `tmp/` - 临时文件（不同步）
- `old-workspaces/` - 旧工作区备份（不同步）

## 同步策略

通过 Git 同步以下目录：
- `memory/`
- `projects/`（除虚拟环境）
- `skills/`
- `scripts/`
- `config/`（模板）
- `docs/`

不同步：
- `tmp/`
- `old-workspaces/`
- `projects/graphrag-mvp/env/`（虚拟环境）
- 其他设备特定文件

## 多设备使用

1. 克隆仓库到 `~/.openclaw/workspace`
2. 设置环境变量（API 密钥等）
3. 运行 OpenClaw

## 更新记录

- 2026-04-07：重新组织目录结构