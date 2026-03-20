# OpenClaw 迁移到 Windows 11

目标：
- 仓库保存可迁移结构
- 机器本地保存敏感凭据
- 新机器拉代码后，只需补环境变量和少量本机路径即可恢复
- 文档可直接照做，尽量不靠回忆

## 一句话方案

采用 **"仓库保存骨架，env 保存秘密"** 的迁移方式：
- git 仓库里：放模板、角色、工作区、文档
- 新旧机器本地：放 token、私钥、运行时缓存、浏览器用户数据

---

## 当前约定

### 进仓库
- `workspace/` 主工作区内容
- `workspace-browser/` 中的可读配置文件（不含 `.openclaw/` 运行时目录）
- `openclaw.example.json` 脱敏配置模板
- `.env.example` 环境变量模板
- 说明文档（本文档）

### 不进仓库
- 真实 `openclaw.json`
- 真实 `.env`
- `browser/` 浏览器用户数据
- `agents/` 会话缓存
- `workspace*/.openclaw/` 运行时状态
- 各类 token / 私钥 / 本机缓存

---

## 这台旧机器建议保留的本机秘密

至少这些不要进 git：
- `OPENCLAW_GATEWAY_TOKEN`
- `DISCORD_BOT_TOKEN`
- `DISCORD_BOT_TOKEN_QINGLAN`
- `~/.ssh/` 私钥

如果后面还有别的 provider key，也同样放 env：
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `BRAVE_API_KEY`
- 其他第三方服务 token

---

## 升级前检查清单（旧机器）

升级 Windows 11 之前，先确认这些都已经完成：

- [ ] 代码已推到 GitHub
- [ ] `openclaw.example.json` 已存在
- [ ] `.env.example` 已存在
- [ ] 真实 `openclaw.json` 没有再提交进仓库
- [ ] SSH 公钥已加到 GitHub
- [ ] 需要保留的 token 已记录到密码管理器 / 安全文档 / 私密备份
- [ ] 你知道新机器上要重新设置哪些环境变量

### 建议你另外保存一份的内容
手工放到你自己的安全位置：
- GitHub SSH 私钥位置：`C:\Users\wei\.ssh\`
- 当前使用的 gateway token
- Discord bot token（主 bot）
- Discord bot token（青览）
- 未来若有其他 API key，也一起放入密码管理器

---

## 新机器恢复步骤（操作版）

下面这部分就是你升级完系统后可以直接照做的步骤。

### 1. 安装基础环境
先安装：
- Git
- Node.js
- OpenClaw
- Chrome / Brave / Edge 之一

如果 SSH 还没恢复，也要把你的 `~/.ssh/` 放回去，或者重新生成并重新加到 GitHub。

---

### 2. 拉取仓库
```powershell
git clone git@github.com:lijunyang369/xiaoqing.git C:\Users\wei\.openclaw
cd C:\Users\wei\.openclaw
```

如果这里拉不下来，先检查：
```powershell
ssh -T git@github.com
```

期望看到类似：
```text
Hi lijunyang369! You've successfully authenticated...
```

---

### 3. 建立本机配置文件
复制模板为真实配置：

```powershell
Copy-Item .\openclaw.example.json .\openclaw.json
```

然后检查/修改这些路径是否仍然适配新机器：
- `agents.defaults.workspace`
- `agents.list[*].workspace`
- `agents.list[*].agentDir`

如果用户名、目录结构变了，这一步必须改。

---

### 4. 配置环境变量
至少要恢复这些：

```env
OPENCLAW_GATEWAY_TOKEN=...
DISCORD_BOT_TOKEN=...
DISCORD_BOT_TOKEN_QINGLAN=...
```

#### 方式 A：用系统环境变量（推荐长期）
PowerShell 里可以用：

```powershell
setx OPENCLAW_GATEWAY_TOKEN "你的真实token"
setx DISCORD_BOT_TOKEN "你的真实token"
setx DISCORD_BOT_TOKEN_QINGLAN "你的真实token"
```

**重要：`setx` 只对新开的进程生效。**
也就是说：
- 当前这个 PowerShell 窗口通常拿不到新值
- 已经运行中的 OpenClaw / Gateway 也拿不到新值
- 你需要 **重新打开终端**，并重新启动 OpenClaw / Gateway

#### 方式 B：用本机 `.env`（如果你后面决定这么管）
仓库里只有 `.env.example`，真实 `.env` 不提交。

你可以复制：

```powershell
Copy-Item .\.env.example .\.env
```

然后自己填真实值。

> 注意：是否自动加载 `.env` 取决于你的启动方式。最稳妥的仍然是系统环境变量或明确的启动脚本注入。

---

### 5. 更新 Control UI 域名 / allowedOrigins
如果你继续用 ngrok 或换了域名，记得更新：
- `gateway.controlUi.allowedOrigins`

例如原来是旧 ngrok 域名，新机器启动后若域名变化，这里要改成新的域名。

---

### 6. 启动前自检
在**新开的终端**里检查：

```powershell
openclaw gateway status
openclaw browser profiles
```

如果 `gateway status` 报认证相关错误，优先检查：
- `OPENCLAW_GATEWAY_TOKEN` 是否真的在当前进程可见
- 是否还是旧终端
- `openclaw.json` 是否已改成 SecretRef / env 引用

---

### 7. 启动 Gateway
```powershell
openclaw gateway start
```

如果已在运行，可用：
```powershell
openclaw gateway restart
```

---

### 8. 启动后验证
至少验证这几项：
- Control UI 是否能连上
- Discord bot 是否上线
- `browser-ops` 新会话是否拿到 browser 能力
- 常用 workspace 是否正常加载

---

## 当前已知坑（非常重要）

### 1. `setx` 不是即时生效
这次已经踩到一次了。

现象：
- 你刚 `setx OPENCLAW_GATEWAY_TOKEN ...`
- 但系统提示：
  - `Environment variable "OPENCLAW_GATEWAY_TOKEN" is missing or empty`

原因：
- `setx` 只更新注册表 / 后续新进程环境
- **当前运行中的 Gateway 仍然看不到这个变量**

正确做法：
1. `setx ...`
2. 关闭当前终端 / 重新开新终端
3. 重新启动 gateway

### 2. `browser/` 绝不能进仓库
这是浏览器用户数据目录，包含缓存、cookie、登录态、历史等敏感状态。

### 3. `workspace-browser/.openclaw/` 不能进仓库
这是运行时目录，只适合本机。

### 4. 真实 `openclaw.json` 不能进仓库
仓库里应该只保留：
- `openclaw.example.json`

---

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
- 每次完成较大配置调整后，都更新这份迁移文档

---

## 升级后最短恢复流程（超简版）

系统升级后，如果你只想最快恢复，按这个顺序：

1. 装 Git / Node / OpenClaw / 浏览器
2. `git clone` 仓库
3. `Copy-Item openclaw.example.json openclaw.json`
4. 配好环境变量：
   - `OPENCLAW_GATEWAY_TOKEN`
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_BOT_TOKEN_QINGLAN`
5. 重新打开终端
6. `openclaw gateway start`
7. 验证 Control UI、Discord、browser-ops

---

## 后续建议

迁移稳定后，建议再做两件事：
- 增加一份 **新机初始化脚本**（一键复制模板 + 检查 env）
- 单独整理一份 **browser-ops 打通文档**，避免以后重复排障
