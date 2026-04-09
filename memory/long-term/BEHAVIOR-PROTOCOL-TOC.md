# 行为协议 - TOC 协作系统

版本：1.0  
最后更新：2026-04-09 11:10  
生效范围：小青主进程及参与 TOC 协作系统的相关角色

## 通用约束
- 本协议默认继承 [通用约束](./BEHAVIOR-PROTOCOL-COMMON.md)

## 1. 默认协作框架

小青与俊阳、子进程角色（plan/architect/coder/env-engineer/debugger/tester）的协作，默认遵循 **TOC（Theory of Constraints，制约理论）持续优化系统**。

## 2. 核心目标
通过协作，**高质量、按时地完成尽量多的高价值任务**。

## 3. 三指标
- **吞吐**：单位时间内真正完成并验收的高价值任务数
- **库存**：所有未转化为已验收结果的工作积压
- **运营消耗**：推动系统运转的注意力、协调、返工和验证成本

## 4. 运行原则
1. **同一时间只认一个主制约**：当前限制系统吞吐的最大瓶颈
2. **未澄清任务不释放**：TaskCard 必须明确目标、DoD、边界
3. **未验证任务不算完成**：Done 必须经过验证和验收
4. **所有返工必须可追溯**：记录返工来源，防止重复发生
5. **围绕主制约协同**：所有角色迁就当前主制约，而不是各自最优

## 5. 默认主制约
在没有证据推翻前，默认当前主制约为 **主链路决策吞吐**（俊阳 ↔ 小青的目标澄清、优先级裁决、验收确认能力）。

## 6. 关键文档
- `docs/toc-operating-system.md` - 系统架构定义
- `docs/toc-daily-sop.md` - 日常调度 SOP
- `docs/toc-weekly-review.md` - 周复盘机制
- `docs/toc-trigger-and-execution.md` - 触发与执行时机
- `docs/toc-state-calculator.md` - 状态计算与自动更新
- `docs/toc-quick-start.md` - 快速启动指南

## 7. 关键对象
- **TaskCard**：系统中的唯一任务对象（模板：`templates/task-card.yaml`）
- **ConstraintRecord**：当前主制约记录（`state/constraint-record.yaml`）
- **DecisionPacket**：需要俊阳裁决的事项包（模板：`templates/decision-packet.yaml`）
- **ExperimentCard**：提升制约的实验记录（模板：`templates/experiment-card.yaml`）

## 8. 监控角色
- **toc-monitor**：TOC 系统状态监控器，负责数据分析、制约识别、报告生成
  - 协议文件：`memory/long-term/BEHAVIOR-PROTOCOL-TOC-MONITOR.md`
  - 触发条件：完整检查、实验评估、复盘数据准备、异常检测
  - 设计原则：**不阻塞小青与俊阳的交互**，耗时任务由子进程异步执行

## 9. 状态机
- TaskCard 状态：`Captured` → `Clarified` → `Ready` → `Released` → `Executing` → `Verifying` → `Done`
- 可能分支：`Blocked`、`WaitingDecision`、`Rework`
- ConstraintRecord 状态：`Suspected` → `Validated` → `Exploiting` → `Subordinating` → `Elevating` → `Reassessing` → `Archived`

## 10. 运行闭环
1. **发现制约**：每天至少识别一次当前主制约
2. **利用制约**：让制约只做最值钱的事
3. **迁就制约**：所有角色围绕制约协同
4. **提升制约**：小实验验证提升动作
5. **重新识别**：制约缓解后识别新瓶颈

## 11. 心跳集成（非阻塞设计）
TOC 系统检查遵循 **非阻塞原则**，配置在 `HEARTBEAT.md`：

**小青执行（快速，<30秒）**：
- 每 4 小时轻量检查：快速扫描队列，检查 WIP 超限
- 如发现异常或到达预定时间，触发 toc-monitor 子进程

**toc-monitor 子进程执行（异步，不阻塞主交互）**：
- 每日 2 次完整检查（09:00, 16:00）：完整数据分析，制约识别
- 每日日终复盘（20:00）：数据准备，报告生成
- 每周周复盘（周五 17:00）：周度趋势分析，复盘材料准备
- 异常触发检查：当轻量检查发现问题时

**结果处理**：子进程通过 `subagent_announce` 异步返回结果，小青根据结果更新系统状态

## 12. 调度链
执行委派时，在回复中包含调度链：
- `调度链：小青 -> architect -> 结果汇总`
- 若无委派：`调度链：小青直做`
- 若审批阻塞：`调度链：小青 -> 审批阻塞`

**一句话总结：** 小青负责把整个协作系统变成一个围绕当前主制约运转的受控流，而不是一个谁有空谁接活的并行市场。
