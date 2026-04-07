# OpenClaw 多设备同步迁移步骤

## 概述
本文档提供了从当前 OpenClaw 目录结构迁移到多设备同步结构的详细步骤。迁移分为四个阶段，预计需要 3-5 天完成。

## 迁移前准备

### 1. 备份当前数据
```bash
# 创建完整备份
BACKUP_DIR="$HOME/.openclaw.backup.$(date +%Y%m%d_%H%M%S)"
cp -r ~/.openclaw "$BACKUP_DIR"
echo "备份已创建: $BACKUP_DIR"

# 验证备份
ls -la "$BACKUP_DIR" | head -10
```

### 2. 检查当前状态
```bash
# 检查 OpenClaw 是否运行
openclaw gateway status

# 停止 OpenClaw 服务
openclaw gateway stop

# 检查磁盘空间
df -h ~/
```

### 3. 安装必要工具
```bash
# 确保 Git 已安装
git --version

# 确保 rsync 已安装
rsync --version

# 确保 jq 已安装（用于 JSON 处理）
jq --version
```

## 阶段 1：创建 Git 仓库结构（第 1 天）

### 步骤 1.1：创建仓库目录
```bash
# 创建同步仓库目录
mkdir -p ~/openclaw-sync
cd ~/openclaw-sync

# 初始化 Git 仓库
git init
```

### 步骤 1.2：创建目录结构
```bash
# 创建共享目录结构
mkdir -p shared/workspace
mkdir -p shared/tasks
mkdir -p shared/cron
mkdir -p shared/flows
mkdir -p shared/agents
mkdir -p shared/memory

# 创建设备特定模板目录
mkdir -p local
mkdir -p local/templates
mkdir -p local/scripts
```

### 步骤 1.3：复制 .gitignore 文件
```bash
# 从设计文档复制 .gitignore
cp ~/.openclaw/workspace/gitignore-template.txt .gitignore

# 验证 .gitignore
head -20 .gitignore
```

### 步骤 1.4：创建 README 文件
```bash
cat > README.md << 'EOF'
# OpenClaw 多设备同步仓库

## 概述
此仓库用于在多个设备间同步 OpenClaw 配置、记忆和工作区。

## 目录结构
```
openclaw-sync/
├── shared/           # 共享文件（通过 Git 同步）
│   ├── workspace/   # 工作区文件
│   ├── tasks/       # 任务数据
│   ├── cron/        # 定时任务
│   ├── flows/       # 工作流
│   └── agents/      # Agent 配置
├── local/           # 设备特定模板
│   ├── .env.example
│   └── openclaw.json.example
├── scripts/         # 同步脚本
├── .gitignore       # Git 忽略规则
└── README.md        # 本文件
```

## 使用说明

### 初始化新设备
```bash
./scripts/init-device.sh
```

### 同步数据
```bash
./scripts/sync-openclaw.sh
```

### 检查状态
```bash
./scripts/check-status.sh
```

## 维护指南
- 定期运行同步脚本
- 及时解决合并冲突
- 备份重要更改
EOF
```

## 阶段 2：迁移共享数据（第 2 天）

### 步骤 2.1：迁移工作区文件
```bash
# 迁移核心身份文件
cp ~/.openclaw/workspace/AGENTS.md shared/workspace/
cp ~/.openclaw/workspace/SOUL.md shared/workspace/
cp ~/.openclaw/workspace/IDENTITY.md shared/workspace/
cp ~/.openclaw/workspace/USER.md shared/workspace/
cp ~/.openclaw/workspace/MEMORY.md shared/workspace/
cp ~/.openclaw/workspace/TOOLS.md shared/workspace/

# 迁移记忆文件
if [ -d ~/.openclaw/workspace/memory ]; then
    cp -r ~/.openclaw/workspace/memory shared/workspace/
fi

# 迁移技能文件（选择性）
if [ -d ~/.openclaw/workspace/skills ]; then
    mkdir -p shared/workspace/skills
    # 只迁移核心技能
    cp -r ~/.openclaw/workspace/skills/core shared/workspace/skills/ 2>/dev/null || true
    cp -r ~/.openclaw/workspace/skills/essential shared/workspace/skills/ 2>/dev/null || true
fi

# 迁移脚本文件
if [ -d ~/.openclaw/workspace/scripts ]; then
    cp -r ~/.openclaw/workspace/scripts shared/workspace/
fi
```

