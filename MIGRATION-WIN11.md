# OpenClaw 迁移到 Windows 11

目标：
- 仓库保存可迁移结构
- 机器本地保存敏感凭据
- 新机器拉代码后，只需补环境变量和少量本机路径即可恢复

## 当前约定

进仓库：
- `workspace/` 主工作区内容
- `workspace-browser/` 中的可读配置文件（不含 `.openclaw/` 运行时目录）
- `openclaw.example.json` 脱敏配置模板
- `.env.example` 环境变量模板
- 说明文档（本文档）

不进仓库：
- 真实 `openclaw.json`
- `.env`
- `browser/` 浏览器用户数据
- `agents/` 会话缓存
- `workspace*/.openclaw/` 运行时状态
- 各类 token / 私钥 / 本机缓存

## 这台旧机器建议保留的本机秘密

至少这些不要进 git：
- `OPENCLAW_GATEWAY_TOKEN`
- `DISCORD_BOT_TOKEN`
- `DISCORD_BOT_TOKEN_QINGLAN`
- `~/.ssh/` 私钥

## 新机器恢复步骤

### 1. 安装基础环境
- 安装 Git
- 安装 Node.js
- 安装 OpenClaw
- 安装需要的浏览器（Chrome / Brave / Edge 之一）

### 2. 拉取仓库
```powershell
git clone git@github.com:lijunyang369/xiaoqing.git C:\Users\wei\.openclaw
cd C:\Users\wei\.openclaw
```

### 3. 建立本机配置
- 复制 `openclaw.example.json` 为 `openclaw.json`
- 按新机器实际情况检查并修改这些路径：
  - `agents.defaults.workspace`
  - `agents.list[*].workspace`
  - `agents.list[*].agentDir`
- 更新 `gateway.controlUi.allowedOrigins`
  - 如果 ngrok 域名变了，这里要改

### 4. 配置环境变量
可用系统环境变量，或本机 `.env` / 启动脚本方式注入。

至少要有：
```env
OPENCLAW_GATEWAY_TOKEN=...
DISCORD_BOT_TOKEN=...
DISCORD_BOT_TOKEN_QINGLAN=...
```

### 5. 启动前自检
```powershell
openclaw gateway status
openclaw browser profiles
```

### 6. 启动 Gateway
```powershell
openclaw gateway start
```

### 7. 验证
- Control UI 是否能连上
- Discord bot 是否上线
- `browser-ops` 新会话是否拿到 browser 能力

## 推荐迁移策略

### 配置分层
- `openclaw.example.json`：仓库里的公开模板
- `openclaw.json`：当前机器专用配置
- `.env.example`：仓库里的变量清单
- `.env` 或系统环境变量：当前机器真实秘密

### 日常维护规则
- 新增 token：优先放环境变量，不写入 json 明文
- 新增本机路径：优先写到模板和迁移文档
- 新增运行时缓存目录：及时补到 `.gitignore`

## 当前已知注意点
- `browser/` 是 OpenClaw 浏览器用户数据目录，不能进仓库。
- `workspace-browser/.openclaw/` 是运行时目录，不能进仓库。
- `openclaw.json` 当前机器上仍含真实 gateway token，推送前必须避免上传真实文件。
