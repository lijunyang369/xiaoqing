# browser-ops（青览）恢复标准

目标：确保 browser-ops 在新机器 / 新系统上不是“能说话”，而是真正拿到了 browser 工具能力。

## 通过标准

必须同时满足：
1. browser profile 可识别
2. browser-ops 建立的是新 session
3. 新 session 内已注入 browser 工具
4. 至少完成一次最低风险浏览验证

---

## 恢复步骤

### 1. 先检查浏览器 profile
```powershell
openclaw browser profiles
```

看点：
- 是否存在预期 profile
- browser 功能是否处于可用状态

### 2. 检查配置
重点看：
- `agents.list` 中是否存在 `browser-ops`
- `browser-ops.tools.allow` 是否含 `browser`
- `tools.profile` 是否会覆盖/限制 browser
- `bindings` 是否正确把账号路由到 `browser-ops`

### 3. 重建会话
重点原则：
- 不要只盯着旧会话的 `capabilities=none`
- 必须验证 **新建 session** 的工具快照
- 如果 Control UI 复用了旧上下文，要主动重建

### 4. 最低风险验证
建议验证动作：
- 打开 `https://example.com`
- 读取页面标题
- 截图或 snapshot（如可用）

不要做：
- 登录
- 提交表单
- 外部写入
- 高风险点击

---

## 常见失败模式

### 1. 旧 session 复用
现象：
- 明明配置已改，但会话仍显示旧能力

结论：
- 看到的是旧快照，不是新注入结果

### 2. gateway 已启动，但新能力未进入会话
现象：
- 配置层看起来没问题
- 但当前会话仍 `capabilities=none`

排查重点：
- Control UI 是否真的新建 session
- agent 绑定是否指向了正确账号
- browser 工具是否被 profile / allowlist 压掉

### 3. browser profile 不可用
现象：
- `openclaw browser profiles` 异常
- browser 无法启动或识别

排查重点：
- 本机浏览器是否安装
- profile 配置是否有效
- Gateway 是否正常

---

## 恢复完成判定

只有当以下条件全部满足时，才算青览恢复完成：
- `openclaw browser profiles` 正常
- browser-ops 新 session 建立成功
- 新 session 已拿到 browser 工具
- 已完成一次最低风险浏览验证