### 步骤 2.2：迁移其他共享数据
```bash
# 迁移任务数据
if [ -d ~/.openclaw/tasks ]; then
    cp -r ~/.openclaw/tasks shared/
fi

# 迁移定时任务
if [ -d ~/.openclaw/cron ]; then
    cp -r ~/.openclaw/cron shared/
fi

# 迁移工作流
if [ -d ~/.openclaw/flows ]; then
    cp -r ~/.openclaw/flows shared/
fi

# 迁移 Agent 配置
if [ -d ~/.openclaw/agents ]; then
    cp -r ~/.openclaw/agents shared/
fi
```

### 步骤 2.3：创建设备特定模板
```bash
# 创建 .env 模板
if [ -f ~/.openclaw/.env ]; then
    # 创建带占位符的模板
    sed 's/=.*/=PLACEHOLDER/' ~/.openclaw/.env > local/.env.example
else
    cat > local/.env.example << 'EOF'
# OpenClaw 环境变量模板
OPENCLAW_DEVICE_ID=DEVICE_ID_HERE
OPENCLAW_DEVICE_NAME="设备名称"
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENCLAW_GATEWAY_TOKEN=your_gateway_token_here
EOF
fi

# 创建配置文件模板
if [ -f ~/.openclaw/openclaw.json ]; then
    # 创建带注释的模板
    jq 'walk(if type == "string" and test("^(sk-|eyJ|MT|http://172\\.)") then "PLACEHOLDER" else . end)' ~/.openclaw/openclaw.json > local/openclaw.json.example
else
    cp ~/.openclaw/workspace/openclaw.example.json local/openclaw.json.example
fi
```

## 阶段 3：创建同步脚本（第 3 天）

### 步骤 3.1：创建同步脚本
```bash
mkdir -p scripts

cat > scripts/sync-openclaw.sh << 'EOF'
#!/bin/bash
# OpenClaw 同步脚本
# 用法: ./sync-openclaw.sh [pull|push|both]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OPENCLAW_HOME="$HOME/.openclaw"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查目录
check_directories() {
    if [ ! -d "$OPENCLAW_HOME" ]; then
        log_error "OpenClaw 目录不存在: $OPENCLAW_HOME"
        exit 1
    fi
    
    if [ ! -d "$REPO_DIR" ]; then
        log_error "仓库目录不存在: $REPO_DIR"
        exit 1
    fi
}

# 拉取远程更改
pull_changes() {
    log_info "拉取远程更改..."
    cd "$REPO_DIR"
    
    # 检查是否有远程仓库
    if git remote -v | grep -q origin; then
        git pull origin main --rebase
    else
        log_warn "未配置远程仓库，跳过拉取"
    fi
    
    # 同步共享文件到本地
    log_info "同步共享文件到本地..."
    
    # 工作区文件
    if [ -d "$REPO_DIR/shared/workspace" ]; then
        rsync -av --delete --exclude='.openclaw/' "$REPO_DIR/shared/workspace/" "$OPENCLAW_HOME/workspace/"
    fi
    
    # 其他共享目录
    for dir in tasks cron flows agents; do
        if [ -d "$REPO_DIR/shared/$dir" ]; then
            rsync -av --delete "$REPO_DIR/shared/$dir/" "$OPENCLAW_HOME/$dir/"
        fi
    done
    
    log_info "拉取完成"
}

# 推送本地更改
push_changes() {
    log_info "推送本地更改..."
    cd "$REPO_DIR"
    
    # 检查是否有更改
    if git status --porcelain | grep -q .; then
        # 添加更改
        git add .
        
        # 提交
        commit_msg="Sync: $(date +'%Y-%m-%d %H:%M:%S') from $(hostname)"
        git commit -m "$commit_msg"
        
        # 推送到远程
        if git remote -v | grep -q origin; then
            git push origin main
        else
            log_warn "未配置远程仓库，跳过推送"
        fi
    else
        log_info "没有更改需要提交"
    fi
    
    log_info "推送完成"
}

# 完整同步
sync_both() {
    log_info "开始完整同步..."
    pull_changes
    push_changes
    log_info "完整同步完成"
}

# 主函数
main() {
    check_directories
    
    local mode="${1:-both}"
    
    case "$mode" in
        pull)
            pull_changes
            ;;
        push)
            push_changes
            ;;
        both)
            sync_both
            ;;
        *)
            log_error "未知模式: $mode"
            echo "用法: $0 [pull|push|both]"
            exit 1
            ;;
    esac
}

main "$@"
EOF

chmod +x scripts/sync-openclaw.sh
```

