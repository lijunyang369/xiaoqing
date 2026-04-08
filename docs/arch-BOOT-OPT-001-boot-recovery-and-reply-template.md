# 架构设计：BOOT-OPT-001 boot 恢复逻辑与回复模板优化

最后更新：2026-04-08  
角色：architect

## 1. 设计目标

1. boot 启动时只基于统一 TOC canonical 状态机处理恢复
2. 只恢复 `Released` / `Executing` 且未完成任务
3. `Ready` 任务不自动恢复，只保留在待分配池
4. 恢复完成后先重建 `TASKS.md`，再渲染简洁启动回复
5. 启动回复模板只保留两块：
   - 中断任务结果
   - 任务回复模板内容

## 2. 状态机约束

唯一正式状态机：

`Captured -> Clarified -> Ready -> Released -> Executing -> Verifying -> Done`

恢复阶段只允许消费以下状态：

| 状态 | 是否自动恢复 | 原因 |
|---|---|---|
| Captured | 否 | 尚未澄清 |
| Clarified | 否 | 尚未进入可执行池 |
| Ready | 否 | 只是待分配，不应在 boot 时自动释放 |
| Released | 是 | 已完成分配但可能尚未重新拉起执行者 |
| Executing | 是 | 启动前处于执行中，属于中断恢复主对象 |
| Verifying | 否 | 默认回到待验证，不自动继续执行 |
| WaitingDecision | 否 | 需要俊阳裁决 |
| Blocked | 否 | 阻塞未解除 |
| Rework | 否 | 需重新进入正常分配链 |
| Done | 否 | 已完成 |

## 3. 推荐 boot 恢复架构

## 3.1 权威数据源

- `tasks/*.yaml`：唯一权威源
- `TASKS.md`：自动生成摘要视图
- `runs.json` / session 状态：运行态辅助证据，不是任务真相源

因此 boot 恢复不应再以 `runs.json` 中 `endedAt == null` 作为唯一判断，而应改为：

1. 先读取 TaskCard
2. 按 canonical status 找出候选任务
3. 再用 `runs.json` 与 session 状态判断这些候选任务是否真的被中断

## 3.2 恢复规则

### 候选筛选

```python
def collect_recovery_candidates(tasks):
    return [
        t for t in tasks
        if t.status in {"Released", "Executing"}
        and t.status != "Done"
    ]
```

### 判定逻辑

```python
def should_recover(task, run_state):
    if task.status == "Released":
        return task.assignedRole is not None and not run_state.has_live_session

    if task.status == "Executing":
        return task.executor is not None and not run_state.has_live_session

    return False
```

### 恢复动作

| 任务状态 | 恢复动作 | 状态处理 |
|---|---|---|
| Released | 重新执行 `release_task()` 的恢复分支，重新拉起目标角色 | 保持 `Released`，待子进程真正启动后再进入 `Executing` |
| Executing | 生成 resume 包并重启同角色执行会话 | 保持 `Executing`，并追加恢复事件日志 |

### 明确禁止

- 不自动恢复 `Ready`
- 不自动把 `WaitingDecision`、`Blocked`、`Verifying` 重新推进到执行态
- 不根据 `TASKS.md` 直接做恢复决策
- 不把“无中断任务”再包装成新的恢复动作

## 3.3 启动流程

```python
def boot_recovery_flow():
    tasks = load_taskcards()
    candidates = collect_recovery_candidates(tasks)
    recovery_result = recover_candidates(candidates)
    regenerate_tasks_md(tasks)
    todo_context = load_todo_context_from_tasks_md()
    return render_boot_reply(recovery_result, todo_context)
```

推荐拆成 5 个明确步骤：

1. `load_taskcards()`
2. `collect_recovery_candidates()`
3. `recover_candidates()`
4. `regenerate_TASKS_md()`
5. `render_boot_reply()`

这样能与 `classify_request()`、`route_task()`、`release_task()` 保持同一套职责边界。

## 3.4 与现有脚本的集成建议

当前 `recover-interrupted.sh` 存在三个架构问题：

1. 以 `runs.json` 为主，而不是以 TaskCard 为主
2. 用 `grep` 统计 `TASKS.md`，不是消费结构化摘要
3. “发现未结束任务”与“应当恢复任务”被混为一谈

### 最小集成路径

短期不要推翻脚本入口，但应重构其内部职责：

- 保留 `postStart -> recover-interrupted.sh` 入口
- 脚本只做“调用恢复服务/恢复命令”
- 真正的候选筛选、状态校验、`TASKS.md` 重建、模板渲染下沉到统一任务层

即：

```bash
recover-interrupted.sh
  -> openclaw gateway recover --mode boot
```

由 `gateway recover` 或内部恢复模块完成：

- TaskCard 扫描
- run/session 交叉校验
- 恢复执行
- TASKS.md 重建
- 启动回复渲染

这比继续在 shell 中堆 `jq + grep` 稳定得多。

## 4. 回复模板设计

## 4.1 模板原则

- 只保留两块
- 简洁，可直接在 boot 后输出
- 第一块先说恢复结果
- 第二块再给当前待办与任务回复信息
- 数据统一来自“恢复后的 `TASKS.md` 摘要”

## 4.2 标准模板

