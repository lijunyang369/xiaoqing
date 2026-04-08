# Behavior Protocol Enforcer 技能架构设计

## 1. 概述

### 1.1 目标
设计一个完整的 OpenClaw 技能，用于在会话开始时自动提醒 agent 读取行为协议，并提供工具检查合规性。

### 1.2 核心功能
1. **自动提醒**：在会话开始时自动注入系统事件，提醒 agent 读取相应行为协议
2. **协议读取**：提供工具读取当前会话类型对应的行为协议
3. **合规检查**：提供工具检查 agent 行为是否符合协议规则
4. **会话类型检测**：自动识别 main session 和 subprocess session

## 2. 技能文件结构

```
skills/behavior-protocol-enforcer/
├── SKILL.md                    # 技能主文档（已存在）
├── package.json                # 技能包配置（新增）
├── index.js                    # 技能主入口（新增）
├── src/
│   ├── tools/
│   │   ├── read-protocol.js    # read_behavior_protocol 工具实现
│   │   └── check-compliance.js # check_compliance 工具实现
│   ├── events/
│   │   └── session-start.js    # 会话开始事件处理器
│   ├── utils/
│   │   ├── session-detector.js # 会话类型检测器
│   │   └── protocol-loader.js  # 协议文件加载器
│   └── index.js                # 模块导出
├── references/
│   └── openclaw-skill-api.md   # OpenClaw 技能 API 参考
└── scripts/
    └── install.js              # 技能安装脚本（可选）
```

## 3. 工具接口定义

### 3.1 read_behavior_protocol 工具

**函数签名**：
```javascript
async function readBehaviorProtocol(params = {}) {
  // 实现逻辑
}
```

**参数**：
- `protocol` (string, optional): 指定要读取的协议名称（如 "architect"）
- 如果未指定，自动基于会话标签检测

**返回值**：
```json
{
  "success": true,
  "protocol": "architect",
  "content": "协议文件内容...",
  "filePath": "/path/to/BEHAVIOR-PROTOCOL-ARCHITECT.md"
}
```

**错误处理**：
- 协议文件不存在：返回 `{success: false, error: "Protocol file not found", filePath: "...", suggestion: "Create the protocol file first"}`
- 读取失败：返回 `{success: false, error: "Failed to read protocol file", details: "..."}`

### 3.2 check_compliance 工具

**函数签名**：
```javascript
async function checkCompliance(params = {}) {
  // 实现逻辑
}
```

**参数**：
- `actions` (array, optional): 要检查的动作列表
- `timeframe` (string, optional): 时间范围，如 "last-10-messages", "today", "session"
- 如果未指定动作，自动从会话历史中提取最近10条消息

**返回值**：
```json
{
  "success": true,
  "complianceScore": 0.85,
  "violations": [
    {
      "rule": "必须读取协议后再开始工作",
      "violation": "未读取协议直接开始设计",
      "severity": "high",
      "suggestion": "立即运行 read_behavior_protocol"
    }
  ],
  "compliantActions": ["读取了协议文件", "遵循了设计流程"],
  "report": "合规性检查完成，发现1个高风险违规..."
}
```

**错误处理**：
- 无协议文件：返回 `{success: false, error: "No protocol available for compliance check"}`
- 无会话历史：返回 `{success: false, error: "No session history available for analysis"}`

## 4. 系统事件触发机制

### 4.1 会话开始事件

**触发时机**：
- 当 OpenClaw 启动新会话时
- 当技能被加载到会话中时

**实现方式**：
1. **OpenClaw 插件钩子**：注册 `onSessionStart` 钩子
2. **技能初始化**：在技能加载时自动注册事件监听器
3. **条件检测**：检测会话类型，生成相应提醒消息

**事件消息模板**：
```javascript
// Main session
{
  type: "system",
  content: "Behavior Protocol Enforcer loaded. Please read BEHAVIOR-PROTOCOL.md before proceeding."
}

// Subprocess session
{
  type: "system", 
  content: `You are a ${role} subprocess. Read BEHAVIOR-PROTOCOL-${role.toUpperCase()}.md before starting.`
}
```

