# Behavior Protocol Enforcer 实施清单

## 1. 文件创建清单

### 1.1 必须创建的核心文件

**1. package.json - 技能包配置**
```
skills/behavior-protocol-enforcer/package.json
```
内容模板：
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
    "autoLoad": true,
    "requires": {
      "openclaw": ">=2026.4.5"
    }
  },
  "scripts": {
    "test": "node --test"
  }
}
```

**2. index.js - 技能主入口**
```
skills/behavior-protocol-enforcer/index.js
```
内容模板：
```javascript
import { readBehaviorProtocol } from './src/tools/read-protocol.js';
import { checkCompliance } from './src/tools/check-compliance.js';
import { onSessionStart } from './src/events/session-start.js';

export default {
  name: 'behavior-protocol-enforcer',
  version: '1.0.0',
  
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
  
  events: {
    'session:start': onSessionStart
  },
  
  async init(context) {
    console.log('Behavior Protocol Enforcer skill initialized');
    return true;
  }
};
```

### 1.2 工具实现文件

**3. read-protocol.js - 协议读取工具**
```
skills/behavior-protocol-enforcer/src/tools/read-protocol.js
```
核心功能：
- 检测当前会话类型
- 读取对应的协议文件
- 处理文件不存在等错误
- 返回格式化结果

**4. check-compliance.js - 合规检查工具**
```
skills/behavior-protocol-enforcer/src/tools/check-compliance.js
```
核心功能：
- 获取会话历史或指定动作
- 加载对应协议规则
- 检查动作是否符合协议
- 生成合规报告

### 1.3 事件处理文件

**5. session-start.js - 会话开始事件处理器**
```
skills/behavior-protocol-enforcer/src/events/session-start.js
```
核心功能：
- 监听会话开始事件
- 检测会话类型
- 生成相应的提醒消息
- 发送系统事件

### 1.4 工具函数文件

**6. session-detector.js - 会话类型检测器**
```
skills/behavior-protocol-enforcer/src/utils/session-detector.js
```
核心功能：
- 分析会话标签和元数据
- 识别 main session 和 subprocess session
- 返回检测到的角色类型

**7. protocol-loader.js - 协议文件加载器**
```
skills/behavior-protocol-enforcer/src/utils/protocol-loader.js
```
核心功能：
- 构建协议文件路径
- 检查文件是否存在
- 读取文件内容
- 缓存已读取的协议

### 1.5 目录结构创建
需要创建的目录：
```
mkdir -p skills/behavior-protocol-enforcer/src/tools
mkdir -p skills/behavior-protocol-enforcer/src/events
mkdir -p skills/behavior-protocol-enforcer/src/utils
mkdir -p skills/behavior-protocol-enforcer/references
mkdir -p skills/behavior-protocol-enforcer/scripts
```

## 2. 实施步骤

### 步骤1：创建目录结构
```bash
cd ~/.openclaw/workspace/skills/behavior-protocol-enforcer
mkdir -p src/{tools,events,utils} references scripts
```

### 步骤2：创建 package.json
```bash
# 使用上面提供的模板创建 package.json
```

### 步骤3：创建工具函数文件
1. 先创建 `src/utils/session-detector.js`
2. 再创建 `src/utils/protocol-loader.js`
3. 这两个是基础工具，其他文件会依赖它们

### 步骤4：创建工具实现
1. 创建 `src/tools/read-protocol.js`
2. 创建 `src/tools/check-compliance.js`

### 步骤5：创建事件处理器
1. 创建 `src/events/session-start.js`

### 步骤6：创建主入口文件
1. 创建 `index.js`

### 步骤7：更新 SKILL.md
更新现有的 SKILL.md，确保工具描述与实际实现一致。

### 步骤8：测试技能
1. 重启 OpenClaw 或重新加载技能
2. 测试 `read_behavior_protocol` 工具
3. 测试 `check_compliance` 工具
4. 验证会话开始时的自动提醒

## 3. 关键实现细节

### 3.1 会话类型检测逻辑
```javascript
// session-detector.js 中的核心逻辑
export function detectSessionType(sessionContext) {
  // 1. 从会话标签检测
  const label = sessionContext.label?.toLowerCase() || '';
  const subprocessRoles = [
    'plan', 'architect', 'coder', 
    'env-engineer', 'debugger', 'tester'
  ];
  
  for (const role of subprocessRoles) {
    if (label.includes(role)) {
      return role;
    }
  }
  
  // 2. 从会话元数据检测
  if (sessionContext.agentType) {
    return sessionContext.agentType;
  }
  
  // 3. 默认返回 main
  return 'main';
}
```

### 3.2 协议文件路径映射
```javascript
// protocol-loader.js 中的路径映射
const PROTOCOL_FILES = {
  main: 'memory/long-term/BEHAVIOR-PROTOCOL.md',
  plan: 'memory/long-term/BEHAVIOR-PROTOCOL-PLAN.md',
  architect: 'memory/long-term/BEHAVIOR-PROTOCOL-ARCHITECT.md',
  coder: 'memory/long-term/BEHAVIOR-PROTOCOL-CODER.md',
  'env-engineer': 'memory/long-term/BEHAVIOR-PROTOCOL-ENV-ENGINEER.md',
  debugger: 'memory/long-term/BEHAVIOR-PROTOCOL-DEBUGGER.md',
  tester: 'memory/long-term/BEHAVIOR-PROTOCOL-TESTER.md'
};
```

### 3.3 错误处理模式
```javascript
// 统一的错误处理模式
export async function safeReadProtocol(protocolName) {
  try {
    const filePath = getProtocolPath(protocolName);
    
    // 检查文件是否存在
    if (!await fileExists(filePath)) {
      return {
        success: false,
        error: `Protocol file not found: ${filePath}`,
        suggestion: `Create ${filePath} with the behavior protocol for ${protocolName}`
      };
    }
    
    // 读取文件
    const content = await readFile(filePath, 'utf-8');
    
    return {
      success: true,
      protocol: protocolName,
      content,
      filePath
    };
  } catch (error) {
    return {
      success: false,
      error: `Failed to read protocol: ${error.message}`,
      details: error.stack
    };
  }
}
```

## 4. 测试用例

### 4.1 手动测试步骤
1. **启动新会话**：检查是否收到协议提醒
2. **调用 read_behavior_protocol**：验证能否正确读取协议
3. **调用 check_compliance**：验证合规检查功能
4. **错误场景测试**：
   - 删除协议文件，测试错误处理
   - 使用无效参数调用工具

### 4.2 预期结果
1. 新会话开始时，自动显示："Behavior Protocol Enforcer loaded. Please read the appropriate behavior protocol before proceeding."
2. `read_behavior_protocol` 返回协议内容
3. `check_compliance` 返回合规报告
4. 错误情况返回友好的错误消息

## 5. 依赖和兼容性

### 5.1 OpenClaw 版本要求
- 需要 OpenClaw >= 2026.4.5（支持技能插件系统）
- 确认技能 API 可用

### 5.2 文件系统权限
- 需要读取 `memory/long-term/` 目录的权限
- 需要读取会话历史的能力

### 5.3 协议文件要求
- 协议文件必须存在才能正常工作
- 文件格式应为 Markdown

## 6. 完成标准

### 6.1 功能完成标准
- [ ] 技能能正确加载到 OpenClaw
- [ ] 新会话开始时自动显示提醒
- [ ] `read_behavior_protocol` 工具能正确读取协议
- [ ] `check_compliance` 工具能生成合规报告
- [ ] 错误处理工作正常

### 6.2 代码质量标准
- [ ] 所有文件都有适当的错误处理
- [ ] 代码有清晰的注释
- [ ] 遵循一致的代码风格
- [ ] 无明显的性能问题

### 6.3 文档完成标准
- [ ] SKILL.md 更新为最新
- [ ] 关键函数有文档注释
- [ ] 使用说明清晰完整

## 7. 常见问题解决

### 7.1 技能无法加载
- 检查 package.json 格式
- 检查 OpenClaw 版本兼容性
- 查看 OpenClaw 日志

### 7.2 工具调用失败
- 检查工具函数导出
- 验证参数格式
- 检查文件权限

### 7.3 事件不触发
- 确认事件名称正确
- 检查会话开始事件是否被触发
- 验证事件处理器注册

## 8. 后续优化建议

### 8.1 短期优化
1. 添加协议文件缓存，提高读取性能
2. 完善合规检查规则
3. 添加更多测试用例

### 8.2 长期优化
1. 支持自定义协议文件位置
2. 添加协议版本管理
3. 实现协议自动更新检查
4. 添加可视化合规报告

## 9. 交付物清单

完成实施后，应交付以下文件：

1. `skills/behavior-protocol-enforcer/package.json`
2. `skills/behavior-protocol-enforcer/index.js`
3. `skills/behavior-protocol-enforcer/src/tools/read-protocol.js`
4. `skills/behavior-protocol-enforcer/src/tools/check-compliance.js`
5. `skills/behavior-protocol-enforcer/src/events/session-start.js`
6. `skills/behavior-protocol-enforcer/src/utils/session-detector.js`
7. `skills/behavior-protocol-enforcer/src/utils/protocol-loader.js`
8. 更新后的 `skills/behavior-protocol-enforcer/SKILL.md`
9. 可选的测试文件

所有文件应通过基本功能测试，确保技能在实际环境中可用。