# BOOT.md - Gateway 中断任务恢复机制

**版本**：1.0  
**最后更新**：2026-04-08  
**生效范围**：OpenClaw Gateway 启动流程

## 1. 问题背景

OpenClaw Gateway 作为核心服务，负责管理所有 agent 会话和子任务。当 Gateway 因维护、重启或意外停止时，正在运行的**子代理任务**（subagent runs）可能被中断，导致：

- 长时间运行的任务（如数据同步、模型训练）半途而废
- 用户需要手动重新启动任务
- 任务状态丢失，可能造成数据不一致

## 2. 设计目标

- **自动检测**：Gateway 启动时自动识别因上次停止而中断的任务
- **智能恢复**：根据任务类型和中断点决定恢复策略
- **状态保持**：尽可能保留任务原有进度和上下文
- **用户透明**：恢复过程对用户透明，必要时通知用户

## 3. 技术方案

### 3.1 中断任务检测

**数据源**：
- `~/.openclaw/subagents/runs.json` - 所有子代理运行记录
- `~/.openclaw/agents/*/sessions/` - 会话状态文件
- Gateway 内存状态（重启后丢失）

**检测逻辑**：
```javascript
// 伪代码
function detectInterruptedRuns() {
  // 1. 加载 runs.json
  const runs = loadRunsJson();
  
  // 2. 筛选未完成的任务
  const interrupted = [];
  for (const run of runs) {
    if (run.status === 'running' || run.status === 'pending') {
      // 3. 检查对应的会话是否还存在
      const sessionExists = checkSessionExists(run.sessionKey);
      if (!sessionExists) {
        interrupted.push(run);
      }
    }
  }
  
  return interrupted;
}
```

**状态标志**：
- `completed` - 任务正常完成
- `failed` - 任务失败（明确终止）
- `running` - 运行中（可能中断）
- `pending` - 等待启动（可能中断）

### 3.2 恢复策略矩阵

| 任务类型 | 恢复策略 | 备注 |
|---------|---------|------|
| **短期任务** (<5分钟) | 重新启动 | 从头开始，成本低 |
| **长期任务** (>5分钟) | 检查点恢复 | 需要任务支持检查点 |
| **数据同步任务** | 增量恢复 | 从上次成功点继续 |
| **交互式任务** | 用户确认 | 可能需要用户重新输入 |

### 3.3 恢复实现

#### 方案 A：Gateway 内置恢复（推荐）
修改 Gateway 启动流程，在初始化完成后：
```bash
# Gateway 启动脚本新增恢复阶段
gateway_start() {
  # 1. 启动核心服务
  start_core_services();
  
  # 2. 执行中断任务恢复
  if [ -f "$STATE_DIR/subagents/runs.json" ]; then
    recover_interrupted_runs();
  fi
  
  # 3. 继续正常启动
  start_remaining_services();
}
```

#### 方案 B：外部恢复脚本
创建独立恢复脚本，通过 cron 或 systemd 在 Gateway 启动后执行：
```bash
#!/bin/bash
# ~/.openclaw/scripts/recover-interrupted-runs.sh

STATE_DIR="$HOME/.openclaw"
RUNS_FILE="$STATE_DIR/subagents/runs.json"

# 检查 Gateway 是否已就绪
if ! openclaw gateway status >/dev/null 2>&1; then
  echo "Gateway not running, skipping recovery"
  exit 0
fi

# 检测中断任务
INTERRUPTED=$(jq -r '.runs | to_entries[] | select(.value.status == "running") | .key' "$RUNS_FILE")

for run_id in $INTERRUPTED; do
  echo "Recovering run: $run_id"
  
  # 提取任务信息
  TASK=$(jq -r ".runs.\"$run_id\".task" "$RUNS_FILE")
  LABEL=$(jq -r ".runs.\"$run_id\".label" "$RUNS_FILE")
  
  # 重新启动任务（通过 Gateway API）
  curl -X POST "http://localhost:19000/api/v1/subagents/restart" \
    -H "Content-Type: application/json" \
    -d "{\"runId\": \"$run_id\", \"reason\": \"gateway_restart\"}"
done
```

#### 方案 C：Agent 自恢复
每个子代理任务定期保存检查点，Gateway 重启后：
1. 子代理检测到会话中断
2. 从检查点恢复状态
3. 继续执行