```md
## 中断任务结果
- 恢复状态：<已恢复 N 个任务 / 未发现需恢复任务 / 发现 N 个任务但未自动恢复>
- 恢复任务：<TASK-ID 列表；无则写 无>
- 未自动恢复：<TASK-ID + 原因；无则写 无>

## 任务回复模板内容
- 当前聚焦：<TASK-ID> / <任务名> / <状态>
- 进行中：<0-3 条；无则写 无>
- 等待 / 未完成：<0-3 条；无则写 无>
- 下一步：<一句动作>
```

## 4.3 三种渲染场景

### A. 无需恢复

```md
## 中断任务结果
- 恢复状态：未发现需恢复任务
- 恢复任务：无
- 未自动恢复：无

## 任务回复模板内容
- 当前聚焦：AVATAR-001 / 修复 avatar 的展示异常 / Ready
- 进行中：TOC-TRIAL-001，TOC-001
- 等待 / 未完成：BOOT-OPT-001
- 下一步：按当前聚焦任务继续分配并执行
```

### B. 成功恢复

```md
## 中断任务结果
- 恢复状态：已恢复 1 个任务
- 恢复任务：BOOT-OPT-001
- 未自动恢复：无

## 任务回复模板内容
- 当前聚焦：BOOT-OPT-001 / 优化boot逻辑和回复模板 / Executing
- 进行中：BOOT-OPT-001
- 等待 / 未完成：LOGIC-001
- 下一步：等待恢复后的 architect 会话继续产出结果
```

### C. 有候选但未自动恢复

```md
## 中断任务结果
- 恢复状态：发现 2 个任务但未自动恢复
- 恢复任务：无
- 未自动恢复：TASK-A（WaitingDecision），TASK-B（Blocked）

## 任务回复模板内容
- 当前聚焦：TASK-A / <任务名> / WaitingDecision
- 进行中：无
- 等待 / 未完成：TASK-A，TASK-B
- 下一步：先处理待决策或阻塞项，再决定是否重新释放任务
```

## 5. 与 LOGIC-001 的集成方案

## 5.1 接口对齐

BOOT-OPT-001 应直接接到 LOGIC-001 推荐的三类函数：

```python
classify_request()
route_task()
release_task()
```

新增恢复侧接口：

```python
collect_recovery_candidates()
recover_task()
render_boot_reply()
```

职责关系：

- `classify_request()`：只处理用户输入路由
- `route_task()`：决定任务应给谁执行
- `release_task()`：让 `Ready -> Released`
- `collect_recovery_candidates()`：boot 时找出可恢复任务
- `recover_task()`：对 `Released/Executing` 做恢复
- `render_boot_reply()`：输出两块式启动回复

## 5.2 状态迁移兼容

boot 恢复不新增第二套状态，只允许以下迁移：

- `Released -> Released`（恢复拉起中）
- `Released -> Executing`（新子进程确认启动后）
- `Executing -> Executing`（恢复执行）
- `Executing -> Blocked`（恢复失败且需人工介入）

不允许：

- `Ready -> Executing`
- `WaitingDecision -> Executing`
- `Blocked -> Executing`

## 5.3 TASKS.md 重建时机

强制规则：

1. 恢复动作完成
2. 回写 TaskCard / 恢复日志
3. 重新生成 `TASKS.md`
4. 再渲染启动回复

这样才能避免“恢复结果已变化，但回复仍引用旧摘要”。

## 6. 实施建议与时间表

## Phase 1，模型接线（0.5 天）

- 确认 boot 恢复只认 canonical 状态
- 明确 `tasks/*.yaml` 为恢复权威源
- 定义 `collect_recovery_candidates()` / `recover_task()` 输入输出

## Phase 2，恢复链路改造（0.5 到 1 天）

- 将现有 shell 脚本改为轻入口
- 把候选筛选、恢复判定、TASKS.md 重建迁到统一任务层
- 增加恢复失败落 `Blocked` 或恢复备注的规则

## Phase 3，模板接线与验证（0.5 天）

- 落地两块式启动回复模板
- 验证三类场景：无恢复、恢复成功、发现但不恢复
- 验证 `TASKS.md` 与 TaskCard 一致性

总计建议：**1.5 到 2 天**

## 7. 关键决策建议

推荐路径：**先按 LOGIC-001 的统一状态机接线，再以最小改动重构现有恢复脚本入口。**

原因：

1. 这能满足“有则恢复，没有就算了”的需求，同时不破坏任务池语义
2. 可以复用现有 `postStart` 集成点，实施成本低
3. 能避免继续把 `runs.json` 和 `TASKS.md` 当成双真相源
4. 启动回复模板可以稳定消费恢复后的摘要，不再出现信息漂移

## 8. 交付给实现角色的具体要求

### 给 coder
- 实现 `collect_recovery_candidates()`、`recover_task()`、`render_boot_reply()`
- 将 `TASKS.md` 改为恢复完成后的必经重建步骤
- 把 shell 中的业务判断迁出

### 给 tester
- 回归场景至少覆盖：
  - 无候选任务
  - `Released` 任务恢复
  - `Executing` 任务恢复
  - `Ready` 任务不恢复
  - `WaitingDecision` 不恢复
  - 恢复后 `TASKS.md` 与回复模板一致

---

调度链：小青 -> architect -> 结果汇总