### 4.2 会话类型检测

**检测逻辑**：
1. **会话标签分析**：检查会话标签是否包含子进程标识
   - "plan" → plan 子进程
   - "architect" → architect 子进程
   - "coder" → coder 子进程
   - 等等
2. **会话元数据**：检查会话配置中的 `agentType` 或 `role` 字段
3. **默认回退**：如果无法检测，视为 main session

**实现代码**：
```javascript
function detectSessionType(session) {
  const label = session.label?.toLowerCase() || '';
  const roles = ['plan', 'architect', 'coder', 'env-engineer', 'debugger', 'tester'];
  
  for (const role of roles) {
    if (label.includes(role)) {
      return role;
    }
  }
  
  return 'main';
}
```

## 5. 技能集成步骤

### 5.1 技能注册

**package.json 配置**：
```json
{
  "name": "behavior-protocol-enforcer",
  "version": "1.0.0",
  "description": "Enforce behavior protocols for OpenClaw agents",
  "type": "module",
  "main": "index.js",
  "openclaw": {
    "skill": true,
    "tools": [
      "read_behavior_protocol",
      "check_compliance"
    ],
    "events": [
      "session:start"
    ],
    "autoLoad": true
  }
}
```

### 5.2 工具注册

**index.js 主入口**：
```javascript
import { readBehaviorProtocol } from './src/tools/read-protocol.js';
import { checkCompliance } from './src/tools/check-compliance.js';
import { onSessionStart } from './src/events/session-start.js';

export default {
  name: 'behavior-protocol-enforcer',
  version: '1.0.0',
  
  // 工具定义
  tools: {
    read_behavior_protocol: {
      description: 'Read the behavior protocol for current session',
      handler: readBehaviorProtocol,
      params: {
        protocol: { type: 'string', optional: true }
      }
    },
    check_compliance: {
      description: 'Check compliance with behavior protocol',
      handler: checkCompliance,
      params: {
        actions: { type: 'array', optional: true },
        timeframe: { type: 'string', optional: true }
      }
    }
  },
  
  // 事件处理器
  events: {
    'session:start': onSessionStart
  },
  
  // 初始化函数
  async init(context) {
    console.log('Behavior Protocol Enforcer skill initialized');
    return true;
  }
};
```

### 5.3 自动加载机制

**方式1：全局技能配置**
- 在 OpenClaw 配置文件中添加技能到 `autoLoadSkills` 列表
- 确保技能在所有会话中自动加载

**方式2：工作区技能**
- 将技能放置在 workspace 的 `skills/` 目录下
- OpenClaw 会自动加载工作区技能

## 6. 错误处理策略

### 6.1 协议文件不存在
- **检测**：在读取前检查文件是否存在
- **处理**：返回友好的错误消息，建议创建协议文件
- **降级**：如果协议文件缺失，仍允许其他功能正常工作

### 6.2 工具调用失败
- **输入验证**：验证参数格式和类型
- **异常捕获**：使用 try-catch 包装工具逻辑
- **优雅降级**：返回详细的错误信息，而不是崩溃

### 6.3 会话检测失败
- **默认值**：无法检测时视为 main session
- **日志记录**：记录检测失败的原因用于调试
- **用户提示**：提示用户手动指定会话类型

## 7. 配置与自定义

### 7.1 协议文件位置
```javascript
// 可配置的协议文件路径
const PROTOCOL_PATHS = {
  main: 'memory/long-term/BEHAVIOR-PROTOCOL.md',
  plan: 'memory/long-term/BEHAVIOR-PROTOCOL-PLAN.md',
  architect: 'memory/long-term/BEHAVIOR-PROTOCOL-ARCHITECT.md',
  // ... 其他角色
};
```

### 7.2 合规检查规则
```javascript
// 可配置的合规规则
const COMPLIANCE_RULES = {
  mustReadProtocolFirst: {
    check: (actions, protocol) => actions[0]?.includes('read_behavior_protocol'),
    message: '必须首先读取行为协议',
    severity: 'high'
  },
  // ... 其他规则
};
```