### 步骤 3.2：创建设备初始化脚本
```bash
cat > scripts/init-device.sh << 'EOF'
#!/bin/bash
# OpenClaw 设备初始化脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OPENCLAW_HOME="$HOME/.openclaw"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== OpenClaw 设备初始化 ===${NC}"

# 步骤 1: 检查 Git 仓库
if [ ! -d "$REPO_DIR/.git" ]; then
    echo -e "${RED}错误: 不是 Git 仓库目录${NC}"
    exit 1
fi

# 步骤 2: 检查 .env 文件
if [ ! -f "$REPO_DIR/local/.env.example" ]; then
    echo -e "${YELLOW}警告: 未找到 .env.example 模板${NC}"
    echo "创建默认 .env 模板..."
    cat > "$REPO_DIR/local/.env.example" << 'ENVEOF'
# OpenClaw 环境变量模板
OPENCLAW_DEVICE_ID=DEVICE_ID_HERE
OPENCLAW_DEVICE_NAME="设备名称"
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENCLAW_GATEWAY_TOKEN=your_gateway_token_here
ENVEOF
fi

if [ ! -f "$OPENCLAW_HOME/.env" ]; then
    echo "创建 .env 文件..."
    cp "$REPO_DIR/local/.env.example" "$OPENCLAW_HOME/.env"
    echo -e "${YELLOW}请编辑 $OPENCLAW_HOME/.env 文件并填写设备特定配置${NC}"
    echo "按 Enter 继续..."
    read
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi

# 步骤 3: 创建目录结构
echo "创建目录结构..."
mkdir -p "$OPENCLAW_HOME"
mkdir -p "$OPENCLAW_HOME/workspace"
mkdir -p "$OPENCLAW_HOME/logs"
mkdir -p "$OPENCLAW_HOME/browser"
mkdir -p "$OPENCLAW_HOME/tasks"
mkdir -p "$OPENCLAW_HOME/cron"
mkdir -p "$OPENCLAW_HOME/flows"
mkdir -p "$OPENCLAW_HOME/agents"

# 步骤 4: 复制配置文件
if [ ! -f "$OPENCLAW_HOME/openclaw.json" ]; then
    if [ -f "$REPO_DIR/local/openclaw.json.example" ]; then
        echo "复制 openclaw.json 配置文件..."
        cp "$REPO_DIR/local/openclaw.json.example" "$OPENCLAW_HOME/openclaw.json"
        echo -e "${YELLOW}请编辑 $OPENCLAW_HOME/openclaw.json 文件${NC}"
    else
        echo -e "${YELLOW}警告: 未找到 openclaw.json 模板${NC}"
    fi
else
    echo -e "${GREEN}✓ openclaw.json 文件已存在${NC}"
fi

# 步骤 5: 同步共享文件
echo "同步共享文件..."
"$SCRIPT_DIR/sync-openclaw.sh" pull

# 步骤 6: 设置权限
echo "设置文件权限..."
chmod 700 "$OPENCLAW_HOME"
chmod 600 "$OPENCLAW_HOME/.env" 2>/dev/null || true

echo -e "${GREEN}=== 初始化完成 ===${NC}"
echo ""
echo -e "${YELLOW}下一步操作:${NC}"
echo "1. 编辑 $OPENCLAW_HOME/.env 文件"
echo "2. 编辑 $OPENCLAW_HOME/openclaw.json 文件"
echo "3. 运行同步脚本: $SCRIPT_DIR/sync-openclaw.sh"
echo "4. 启动 OpenClaw: openclaw gateway start"
EOF

chmod +x scripts/init-device.sh
```

