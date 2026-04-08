# 架构审查：LOGIC-001 小青任务分配逻辑优化

最后更新：2026-04-08
角色：architect

## 1. 结论摘要

当前问题不是单点 bug，而是**任务状态模型、分配决策、展示视图**三层没有被同一个状态机约束，导致：

1. 同一任务在 `TASKS.md`、`tasks/*.yaml`、回复模板里出现不同状态
2. `assignedRole`、`stageOwner`、`releasedAt`、`startedAt` 的语义混用，任务是否真的被分发不清楚
3. 小青“该不该分发、分给谁、何时切换任务”缺少统一决策函数，容易把独立任务串在一起

建议把系统收敛为：
- **`tasks/*.yaml` 作为唯一权威状态源**
- **`TASKS.md` 改为自动生成的人类摘要视图**
- **任务分配改为显式路由决策函数**，由状态机和 WIP/主制约共同约束
- **回复模板只消费归一化后的状态，不直接拼接原始字段**

---

## 2. 审查证据

### 2.1 状态模型冲突
- `docs/TASK-SYSTEM.md` 定义状态：`Queued / Ready / In Progress / Waiting / Verifying / Done / Cancelled`
- `docs/TOC-TEMPLATES.md`、`docs/toc-operating-system.md`、任务卡定义状态：`Captured / Clarified / Ready / Released / Executing / Verifying / WaitingDecision / Blocked / Rework / Done`
- `AGENTS.md` 的进度表规则又依赖任务状态展示，但没有说明以哪套状态模型为准

### 2.2 摘要与底层任务卡漂移
- `TASKS.md` 中 `LOGIC-001` 状态为 `Released`
- `tasks/LOGIC-001.yaml` 状态为 `Executing`
- `TASKS.md` 中 `AVATAR-001` 状态为 `Ready`
- `tasks/AVATAR-001.yaml` 状态为 `Released`

这说明 `TASKS.md` 已经不是“单一事实来源”，而是一个可能过期的手工摘要。

### 2.3 释放与执行边界不清
- `tasks/LOGIC-001.yaml`：`status: Executing`，但 `releasedAt: null`
- `tasks/AVATAR-001.yaml`：`status: Released`，但 `startedAt` 已存在
- `tasks/T-20260407-001.yaml`：`status: Ready`，但同时已有 `releasedAt`、`startedAt`，notes 还记录过 `WaitingDecision`

这说明状态迁移没有不可变约束，字段可以互相打架。

---

## 3. 系统性问题

### 问题一：存在两套互不兼容的任务状态语言

**表现**
- TOC 系统按 `Released/Executing/WaitingDecision` 运转
- 任务系统文档和部分回复模板按 `In Progress/Waiting` 运转

**影响**
- 进度表颜色、排序、当前任务状态容易算错
- 任务分配逻辑无法基于统一状态判断是否该 spawn
- 同一个任务在不同层被当作不同阶段处理

**根因**
- 没有统一的 canonical status enum
- 展示层直接消费原始状态，而不是通过映射层

### 问题二：任务真相源被拆成了“任务卡 + 手工摘要”两份

**表现**
- `TASKS.md` 声称是单一事实来源
- `toc-state-calculator.md` 又以 `tasks/*.yaml` 为计算输入
- 实际数据已经漂移

**影响**
- 小青用 `TASKS.md` 决策时可能基于旧数据分配任务
- 子进程实际执行状态无法稳定回写到用户可见视图
- Gateway 重启恢复、待办卡片、进度表都可能读到不同答案

**根因**
- 没有定义“谁是权威，谁是投影视图”
- 没有状态更新后的自动同步机制

### 问题三：角色分配规则只有模板，没有决策引擎

**表现**
- `docs/spawn-task-templates.md` 只规定了怎么写 spawn 文本
- `docs/INTAKE-DECISION-PACKET-SOP.md` 只规定了回复顺序
- 但没有一个明确函数回答：
  - 这是聊天还是任务？
  - 是小青直做还是分发？
  - 分给哪个角色？
  - 何时允许从 `Ready` 进入 `Released`？
  - 新任务是否允许打断当前聚焦任务？

**影响**
- 小青容易基于“感觉”而不是规则分配
- 独立任务会被错误串联，例如 `LOGIC-001` 与 `BOOT-OPT-001`
- 用户指出“任务分配逻辑有问题”时，很难定位是 intake、release、owner 还是 rendering 出错

