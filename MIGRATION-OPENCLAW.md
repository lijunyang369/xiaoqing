# OpenClaw 跨机器恢复手册

目标：
- 让 OpenClaw 在 **Windows / macOS / 未来新机器** 上都能快速恢复
- 不把这次机器的偶然细节写死在文档里
- 把系统调教沉淀成 **可复用、可迁移、可持续维护** 的结构

## 核心原则

采用 **"仓库保存骨架，环境变量保存秘密，本机保存状态"** 的结构：

### 仓库里保存
- 工作区内容（`workspace/`）
- agent 角色/人格/长期记忆
- 脱敏配置模板（如 `openclaw.example.json`）
- 环境变量模板（如 `.env.example`）
- 恢复文档 / 操作手册

### 环境变量保存
- Gateway token
- Discord bot token
- 其他 API key / 第三方凭据

### 本机状态单独保存
- 浏览器用户数据
- agent 会话缓存
- `.openclaw/` 运行时目录
- SSH 私钥
- 本机专属缓存 / 日志 / 临时状态

> 目标不是“把当前机器完整复制过去”，而是：
> **让任意新机器都能按同一恢复流程跑起来，而不用重新调教。**

---

## 目录分层约定

### 应该进入 git 的内容
- `workspace/`
- `workspace-browser/` 中的可读配置文件（不含 `.openclaw/`）
- `openclaw.example.json`
- `.env.example`
- 各类恢复 / 迁移 / 操作文档

### 不应进入 git 的内容
- 真实 `openclaw.json`
- 真实 `.env`
- `browser/`
- `agents/`
- `workspace*/.openclaw/`
- 日志、缓存、运行时状态
- 私钥、token、secret

---

## 恢复所需最小资产

无论以后迁移到：
- Windows 新机器
- macOS
- 重装系统后的同一台机器

都至少需要这三类东西：

### 1. 仓库
仓库里要有：
- 工作区内容
- 模板配置
- 恢复文档

### 2. 秘密
至少这些需要单独保存：
- `OPENCLAW_GATEWAY_TOKEN`
- `DISCORD_BOT_TOKEN`
- `DISCORD_BOT_TOKEN_QINGLAN`
- 未来新增的其他 provider key
- GitHub SSH 私钥（如果你用 SSH 拉仓库）

### 3. 基础运行环境
新机器上至少要有：
- Git
- Node.js
- OpenClaw
- 一个 Chromium 系浏览器（Chrome / Brave / Edge）

---

## 通用恢复流程

下面这套步骤应当适用于未来多数机器，而不是只适用于这一次升级。

### 第 1 步：安装基础环境
安装：
- Git
- Node.js
- OpenClaw
- Chrome / Brave / Edge 之一

如果使用 Git SSH：
- 恢复 `~/.ssh/` 私钥
- 或重新生成 SSH key 并重新加到 GitHub

验证 SSH：
```powershell
ssh -T git@github.com
```

成功示例：
```text
Hi <your-account>! You've successfully authenticated...
```

---

### 第 2 步：拉取仓库
```powershell
git clone git@github.com:lijunyang369/xiaoqing.git C:\Users\wei\.openclaw
cd C:\Users\wei\.openclaw
```

在 macOS / Linux 上，路径按本机改，例如：
```bash
git clone git@github.com:lijunyang369/xiaoqing.git ~/.openclaw
cd ~/.openclaw
```

---

### 第 3 步：从模板生成真实配置
复制模板：

#### Windows PowerShell
```powershell
Copy-Item .\openclaw.example.json .\openclaw.json
```

#### macOS / Linux
```bash
cp ./openclaw.example.json ./openclaw.json
```

然后检查这些字段是否适配当前机器：
- `agents.defaults.workspace`
- `agents.list[*].workspace`
- `agents.list[*].agentDir`
- `gateway.controlUi.allowedOrigins`

### 关于路径
这是最容易因为换机器 / 换系统而失效的部分。

建议长期做法：
- 配置里尽量减少写死用户名路径
- 每次新增 agent/workspace 时，同步更新模板
- 文档明确说明哪些字段是“机器相关字段”

---

### 第 4 步：恢复环境变量
至少恢复：

```env
OPENCLAW_GATEWAY_TOKEN=...
DISCORD_BOT_TOKEN=...
DISCORD_BOT_TOKEN_QINGLAN=...
```

