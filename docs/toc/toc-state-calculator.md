# TOC 状态计算与自动更新

版本：v1.0  
适用对象：小青  
目标：定义如何自动收集证据、计算指标、更新系统状态

---

## 1. 状态计算总览

### 1.1 计算目标
为 TOC 系统提供准确的证据数据，包括：

- 各环节队列长度
- 平均等待时间
- 返工率
- 中断频率
- 当前主制约判断

### 1.2 计算频率
- **高频**：每 2-4 小时（轻量扫描）
- **低频**：每日 1-2 次（完整计算）
- **触发时**：状态变化时（增量更新）

### 1.3 数据源
- TaskCard 文件（`tasks/` 目录或内存）
- 状态变化日志
- 时间戳记录

---

## 2. 证据指标计算方法

### 2.1 队列长度计算
计算每个环节有多少 TaskCard 处于特定状态。

```python
def calculate_queue_lengths():
    # 读取所有 TaskCard
    tasks = load_all_taskcards()
    
    queues = {
        "waiting_decision": 0,    # WaitingDecision 状态
        "verifying": 0,           # Verifying 状态
        "blocked": 0,             # Blocked 状态
        "executing": 0,           # Executing 状态
        "ready": 0,               # Ready 状态（未释放）
    }
    
    for task in tasks:
        status = task["status"]
        if status in queues:
            queues[status] += 1
    
    return queues
```

### 2.2 平均等待时间计算
计算 TaskCard 在各环节的停留时间。

```python
def calculate_avg_wait_times():
    tasks = load_all_taskcards()
    
    wait_times = {
        "waiting_decision": [],
        "verifying": [],
        "blocked": [],
    }
    
    for task in tasks:
        status = task["status"]
        if status in wait_times:
            # 计算在当前状态的停留时间
            entered_at = task.get(f"entered_{status}_at")
            if entered_at:
                wait_hours = (now() - entered_at).total_seconds() / 3600
                wait_times[status].append(wait_hours)
    
    # 计算平均值
    avg_wait = {}
    for status, times in wait_times.items():
        if times:
            avg_wait[status] = sum(times) / len(times)
        else:
            avg_wait[status] = 0
    
    return avg_wait
```

### 2.3 返工率计算
计算从 `Verifying` 进入 `Rework` 的比例。

```python
def calculate_rework_rate(days=7):
    tasks = load_recent_taskcards(days)
    
    total_verified = 0
    total_reworked = 0
    
    for task in tasks:
        # 检查是否有验证历史
        if "verifiedAt" in task:
            total_verified += 1
        
        # 检查是否有返工
        if task.get("reworkCount", 0) > 0:
            total_reworked += 1
    
    if total_verified == 0:
        return 0.0
    
    return total_reworked / total_verified
```

### 2.4 中断频率计算
计算每日影响主制约的中断次数。

```python
def calculate_interrupt_frequency(days=7):
    # 从日志或 TaskCard notes 中提取中断记录
    logs = load_system_logs(days)
    
    interrupts = 0
    for log in logs:
        if is_interrupt_event(log):
            interrupts += 1
    
    # 计算每日平均值
    return interrupts / days
```

---

## 3. 主制约识别算法

### 3.1 证据权重
不同证据的权重不同：

- **队列长度权重**：40%
- **平均等待时间权重**：30%
- **返工率权重**：20%
- **中断频率权重**：10%

### 3.2 评分计算
```python
def calculate_constraint_score(queue_len, avg_wait, rework_rate, interrupt_freq):
    # 归一化处理
    norm_queue = queue_len / max(queue_len, 1)
    norm_wait = avg_wait / max(avg_wait, 1)
    norm_rework = rework_rate / max(rework_rate, 0.01)
    norm_interrupt = interrupt_freq / max(interrupt_freq, 1)
    
    # 加权计算
    score = (
        norm_queue * 0.4 +
        norm_wait * 0.3 +
        norm_rework * 0.2 +
        norm_interrupt * 0.1
    )
    
    return score
```

### 3.3 主制约判断
```python
def identify_main_constraint():
    # 计算各环节指标
    metrics = {}
    
    for stage in ["decision", "verification", "environment", "implementation", "planning"]:
        queue = get_queue_for_stage(stage)
        wait = get_wait_for_stage(stage)
        rework = get_rework_for_stage(stage)
        interrupt = get_interrupt_for_stage(stage)
        
        score = calculate_constraint_score(queue, wait, rework, interrupt)
        metrics[stage] = {
            "score": score,
            "queue": queue,
            "wait": wait,
            "rework": rework,
            "interrupt": interrupt
        }
    
    # 找出分数最高的环节
    main_stage = max(metrics.items(), key=lambda x: x[1]["score"])
    
    # 判断是否需要切换主制约
    current_constraint = load_current_constraint()
    
    if main_stage[0] != current_constraint["name"]:
        # 检查证据是否充分
        if has_sufficient_evidence(metrics[main_stage[0]]):
            return main_stage[0], metrics
        else:
            # 证据不足，保持原制约
            return current_constraint["name"], metrics
    else:
        return current_constraint["name"], metrics
```