### 步骤 3.3：创建状态检查脚本
```bash
cat > scripts/check-status.sh << 'EOF'
#!/bin/bash
# OpenClaw 同步状态检查脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OPENCLAW_HOME="$HOME/.openclaw"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== OpenClaw 同步状态检查 ===${NC}"
echo "检查时间: $(date)"
echo "设备: $(hostname)"
echo ""

# 检查目录存在性
echo -e "${BLUE}[1] 目录检查${NC}"
check_dir() {
    if [ -d "$1" ]; then
        echo -e "  ${GREEN}✓ $2${NC}"
        return 0
    else
        echo -e "  ${RED}✗ $2 (不存在)${NC}"
        return 1
    fi
}

check_dir "$OPENCLAW_HOME" "OpenClaw 主目录"
check_dir "$REPO_DIR" "同步仓库目录"
check_dir "$OPENCLAW_HOME/workspace" "工作区目录"
check_dir "$REPO_DIR/shared/workspace" "共享工作区目录"

echo ""

# 检查配置文件
echo -e "${BLUE}[2] 配置文件检查${NC}"
check_file() {
    if [ -f "$1" ]; then
        local size=$(stat -c%s "$1" 2>/dev/null || stat -f%z "$1" 2>/dev/null)
        echo -e "  ${GREEN}✓ $2 (${size} bytes)${NC}"
        return 0
    else
        echo -e "  ${RED}✗ $2 (不存在)${NC}"
        return 1
    fi
}

check_file "$OPENCLAW_HOME/.env" ".env 文件"
check_file "$OPENCLAW_HOME/openclaw.json" "openclaw.json 文件"
check_file "$REPO_DIR/local/.env.example" ".env.example 模板"
check_file "$REPO_DIR/local/openclaw.json.example" "openclaw.json.example 模板"

echo ""

# 检查 Git 状态
echo -e "${BLUE}[3] Git 状态检查${NC}"
cd "$REPO_DIR"
if git status --porcelain | grep -q .; then
    echo -e "  ${YELLOW}⚠ 有未提交的更改${NC}"
    git status --short
else
    echo -e "  ${GREEN}✓ 没有未提交的更改${NC}"
fi

# 检查远程仓库
if git remote -v | grep -q origin; then
    echo -e "  ${GREEN}✓ 已配置远程仓库${NC}"
    git remote -v
else
    echo -e "  ${YELLOW}⚠ 未配置远程仓库${NC}"
fi

echo ""

# 检查同步状态
echo -e "${BLUE}[4] 同步状态检查${NC}"

# 检查工作区文件差异
workspace_diff=$(rsync -avn --delete "$REPO_DIR/shared/workspace/" "$OPENCLAW_HOME/workspace/" 2>/dev/null | grep -E '^(>|c|d)' | wc -l)
if [ "$workspace_diff" -eq 0 ]; then
    echo -e "  ${GREEN}✓ 工作区文件已同步${NC}"
else
    echo -e "  ${YELLOW}⚠ 工作区有 $workspace_diff 个文件差异${NC}"
fi

# 检查环境变量
echo -e "${BLUE}[5] 环境变量检查${NC}"
if [ -f "$OPENCLAW_HOME/.env" ]; then
    source "$OPENCLAW_HOME/.env" 2>/dev/null
    
    required_vars=("OPENCLAW_DEVICE_ID" "OPENCLAW_DEVICE_NAME" "DEEPSEEK_API_KEY" "OPENCLAW_GATEWAY_TOKEN")
    missing=0
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "  ${RED}✗ $var 未设置${NC}"
            missing=$((missing + 1))
        elif [[ "${!var}" == *"PLACEHOLDER"* || "${!var}" == *"your_"* ]]; then
            echo -e "  ${YELLOW}⚠ $var 使用占位符${NC}"
        else
            echo -e "  ${GREEN}✓ $var 已设置${NC}"
        fi
    done
    
    if [ $missing -gt 0 ]; then
        echo -e "  ${RED}错误: $missing 个必需变量未设置${NC}"
    fi
else
    echo -e "  ${RED}✗ .env 文件不存在${NC}"
fi

echo ""
echo -e "${BLUE}=== 检查完成 ===${NC}"
EOF

chmod +x scripts/check-status.sh