## 8. 测试策略

### 8.1 单元测试
- 工具函数测试
- 会话类型检测测试
- 协议文件读取测试

### 8.2 集成测试
- 技能加载测试
- 事件触发测试
- 端到端工作流测试

### 8.3 测试文件结构
```
__tests__/
├── unit/
│   ├── session-detector.test.js
│   ├── protocol-loader.test.js
│   └── compliance-checker.test.js
├── integration/
│   ├── skill-load.test.js
│   └── event-trigger.test.js
└── fixtures/
    ├── protocol-files/
    └── session-data/
```

## 9. 部署与维护

### 9.1 安装步骤
1. 将技能目录复制到 workspace 的 `skills/` 目录
2. 运行 `npm install` 安装依赖（如果有）
3. 重启 OpenClaw 或重新加载技能

### 9.2 更新机制
- 技能版本管理
- 向后兼容性保证
- 配置迁移支持

### 9.3 监控与日志
- 技能加载日志
- 工具调用统计
- 错误率监控

## 10. 下一步实施建议

### 10.1 文件创建清单
coder 需要创建以下文件：

1. **核心文件**：
   - `skills/behavior-protocol-enforcer/package.json` - 技能包配置
   - `skills/behavior-protocol-enforcer/index.js` - 技能主入口

2. **工具实现**：
   - `skills/behavior-protocol-enforcer/src/tools/read-protocol.js`
   - `skills/behavior-protocol-enforcer/src/tools/check-compliance.js`

3. **事件处理**：
   - `skills/behavior-protocol-enforcer/src/events/session-start.js`

4. **工具函数**：
   - `skills/behavior-protocol-enforcer/src/utils/session-detector.js`
   - `skills/behavior-protocol-enforcer/src/utils/protocol-loader.js`

5. **测试文件**（可选）：
   - `skills/behavior-protocol-enforcer/__tests__/unit/session-detector.test.js`
   - `skills/behavior-protocol-enforcer/__tests__/integration/skill-load.test.js`

6. **文档更新**：
   - 更新 `SKILL.md` 中的工具定义，与实际实现保持一致
   - 添加 `references/openclaw-skill-api.md` 参考文档

### 10.2 实施优先级
1. **高优先级**：工具实现和基本事件触发
2. **中优先级**：错误处理和配置选项
3. **低优先级**：高级功能和测试覆盖

### 10.3 依赖检查
- 确认 OpenClaw 版本支持技能插件系统
- 检查必要的文件系统访问权限
- 验证协议文件目录结构

## 11. 风险与缓解

### 11.1 技术风险
- **OpenClaw API 变更**：技能可能因 API 变更而失效
  - *缓解*：使用版本锁定，定期更新适配
- **文件权限问题**：无法读取协议文件
  - *缓解*：添加权限检查和友好的错误消息

### 11.2 功能风险
- **误检测**：错误识别会话类型
  - *缓解*：提供手动覆盖选项，添加检测置信度评分
- **性能影响**：合规检查可能影响会话性能
  - *缓解*：优化检查算法，添加性能监控

### 11.3 维护风险
- **协议文件分散**：多个协议文件难以维护
  - *缓解*：考虑协议文件集中管理方案
- **技能兼容性**：与其他技能冲突
  - *缓解*：明确定义技能边界，避免功能重叠

## 12. 总结

本架构设计提供了 behavior-protocol-enforcer 技能的完整实现方案，包括：

1. **清晰的技能结构**：模块化设计，便于维护和扩展
2. **完整的工具实现**：read_behavior_protocol 和 check_compliance 工具的具体实现
3. **自动事件触发**：会话开始时自动提醒读取协议
4. **健壮的错误处理**：处理各种异常情况
5. **灵活的配置**：支持自定义协议路径和规则

实施此架构后，技能将从纯文档变为实际可用的工具，真正实现行为协议的自动提醒和合规检查功能。