如果以后还有：
```env
OPENAI_API_KEY=...
GEMINI_API_KEY=...
BRAVE_API_KEY=...
```
也同样走 env。

#### Windows（长期推荐）
```powershell
setx OPENCLAW_GATEWAY_TOKEN "你的真实token"
setx DISCORD_BOT_TOKEN "你的真实token"
setx DISCORD_BOT_TOKEN_QINGLAN "你的真实token"
```

#### macOS / Linux（示意）
写进 shell 配置，例如 `~/.zshrc` / `~/.bashrc`：
```bash
export OPENCLAW_GATEWAY_TOKEN="你的真实token"
export DISCORD_BOT_TOKEN="你的真实token"
export DISCORD_BOT_TOKEN_QINGLAN="你的真实token"
```
然后：
```bash
source ~/.zshrc
```
或重新开一个终端。

#### 重要提醒
环境变量写入后，**要重新开终端 / 重启相关进程**。

尤其是 Windows `setx`：
- 不会让当前终端立刻拿到新值
- 不会让已经运行中的 Gateway 立刻拿到新值

---

### 第 5 步：启动前自检
```powershell
openclaw gateway status
openclaw browser profiles
```

如果报 token 缺失，优先检查：
- 环境变量是否真的已生效
- 当前是不是旧终端
- `openclaw.json` 是否指向 env SecretRef

---

### 第 6 步：启动 Gateway
```powershell
openclaw gateway start
```
或：
```powershell
openclaw gateway restart
```

---

### 第 7 步：恢复验证
至少验证：
- Control UI 能连接
- 主 bot 正常上线
- 青览 bot 正常上线
- 常用 workspace 正常加载
- browser profile 能被识别
- 关键 agent 的新会话能力正常注入

---

## 跨平台注意点

### Windows
- 常用 `setx` 写环境变量，但它不是即时生效
- 路径分隔符是 `\`
- 浏览器通常来自 Chrome / Edge / Brave

### macOS
- 常见 shell 是 `zsh`
- 需要在 `~/.zshrc` 或启动器中注入环境变量
- 浏览器路径、应用路径、Node 安装位置可能不同

### 共通点
真正需要迁移的不是“某台机器的原样目录”，而是：
- 配置结构
- 秘密来源
- 恢复步骤
- 关键验证点

---

## 已知易踩坑

### 1. 环境变量已设置，但当前进程仍读不到
原因：
- 变量只对新进程生效

处理：
1. 新开终端
2. 重启 Gateway
3. 再检查状态

### 2. 浏览器用户数据误进仓库
`browser/` 绝不能进 git。

### 3. 运行时目录误进仓库
如：
- `agents/`
- `workspace*/.openclaw/`

都应该忽略。

### 4. 真实配置误进仓库
仓库里应该保存：
- `openclaw.example.json`

而不是：
- 真实 `openclaw.json`

---

## 长期可维护建议

为了未来 Windows / macOS / 新机器都不再“重新调教”，建议长期坚持这几条：

### 1. 新增秘密，一律优先 env
不要继续把真实 token 写进 json。

### 2. 新增机器相关配置，先改模板再改本机
也就是：
- 先更新 `openclaw.example.json`
- 再更新本机的 `openclaw.json`

### 3. 每次新增运行时目录，及时补 `.gitignore`
避免未来把缓存、会话、浏览器状态误提交。

### 4. 每次完成关键调教，都更新这份手册
文档要记录：
- 可复用结构
- 通用恢复流程
- 新踩到的坑

而不是记录一次性的临时操作噪音。

---

## 最短恢复流程（极简版）

以后任意机器上，只要你想最快恢复，按这个顺序：

1. 安装 Git / Node.js / OpenClaw / 浏览器
2. 恢复 SSH（或重新配 GitHub SSH）
3. clone 仓库
4. `openclaw.example.json` 复制为 `openclaw.json`
5. 填好环境变量
6. 新开终端
7. `openclaw gateway start`
8. 验证 Control UI / Discord / browser / agent 能力

---

## 未来可继续补强的两项

### A. 新机初始化脚本
做一个脚本自动完成：
- 检查 Git / Node / OpenClaw
- 复制模板配置
- 提示缺少哪些 env
- 做最小自检

### B. agent 能力恢复清单
单独整理：
- main
- windows-ops
- news-brief
- browser-ops

分别在新机会话中应该验证什么，避免以后重复排障。