### 3.4 恢复完成后的待办显示

为了避免 Gateway 恢复后再次扫描 `tasks/*.yaml`，恢复阶段完成后应直接读取 `TASKS.md`，生成一张简洁待办卡片。

**原则**：
- 恢复完成后，`TASKS.md` 是默认待办入口
- 恢复提示和待办速览合并输出，避免二次扫描
- 若没有中断任务，也直接显示当前待办，不再执行任务目录扫描
- 只有当 `TASKS.md` 缺失、明显过期或与恢复结果冲突时，才回退读取单个 TaskCard
- **每次 boot check 完成后，都必须输出一条用户可见的 boot 回复，不允许因为“未发现中断任务”而静默结束**
- **boot 回复必须只输出模板本体，不追加解释、总结、说明文字或额外分析**
- **如果恢复检查已成功执行，即使结果为“未发现需恢复任务”，也必须返回 boot 回复模板，而不是 `NO_REPLY`**

**建议伪代码**：
```javascript
function showTodoAfterRecovery(recoveryResult) {
  const todoContext = loadTodoContextFromTASKS();

  return renderTodoCard({
    recoveryStatus: recoveryResult.recoveredCount > 0
      ? '检测到中断任务并已恢复'
      : '未发现中断任务',
    focus: todoContext.focus,
    active: todoContext.active,
    pending: todoContext.pending,
  });
}
```

**建议输出模板**：
```md
待办恢复卡片
- 恢复状态：<检测到中断任务并已恢复 / 未发现中断任务>
- 当前聚焦：<TASK-ID> / <任务名> / <状态>
- 进行中：<0-3 条>
- 等待 / 未完成：<0-3 条或无>
- 下一步：<一句动作>
```

## 4. 实施步骤

### 阶段 1：信息收集（当前）
1. 分析现有 `runs.json` 结构，确定状态字段
2. 测试 Gateway 停止对子代理的影响
3. 确定可用的恢复 API

### 阶段 2：最小可行恢复
1. 实现基础检测脚本
2. 支持重新启动短期任务
3. 添加恢复日志记录

### 阶段 3：高级恢复功能
1. 支持检查点恢复（需要任务配合）
2. 添加用户通知机制
3. 实现恢复策略配置

### 阶段 4：集成与优化
1. 将恢复逻辑集成到 Gateway
2. 性能优化（避免重复恢复）
3. 添加监控和告警

## 5. 配置选项

在 `openclaw.json` 中添加恢复配置：
```json
{
  "gateway": {
    "recovery": {
      "enabled": true,
      "mode": "auto", // auto, prompt, disabled
      "maxAgeHours": 24,
      "skipShortTasks": true,
      "notificationChannel": "webchat"
    }
  }
}
```

## 6. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| **重复执行** | 任务被执行两次 | 添加幂等性检查，使用唯一执行ID |
| **状态不一致** | 恢复后数据错误 | 强制关键任务实现检查点 |
| **恢复循环** | 不断尝试恢复失败任务 | 设置最大重试次数和超时 |
| **性能影响** | 启动时间延长 | 并行恢复，延迟启动非关键任务 |

## 7. 测试方案

### 单元测试
- 检测逻辑正确识别中断任务
- 恢复脚本正确处理各种状态

### 集成测试
1. 启动一个长期运行子代理
2. 手动停止 Gateway
3. 重启 Gateway
4. 验证任务是否自动恢复

### 压力测试
- 同时恢复多个中断任务
- 模拟部分恢复失败场景

## 8. 监控与日志

### 关键指标
- `gateway_recovery_attempts_total`
- `gateway_recovery_success_rate`
- `gateway_recovery_duration_seconds`

### 日志位置
- `~/.openclaw/logs/recovery-*.log`
- Gateway 系统日志

## 9. 回滚方案

如果恢复机制出现问题：
1. 临时禁用：设置 `"enabled": false`
2. 手动清理：删除错误的恢复状态
3. 版本回退：恢复到上一版本 Gateway

## 10. 后续优化

1. **智能恢复决策**：基于任务历史、资源需求预测恢复成功率
2. **跨节点恢复**：在集群环境中迁移中断任务到其他节点
3. **用户偏好学习**：根据用户历史决策优化恢复策略

