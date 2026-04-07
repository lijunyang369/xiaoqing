# OpenClaw 环境变量清单

## 概述
此文档列出了 OpenClaw 多设备同步所需的环境变量。分为两类：
1. **设备特定变量**：每台设备必须单独配置
2. **共享变量**：可在设备间共享（通过 Git）

## 设备特定环境变量

### 设备标识
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `OPENCLAW_DEVICE_ID` | 设备唯一标识符 | `home-pc`, `work-pc` | 是 |
| `OPENCLAW_DEVICE_NAME` | 设备友好名称 | `"家庭电脑"`, `"公司电脑"` | 是 |
| `OPENCLAW_DEVICE_TYPE` | 设备类型 | `desktop`, `laptop`, `server` | 否 |

### 浏览器配置
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `OPENCLAW_BROWSER_CDP_URL` | Chrome DevTools Protocol URL | `http://172.31.208.1:9223` | 是 |
| `OPENCLAW_BROWSER_DEFAULT_PROFILE` | 默认浏览器配置 | `chrome-relay`, `openclaw` | 是 |
| `OPENCLAW_BROWSER_HEADLESS` | 是否无头模式 | `true`, `false` | 否 |
| `OPENCLAW_BROWSER_PORT` | 浏览器 CDP 端口 | `18800`, `9222` | 否 |

### API 密钥和令牌
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxx` | 是 |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-xxx` | 否 |
| `DISCORD_BOT_TOKEN` | Discord 机器人令牌 | `xxx` | 否 |
| `DISCORD_BOT_TOKEN_QINGLAN` | 青览 Discord 令牌 | `xxx` | 否 |
| `GOOGLE_API_KEY` | Google API 密钥 | `xxx` | 否 |

### 网关配置
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `OPENCLAW_GATEWAY_PORT` | 网关端口 | `18789` | 是 |
| `OPENCLAW_GATEWAY_TOKEN` | 网关认证令牌 | `xxx` | 是 |
| `OPENCLAW_GATEWAY_HOST` | 网关绑定主机 | `127.0.0.1`, `0.0.0.0` | 否 |

### 网络配置
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `HTTP_PROXY` | HTTP 代理 | `http://proxy.example.com:8080` | 否 |
| `HTTPS_PROXY` | HTTPS 代理 | `http://proxy.example.com:8080` | 否 |
| `NO_PROXY` | 不代理的主机 | `localhost,127.0.0.1` | 否 |

### 存储配置
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `OPENCLAW_HOME` | OpenClaw 主目录 | `~/.openclaw` | 否 |
| `OPENCLAW_WORKSPACE` | 工作区目录 | `~/.openclaw/workspace` | 否 |
| `OPENCLAW_CONFIG_PATH` | 配置文件路径 | `~/.openclaw/openclaw.json` | 否 |

## 共享环境变量（通过 Git）

### 应用配置
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `OPENCLAW_LOG_LEVEL` | 日志级别 | `info`, `debug`, `warn` | 否 |
| `OPENCLAW_MAX_CONCURRENT_AGENTS` | 最大并发 Agent 数 | `4` | 否 |
| `OPENCLAW_SUBAGENTS_MAX_CONCURRENT` | 最大并发子 Agent 数 | `8` | 否 |
| `OPENCLAW_ACP_MAX_CONCURRENT_SESSIONS` | ACP 最大会话数 | `8` | 否 |

### 功能开关
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `OPENCLAW_BROWSER_ENABLED` | 浏览器功能开关 | `true`, `false` | 否 |
| `OPENCLAW_ACP_ENABLED` | ACP 功能开关 | `true`, `false` | 否 |
| `OPENCLAW_GATEWAY_ENABLED` | 网关功能开关 | `true`, `false` | 否 |
| `OPENCLAW_CRON_ENABLED` | 定时任务开关 | `true`, `false` | 否 |

## 环境变量模板 (.env.example)