**根因**
- 缺少统一的 `route_task()` / `release_task()` / `switch_focus()` 架构接口

### 问题四：owner 字段语义重叠，责任转移不可追踪

**表现**
- 同时有 `stageOwner` 与 `assignedRole`
- 有时 `stageOwner` 写当前执行者，有时写协调者
- `releasedAt`、`startedAt` 与状态不一致

**影响**
- 任务是谁负责判断不稳定
- 当前进度表“执行agent”字段可能显示错人
- 恢复逻辑无法准确知道该恢复哪个角色、恢复到什么阶段

**根因**
- 没有对字段做严格语义定义和自动推导规则

---

## 4. 优化架构方案

## 4.1 统一状态模型

以 TOC 状态机为唯一正式状态：

`Captured -> Clarified -> Ready -> Released -> Executing -> Verifying -> Done`

分支状态：
- `WaitingDecision`
- `Blocked`
- `Rework`

展示层允许映射，但**禁止引入第二套持久化状态**。

建议映射：

| Canonical | 回复展示别名 |
|---|---|
| Captured | Captured |
| Clarified | Clarified |
| Ready | Ready |
| Released | Released |
| Executing | In Progress |
| WaitingDecision | Waiting Decision |
| Blocked | Blocked |
| Verifying | Verifying |
| Rework | Rework |
| Done | Done |

规则：
- 存储层只存 canonical
- 回复模板、进度表可渲染别名，但不能反向写回别名

## 4.2 权威数据源重构

### 推荐原则
- **权威源**：`tasks/*.yaml`
- **派生视图**：`TASKS.md`
- **会话缓存**：`TodoContext`

### 读写规则
1. 任务创建、状态变更、owner 变更，只写 `tasks/*.yaml`
2. 每次成功写入后，自动重建 `TASKS.md`
3. 会话内 `TodoContext` 只从最新 `TASKS.md` 读取
4. 若检测到 `TASKS.md.updatedAt < 任一 TaskCard.updatedAt`，视为摘要失效

### 收益
- 保留 `TASKS.md` 的启动性能优势
- 避免“用户看见的摘要”和“系统真实状态”分裂

## 4.3 显式任务分配决策引擎

增加三个核心函数：

```python
def classify_request(user_input) -> RequestKind:
    # chat | task | decision | recovery


def route_task(task, system_state) -> RoutingDecision:
    # direct | plan | architect | coder | env-engineer | debugger | tester


def release_task(task, system_state) -> ReleaseDecision:
    # allow / defer / merge-into-existing / waiting-decision
```

### route_task 决策维度
- 任务产物类型：规划 / 架构 / 实现 / 环境 / 调试 / 测试
- 风险等级：低 / 中 / 高
- 当前主制约
- 当前 WIP
- 是否需要俊阳拍板
- 是否与当前聚焦任务属于同一交付链

### 推荐路由矩阵

| 条件 | 默认路径 |
|---|---|
| 普通聊天 / 超短问答 | 小青直做 |
| 需拆解、排期、依赖协调 | plan |
| 架构评审、接口、技术权衡 | architect |
| 代码实现、直接改文件 | coder |
| 环境、依赖、部署、运行时 | env-engineer |
| 根因定位、复现、隔离 | debugger |
| 验证、回归、质量门禁 | tester |
| 需要俊阳拍板 | WaitingDecision + DecisionPacket |

### 任务切换规则
- 同一角色默认只保留 **1 个 focus task**
- 新任务与当前 focus 无直接依赖时，默认进入 `Ready`，不抢占 `Executing`
- 只有满足以下任一条件才允许抢占：
  1. 用户明确要求切换
  2. 当前任务阻塞
  3. 新任务优先级更高且会显著提升全局吞吐

这条规则正好可处理 `LOGIC-001` 与 `BOOT-OPT-001` 的边界，二者应为**两个独立 architect 任务**，而不是一个混合任务。

## 4.4 owner 字段收敛

建议字段语义改成：

```yaml
status: Ready | Released | Executing | ...
assignedRole: architect | coder | ... | null
coordinator: xiaoqing
executor: architect | coder | ... | null
releasedAt: <timestamp|null>
startedAt: <timestamp|null>
```

规则：
- `assignedRole`：目标执行角色，`Ready` 时即可存在
- `executor`：真正开始执行后才有值
- `coordinator`：默认是小青
- `stageOwner` 建议废弃，避免与 `assignedRole` 重叠