## 附录

### A. runs.json 实际结构分析
根据当前系统分析，`runs.json` 结构如下：
```json
{
  "version": 2,
  "runs": {
    "run_id": {
      "runId": "...",
      "childSessionKey": "agent:main:subagent:...",
      "controllerSessionKey": "agent:main:main",
      "task": "任务描述",
      "cleanup": "keep",
      "expectsCompletionMessage": true,
      "spawnMode": "run",
      "label": "任务标签",
      "model": "...",
      "workspaceDir": "...",
      "createdAt": 时间戳,
      "startedAt": 时间戳,
      "sessionStartedAt": 时间戳,
      "accumulatedRuntimeMs": 运行时间,
      "cleanupHandled": true/false,
      "endedAt": 时间戳,           // 如有则表示已结束
      "outcome": { "status": "ok" }, // 结束状态
      "endedReason": "subagent-complete", // 结束原因
      "frozenResultText": "..."   // 冻结的结果文本
    }
  }
}
```

**关键检测点**：
- 任务是否中断：检查 `endedAt` 字段是否存在，如果不存在且会话已终止，则任务中断
- 恢复依据：使用 `frozenResultText` 恢复任务上下文

### B. 相关命令参考
```bash
# 查看当前运行任务
openclaw gateway status --detail

# 手动触发恢复（需实现）
openclaw gateway recover

# 查看恢复日志
tail -f ~/.openclaw/logs/gateway.log | grep -i recovery

# 检查 runs.json 结构
jq '.runs | keys' ~/.openclaw/subagents/runs.json
```

### C. 快速开始（简化方案）
如需立即实现基础恢复功能，可创建以下脚本：

```bash
#!/bin/bash
# ~/.openclaw/scripts/recover-interrupted.sh

STATE_DIR="$HOME/.openclaw"
RUNS_FILE="$STATE_DIR/subagents/runs.json"

# 检测未结束的任务
INTERRUPTED=$(jq -r '.runs | to_entries[] | select(.value.endedAt == null) | .key' "$RUNS_FILE" 2>/dev/null)

if [ -z "$INTERRUPTED" ]; then
  echo "未发现中断任务"
  exit 0
fi

echo "发现 ${#INTERRUPTED[@]} 个可能中断的任务"
for run_id in $INTERRUPTED; do
  LABEL=$(jq -r ".runs.\"$run_id\".label" "$RUNS_FILE" 2>/dev/null)
  echo "- $run_id ($LABEL)"
  
  # TODO: 实际恢复逻辑
  # 1. 检查对应会话是否存活
  # 2. 如会话死亡，重新 spawn 子代理
  # 3. 注入 frozenResultText 恢复上下文
  echo "  需要手动恢复或实现自动化"
done
```

将此脚本添加到 Gateway 启动后执行：
```bash
# 在 ~/.openclaw/openclaw.json 中添加
{
  "gateway": {
    "postStart": "$HOME/.openclaw/scripts/recover-interrupted.sh"
  }
}
```

---

## 11. 实施优先级建议

### 🟢 高优先级（本周内）
1. **分析实际数据结构**：确认 `runs.json` 完整结构和状态字段
2. **实现基础检测脚本**：能识别中断任务并列出
3. **手动恢复流程**：提供用户手动恢复的步骤说明

### 🟡 中优先级（下两周）
1. **自动化恢复**：实现脚本自动重新启动中断任务
2. **集成到 Gateway**：添加 `postStart` 钩子支持
3. **添加配置选项**：在 `openclaw.json` 中配置恢复行为

### 🔴 低优先级（后续迭代）
1. **智能恢复策略**：基于任务类型选择恢复方式
2. **检查点支持**：要求任务实现检查点机制
3. **集群恢复**：支持跨节点任务迁移

---

**调度链**：`architect -> BOOT.md 设计完成`

**下一步**：
1. **小青需要**：评审此设计，确认技术方向
2. **如需快速实现**：可让 **env-engineer** 实现基础检测脚本
3. **如需完整实现**：可让 **coder** 基于此设计开发，**tester** 验证
4. **关键决策**：选择实施方案（A:内置恢复 / B:外部脚本 / C:Agent自恢复）

请根据优先级和资源情况安排实施。"}]}