```bash
# ============================================
# OpenClaw 环境变量模板
# ============================================
# 复制此文件为 .env 并填写实际值
# ============================================

# 设备标识
OPENCLAW_DEVICE_ID=DEVICE_ID_HERE
OPENCLAW_DEVICE_NAME="设备名称"
OPENCLAW_DEVICE_TYPE=desktop

# 浏览器配置
OPENCLAW_BROWSER_CDP_URL=http://localhost:9222
OPENCLAW_BROWSER_DEFAULT_PROFILE=openclaw
OPENCLAW_BROWSER_HEADLESS=true
OPENCLAW_BROWSER_PORT=18800

# API 密钥和令牌
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_BOT_TOKEN_QINGLAN=your_qinglan_discord_token_here
GOOGLE_API_KEY=your_google_api_key_here

# 网关配置
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_GATEWAY_TOKEN=your_gateway_token_here
OPENCLAW_GATEWAY_HOST=127.0.0.1

# 网络配置
# HTTP_PROXY=http://proxy.example.com:8080
# HTTPS_PROXY=http://proxy.example.com:8080
# NO_PROXY=localhost,127.0.0.1

# 存储配置
OPENCLAW_HOME=~/.openclaw
OPENCLAW_WORKSPACE=~/.openclaw/workspace
OPENCLAW_CONFIG_PATH=~/.openclaw/openclaw.json

# 应用配置
OPENCLAW_LOG_LEVEL=info
OPENCLAW_MAX_CONCURRENT_AGENTS=4
OPENCLAW_SUBAGENTS_MAX_CONCURRENT=8
OPENCLAW_ACP_MAX_CONCURRENT_SESSIONS=8

# 功能开关
OPENCLAW_BROWSER_ENABLED=true
OPENCLAW_ACP_ENABLED=true
OPENCLAW_GATEWAY_ENABLED=true
OPENCLAW_CRON_ENABLED=true
```

## 环境变量加载顺序

OpenClaw 按以下顺序加载配置（后加载的覆盖先加载的）：

1. **内置默认值** - OpenClaw 内置的默认配置
2. **共享配置文件** - `shared/openclaw.base.json`（通过 Git 同步）
3. **设备配置文件** - `local/openclaw.local.json`（设备特定）
4. **环境变量** - 从 `.env` 文件或系统环境变量加载
5. **命令行参数** - 启动时的命令行参数

## 设备初始化脚本

创建 `init-device.sh` 脚本用于新设备初始化：

```bash
#!/bin/bash
# OpenClaw 设备初始化脚本

set -e

echo "=== OpenClaw 设备初始化 ==="

# 1. 检查 .env 文件
if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cp .env.example .env
    echo "请编辑 .env 文件并填写设备特定配置"
    exit 1
fi

# 2. 加载环境变量
source .env

# 3. 创建目录结构
echo "创建目录结构..."
mkdir -p ~/.openclaw
mkdir -p ~/.openclaw/workspace
mkdir -p ~/.openclaw/logs
mkdir -p ~/.openclaw/browser

# 4. 复制配置文件
echo "复制配置文件..."
if [ ! -f ~/.openclaw/openclaw.json ]; then
    cp local/openclaw.json.example ~/.openclaw/openclaw.json
    echo "请编辑 ~/.openclaw/openclaw.json 文件"
fi

# 5. 同步共享文件
echo "同步共享文件..."
./sync-openclaw.sh

echo "=== 初始化完成 ==="
echo "下一步："
echo "1. 编辑 ~/.openclaw/openclaw.json 文件"
echo "2. 运行 ./sync-openclaw.sh 同步最新数据"
echo "3. 启动 OpenClaw: openclaw gateway start"
```

## 验证脚本

创建 `check-env.sh` 脚本验证环境变量：

```bash
#!/bin/bash
# 环境变量验证脚本

set -e

echo "=== 环境变量验证 ==="

# 必需变量检查
required_vars=(
    "OPENCLAW_DEVICE_ID"
    "OPENCLAW_DEVICE_NAME"
    "DEEPSEEK_API_KEY"
    "OPENCLAW_GATEWAY_TOKEN"
)

missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -eq 0 ]; then
    echo "✓ 所有必需环境变量已设置"
else
    echo "✗ 以下必需环境变量未设置："
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

# 可选变量检查
optional_vars=(
    "OPENCLAW_BROWSER_CDP_URL"
    "OPENAI_API_KEY"
    "DISCORD_BOT_TOKEN"
)

echo "可选环境变量状态："
for var in "${optional_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "  - $var: 未设置"
    else
        echo "  - $var: 已设置"
    fi
done

echo "=== 验证完成 ==="
```

## 最佳实践

### 1. 安全存储
- 将 `.env` 文件添加到 `.gitignore`
- 使用环境变量而不是硬编码的密钥
- 定期轮换 API 密钥

### 2. 版本控制
- 将 `.env.example` 提交到 Git
- 使用不同的 `.env` 文件用于不同环境
- 记录环境变量变更历史

### 3. 文档维护
- 更新此清单当添加新环境变量时
- 为每个变量添加清晰的描述
- 提供示例值和默认值

### 4. 故障排除
- 使用 `check-env.sh` 验证环境变量
- 检查变量名拼写是否正确
- 确保变量值没有多余的空格

## 变更日志

| 日期 | 版本 | 变更描述 |
|------|------|----------|
| 2026-04-07 | 1.0 | 初始版本，包含核心环境变量 |
| 2026-04-07 | 1.1 | 添加设备标识和浏览器配置变量 |

---
*文档维护：env-engineer（环境工程师）*