状态约束：
- `Released` 必须满足 `assignedRole != null` 且 `releasedAt != null`
- `Executing` 必须满足 `executor != null` 且 `startedAt != null`
- `Ready` 不得携带 `startedAt`
- `Done` 前必须经过 `Verifying` 或明确声明“无需验证”的特例

## 4.5 回复模板与进度表的正确接线

回复层不要直接从散落字段拼表格，改为：

```python
def build_progress_board(tasks):
    normalized = [normalize_task(t) for t in tasks]
    ranked = sort_for_board(normalized)
    return render_board(ranked)
```

其中 `normalize_task()` 负责：
- 校验状态是否合法
- 根据 canonical status 生成展示文案
- 根据 deadline/start 时间计算色块
- 发现冲突时输出 `dataConflict=true`

一旦发现如下冲突：
- `status=Executing` 但 `releasedAt=null`
- `status=Ready` 但 `startedAt!=null`
- `TASKS.md` 与 TaskCard 不一致

就不应继续静默展示，而应优先提示“小青内部任务状态存在冲突，已按 TaskCard 权威源纠偏”。

---

## 5. 与 BOOT-OPT-001 的接口关系

BOOT 恢复逻辑应直接复用上述状态机，而不是另起一套恢复判断。

### 恢复规则建议
- 只尝试恢复 `Released` / `Executing` 且 `doneAt == null` 的任务
- `Ready` 任务不恢复，只继续留在待分配池
- `WaitingDecision` 不自动恢复执行，只恢复为待决策项
- 恢复完成后重新生成 `TASKS.md`，再渲染“待办恢复卡片”

这样 `BOOT-OPT-001` 可以建立在 `LOGIC-001` 的状态机收敛之上，而不是绕过它。

---

## 6. 实施建议与时间表

### Phase 0，立即止血（0.5 天）
1. 明确 `tasks/*.yaml` 为权威源
2. 停止在新文档中继续使用 `In Progress / Waiting / Queued` 作为持久化状态
3. 手工校正已发现冲突任务：`LOGIC-001`、`AVATAR-001`、`T-20260407-001`

### Phase 1，模型收敛（0.5 到 1 天）
1. 在 `docs/TASK-SYSTEM.md` 中改为引用 TOC canonical 状态
2. 定义状态映射表，仅供展示层使用
3. 收敛 owner 字段，废弃或冻结 `stageOwner`

### Phase 2，分配逻辑产品化（1 天）
1. 落地 `classify_request()` / `route_task()` / `release_task()` 规则
2. 把 `docs/INTAKE-DECISION-PACKET-SOP.md` 从“回复模板”升级为“决策流程 + 接口契约”
3. 新增“任务切换规则”和“抢占规则”

### Phase 3，视图与恢复接线（1 天）
1. 让 `TASKS.md` 从 TaskCard 自动生成
2. 进度表和待办卡片统一读归一化数据
3. BOOT 恢复逻辑接入同一状态机

### Phase 4，验证（0.5 天）
1. 构造状态冲突样例做回归
2. 验证以下场景：
   - 新任务进入
   - 分发给 architect
   - 子进程开始执行
   - 任务等待用户决策
   - Gateway 重启恢复
   - 当前任务完成并暴露其他未完成任务

总计建议：**2.5 到 3.5 天**

---

## 7. 明确的下一步实现建议

### 最高优先级
1. **先修模型，不先修展示**。否则进度表只是把错误状态显示得更整齐。
2. 由 coder 或主进程先完成“状态枚举统一 + TASKS.md 改为派生视图”。
3. 随后再做 boot 恢复和回复模板接线。

### 建议分工
- **architect**：确认 canonical 状态机、路由规则、字段语义
- **coder**：实现状态归一化、摘要生成器、路由函数
- **tester**：做状态流转和恢复回归测试
- **小青**：按新规则维护当前 focus，不再把独立任务混在同一次 architect 分发里

### 最小实现路径
1. 建一个 `task-normalizer` 层
2. 建一个 `generate_TASKS_md()` 层
3. 建一个 `route_task()` 层
4. 再把进度表和 boot 恢复接到这三层上

---

## 8. 推荐决策

**推荐路径：先做状态机与真相源收敛，再做 boot 与回复模板。**

理由：
- 当前用户看到的“进度表异常”本质是数据模型问题
- 如果先改 boot 或模板，只会把错误状态传播到更多入口
- `BOOT-OPT-001` 可以作为 `LOGIC-001` 的下游任务，而不是并行抢修同一根因
