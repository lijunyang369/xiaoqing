# Agent 恢复验证清单

目标：新机器 / 新系统恢复后，快速确认各 agent 是否回到可用状态。

## 通用检查

对所有 agent 都先检查：
- 配置模板已复制为真实配置
- 相关 env 已注入
- workspace 路径正确
- Gateway 已启动
- 当前 agent 能成功建立新 session

---

## main（小青）

应验证：
- 能在主会话正常回复
- 能读写 workspace 文件
- 能使用 memory_search / memory_get
- 能执行 git / 文档整理 / 轻量排障

建议验证：
- 发送一条测试消息
- 读取 `SOUL.md` / `USER.md`
- 执行一次 `openclaw gateway status`

---

## windows-ops（青卫）

应验证：
- agentDir / workspace 路径存在
- 能承接 Windows 运维任务
- 能进行本机命令检查

建议验证：
- 建立一个新会话
- 执行低风险状态检查
- 确认不会落到错误 workspace

---

## news-brief（青闻）

应验证：
- 可正常创建新会话
- 可执行资讯整理任务
- 输出格式正常

建议验证：
- 发起一次简短新闻候选整理测试

---

## browser-ops（青览）

应验证：
- 新会话确实是新建，不是复用旧上下文
- browser 工具被正确注入
- 浏览器 profile 可识别
- 最低风险浏览动作可执行

详细标准见：`BROWSER-OPS-RECOVERY.md`

---

## 最终通过标准

满足以下 4 条，可认为 agent 层恢复完成：
- main 正常
- windows-ops 正常
- news-brief 正常
- browser-ops 正常拿到 browser 能力