---

## 4. 自动更新逻辑

### 4.1 更新触发条件
以下任一条件触发状态更新：

1. **定期触发**：心跳检查时
2. **事件触发**：TaskCard 状态变化
3. **手动触发**：俊阳或小青要求

### 4.2 更新流程
```python
def update_toc_state():
    # 1. 收集数据
    tasks = load_all_taskcards()
    logs = load_recent_logs(7)
    
    # 2. 计算指标
    queues = calculate_queue_lengths(tasks)
    wait_times = calculate_avg_wait_times(tasks)
    rework_rate = calculate_rework_rate(tasks, 7)
    interrupt_freq = calculate_interrupt_frequency(logs, 7)
    
    # 3. 识别主制约
    main_constraint, all_metrics = identify_main_constraint(
        queues, wait_times, rework_rate, interrupt_freq
    )
    
    # 4. 更新 ConstraintRecord
    constraint_record = load_constraint_record()
    
    constraint_record["evidence"] = {
        "queueLength": queues.get(main_constraint, 0),
        "avgWaitHours": wait_times.get(main_constraint, 0),
        "reworkRate": rework_rate,
        "interruptFrequencyPerDay": interrupt_freq
    }
    
    constraint_record["symptoms"] = generate_symptoms(
        queues, wait_times, rework_rate, interrupt_freq
    )
    
    # 5. 保存更新
    save_constraint_record(constraint_record)
    
    # 6. 记录更新日志
    log_state_update(constraint_record)
    
    return constraint_record
```

### 4.3 增量更新优化
为避免每次全量扫描，支持增量更新：

```python
def incremental_update(last_update_time):
    # 只处理 last_update_time 之后的变化
    changed_tasks = get_tasks_changed_since(last_update_time)
    
    if not changed_tasks:
        return  # 无变化，跳过
    
    # 增量更新指标
    for task in changed_tasks:
        update_metrics_for_task(task)
    
    # 检查是否影响主制约判断
    if affects_constraint_judgment(changed_tasks):
        # 需要重新计算主制约
        full_update()
    else:
        # 只更新证据数据
        update_evidence_only()
```

---

## 5. 数据存储设计

### 5.1 存储位置
- **TaskCard**：`tasks/` 目录下的 YAML 文件
- **ConstraintRecord**：`state/constraint-record.yaml`
- **系统日志**：`logs/toc-system.log`
- **指标快照**：`state/metrics-snapshots/`

### 5.2 存储格式
```yaml
# 指标快照示例
snapshot_id: metrics-2026-04-08T17:30:00
timestamp: 2026-04-08T17:30:00+08:00

queues:
  waiting_decision: 3
  verifying: 2
  blocked: 1
  executing: 2
  ready: 4

wait_times:
  waiting_decision: 8.5
  verifying: 4.2
  blocked: 12.1

rework_rate: 0.32
interrupt_frequency: 11

main_constraint: decision
constraint_score: 0.85

calculated_by: xiaoqing
```

### 5.3 历史数据保留
- 最近 7 天：完整数据
- 7-30 天：每日快照
- 30 天以上：每周快照

---

## 6. 实现建议

### 6.1 初期实现（手动 + 半自动）
1. 小青在心跳时手动执行检查
2. 使用简单脚本辅助计算
3. 人工确认主制约判断

### 6.2 中期实现（脚本自动化）
1. 创建 Python 脚本自动计算
2. 集成到心跳响应中
3. 自动更新 ConstraintRecord

### 6.3 长期实现（系统集成）
1. 与 OpenClaw 深度集成
2. 实时状态监控
3. 自动预警和调整

---

## 7. 错误处理与恢复

### 7.1 数据不一致处理
当检测到数据不一致时：

1. 记录不一致详情
2. 尝试自动修复
3. 如无法修复，使用最近有效快照
4. 报告需要人工检查

### 7.2 计算失败处理
当计算失败时：

1. 记录失败原因
2. 使用上次计算结果
3. 降低后续检查频率
4. 报告需要维护

### 7.3 存储失败处理
当无法保存时：

1. 尝试多次重试
2. 如仍失败，保存到临时位置
3. 下次启动时恢复

---

## 8. 监控与验证

### 8.1 监控指标
- 计算耗时
- 数据准确性
- 更新频率
- 错误率

### 8.2 验证方法
- 定期与人工判断对比
- 检查数据一致性
- 验证预测准确性

### 8.3 校准机制
当发现偏差时：

1. 分析偏差原因
2. 调整算法参数
3. 更新权重设置
4. 重新训练模型（如使用）

---

## 9. 一句话总结

**TOC 状态计算通过定期扫描 TaskCard、计算各环节指标、加权评分识别主制约，为系统提供数据驱动的决策依据。**

---

## 10. 下一步实现

1. 创建基础计算脚本
2. 集成到心跳机制
3. 建立数据存储结构
4. 测试计算准确性