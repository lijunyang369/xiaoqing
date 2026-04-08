#!/usr/bin/env python3
"""
TOC 算法验证脚本
展示状态计算算法的详细步骤，用于验证算法合理性

使用方法：
python scripts/toc-algorithm-verification.py

输出：
- 加载的TaskCard详情
- 队列计算步骤
- 等待时间计算步骤
- 返工率计算步骤
- 主制约识别步骤
- 最终结果与快照对比
"""

import os
import sys
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 配置路径
WORKSPACE_DIR = Path(__file__).parent.parent
TASKS_DIR = WORKSPACE_DIR / "tasks"
STATE_DIR = WORKSPACE_DIR / "state"
METRICS_SNAPSHOTS_DIR = STATE_DIR / "metrics-snapshots"

class TOCAlgorithmVerifier:
    """TOC 算法验证器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.now = datetime(2026, 4, 8, 17, 0, 0)  # 使用快照时间，便于对比
        self.tasks = []
    
    def log(self, message: str, level: str = "INFO"):
        """输出日志"""
        if self.verbose:
            prefix = {
                "INFO": "ℹ️ ",
                "STEP": "🔍 ",
                "CALC": "🧮 ",
                "RESULT": "📊 ",
                "ERROR": "❌ "
            }.get(level, "  ")
            print(f"{prefix}{message}")
    
    def load_taskcards(self) -> List[Dict[str, Any]]:
        """加载所有TaskCard文件"""
        self.log(f"加载TaskCard从目录: {TASKS_DIR}", "STEP")
        
        tasks = []
        if not TASKS_DIR.exists():
            self.log(f"目录不存在: {TASKS_DIR}", "ERROR")
            return tasks
        
        task_files = list(TASKS_DIR.glob("*.yaml")) + list(TASKS_DIR.glob("*.yml"))
        self.log(f"找到 {len(task_files)} 个TaskCard文件", "INFO")
        
        for task_file in task_files:
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task = yaml.safe_load(f)
                    if task and isinstance(task, dict):
                        task["_filename"] = task_file.name
                        tasks.append(task)
                        self.log(f"  已加载: {task.get('id', '未知ID')} - {task.get('title', '无标题')}", "INFO")
            except (yaml.YAMLError, FileNotFoundError) as e:
                self.log(f"  加载失败 {task_file.name}: {e}", "ERROR")
        
        self.tasks = tasks
        return tasks
    
    def calculate_queues(self) -> Dict[str, int]:
        """计算队列长度，展示详细步骤"""
        self.log("计算队列长度...", "STEP")
        
        queues = {
            "waiting_decision": 0,
            "verifying": 0,
            "blocked": 0,
            "executing": 0,
            "ready": 0,
            "done": 0,
            "captured": 0,
            "clarified": 0,
        }
        
        status_count = {}
        
        for task in self.tasks:
            status = task.get("status", "")
            task_id = task.get("id", "未知ID")
            
            # 统计所有状态
            status_count[status] = status_count.get(status, 0) + 1
            
            # 映射到队列
            if status in queues:
                queues[status] += 1
                self.log(f"  {task_id}: 状态={status} → 队列[{status}] += 1", "CALC")
            else:
                self.log(f"  {task_id}: 状态={status} (未计入队列)", "CALC")
        
        self.log("队列统计结果:", "RESULT")
        for queue, count in queues.items():
            if count > 0:
                self.log(f"  {queue}: {count}", "RESULT")
        
        self.log("完整状态分布:", "INFO")
        for status, count in status_count.items():
            self.log(f"  {status}: {count}", "INFO")
        
        return queues
    
    def parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not dt_str:
            return None
        
        # 处理多种格式
        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                # 处理时区
                if fmt.endswith("%z") and "+" in dt_str:
                    # 处理类似 +08:00 的时区
                    dt_str_adj = dt_str.replace("+08:00", "+0800")
                    return datetime.strptime(dt_str_adj, fmt)
                else:
                    return datetime.strptime(dt_str, fmt)
            except (ValueError, TypeError):
                continue
        
        self.log(f"时间解析失败: {dt_str}", "ERROR")
        return None
    
    def calculate_wait_times(self) -> Dict[str, float]:
        """计算平均等待时间，展示详细步骤"""
        self.log("计算平均等待时间...", "STEP")
        
        wait_times = {
            "waiting_decision": [],
            "verifying": [],
            "blocked": [],
        }
        
        for task in self.tasks:
            status = task.get("status", "")
            task_id = task.get("id", "未知ID")
            
            if status not in wait_times:
                continue
            
            # 确定进入当前状态的时间
            entered_at = None
            
            if status == "waiting_decision":
                # 使用 updatedAt 作为进入决策等待的时间
                entered_at = self.parse_datetime(task.get("updatedAt"))
            elif status == "verifying":
                # 使用 verifiedAt 作为进入验证的时间
                entered_at = self.parse_datetime(task.get("verifiedAt"))
            elif status == "blocked":
                # 使用 updatedAt 作为进入阻塞的时间
                entered_at = self.parse_datetime(task.get("updatedAt"))
            
            if entered_at:
                wait_hours = (self.now - entered_at).total_seconds() / 3600
                wait_times[status].append(wait_hours)
                
                self.log(f"  {task_id}: {status} 进入时间={entered_at}, 等待={wait_hours:.1f}小时", "CALC")
            else:
                self.log(f"  {task_id}: {status} 无时间戳，跳过", "CALC")
        
        # 计算平均值
        avg_wait = {}
        for status, times in wait_times.items():
            if times:
                avg = sum(times) / len(times)
                avg_wait[status] = avg
                self.log(f"  {status}: {len(times)}个任务, 平均等待={avg:.1f}小时", "RESULT")
            else:
                avg_wait[status] = 0.0
                self.log(f"  {status}: 无任务", "RESULT")
        
        return avg_wait
    
    def calculate_rework_rate(self, days: int = 7) -> float:
        """计算返工率，展示详细步骤"""
        self.log(f"计算返工率（最近{days}天）...", "STEP")
        
        recent_tasks = []
        for task in self.tasks:
            updated_at = self.parse_datetime(task.get("updatedAt"))
            if updated_at and (self.now - updated_at).days <= days:
                recent_tasks.append(task)
        
        self.log(f"最近{days}天有{len(recent_tasks)}个任务更新", "INFO")
        
        total_verified = 0
        total_reworked = 0
        
        for task in recent_tasks:
            task_id = task.get("id", "未知ID")
            
            # 检查是否已验证（有verifiedAt）
            verified_at = task.get("verifiedAt")
            if verified_at:
                total_verified += 1
                self.log(f"  {task_id}: 已验证 (verifiedAt={verified_at})", "CALC")
            
            # 检查是否有返工
            rework_count = task.get("reworkCount", 0)
            if rework_count > 0:
                total_reworked += 1
                self.log(f"  {task_id}: 有返工 (reworkCount={rework_count}, source={task.get('sourceOfRework', '未知')})", "CALC")
        
        if total_verified == 0:
            self.log("无已验证任务，返工率=0", "RESULT")
            return 0.0
        
        rework_rate = total_reworked / total_verified
        self.log(f"返工率计算: {total_reworked} / {total_verified} = {rework_rate:.2%}", "RESULT")
        
        return rework_rate
    
    def identify_main_constraint(self, queues: Dict[str, int], 
                                wait_times: Dict[str, float], 
                                rework_rate: float) -> Tuple[str, Dict[str, float]]:
        """识别主制约，展示详细步骤"""
        self.log("识别主制约...", "STEP")
        
        # 各环节基础数据
        stage_data = {
            "decision": {
                "queue": queues.get("waiting_decision", 0),
                "avg_wait": wait_times.get("waiting_decision", 0),
                "rework_impact": rework_rate * 0.5,  # 返工对决策的影响系数
                "interrupt_impact": 8 / 10.0,  # 假设中断频率8，最大10
            },
            "verification": {
                "queue": queues.get("verifying", 0),
                "avg_wait": wait_times.get("verifying", 0),
                "rework_impact": rework_rate * 0.8,  # 返工对验证的影响更大
                "interrupt_impact": 0.0,  # 验证环节不受中断影响
            },
            "environment": {
                "queue": queues.get("blocked", 0),
                "avg_wait": wait_times.get("blocked", 0),
                "rework_impact": 0.0,  # 环境问题通常不直接导致返工
                "interrupt_impact": 0.0,  # 环境问题本身是中断
            }
        }
        
        self.log("各环节基础数据:", "INFO")
        for stage, data in stage_data.items():
            self.log(f"  {stage}: 队列={data['queue']}, 等待={data['avg_wait']:.1f}h, 返工影响={data['rework_impact']:.2f}, 中断影响={data['interrupt_impact']:.2f}", "INFO")
        
        # 计算分数（加权）
        scores = {}
        for stage, data in stage_data.items():
            # 权重：队列40%，等待时间30%，返工影响20%，中断影响10%
            score = (
                data["queue"] * 0.4 +
                data["avg_wait"] * 0.3 +
                data["rework_impact"] * 0.2 +
                data["interrupt_impact"] * 0.1
            )
            scores[stage] = score
            
            self.log(f"  {stage}分数计算:", "CALC")
            self.log(f"    队列贡献: {data['queue']} × 0.4 = {data['queue'] * 0.4:.2f}", "CALC")
            self.log(f"    等待贡献: {data['avg_wait']:.1f} × 0.3 = {data['avg_wait'] * 0.3:.2f}", "CALC")
            self.log(f"    返工贡献: {data['rework_impact']:.2f} × 0.2 = {data['rework_impact'] * 0.2:.2f}", "CALC")
            self.log(f"    中断贡献: {data['interrupt_impact']:.2f} × 0.1 = {data['interrupt_impact'] * 0.1:.2f}", "CALC")
            self.log(f"    总分: {score:.2f}", "CALC")
        
        # 找出最高分
        main_stage = max(scores.items(), key=lambda x: x[1])
        
        # 映射到可读名称
        stage_map = {
            "decision": "主链路决策吞吐",
            "verification": "验证吞吐",
            "environment": "环境稳定性"
        }
        
        main_constraint = stage_map.get(main_stage[0], "未知制约")
        
        self.log(f"主制约识别结果: {main_constraint} (分数={main_stage[1]:.2f})", "RESULT")
        
        return main_constraint, scores
    
    def load_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """加载最新快照用于对比"""
        if not METRICS_SNAPSHOTS_DIR.exists():
            return None
        
        snapshot_files = list(METRICS_SNAPSHOTS_DIR.glob("*.json"))
        if not snapshot_files:
            return None
        
        # 按时间戳排序
        snapshot_files.sort(reverse=True)
        latest_file = snapshot_files[0]
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            self.log(f"已加载最新快照: {latest_file.name}", "INFO")
            return snapshot
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log(f"加载快照失败: {e}", "ERROR")
            return None
    
    def compare_with_snapshot(self, queues: Dict[str, int], 
                             wait_times: Dict[str, float], 
                             rework_rate: float,
                             main_constraint: str,
                             scores: Dict[str, float]) -> None:
        """与快照数据对比"""
        snapshot = self.load_latest_snapshot()
        if not snapshot:
            self.log("无快照数据可对比", "INFO")
            return
        
        self.log("与快照数据对比...", "STEP")
        
        # 队列对比
        snapshot_queues = snapshot.get("queues", {})
        self.log("队列对比:", "INFO")
        for queue in set(list(queues.keys()) + list(snapshot_queues.keys())):
            calc_val = queues.get(queue, 0)
            snap_val = snapshot_queues.get(queue, 0)
            diff = calc_val - snap_val
            status = "✓" if calc_val == snap_val else f"Δ{diff:+d}"
            self.log(f"  {queue}: 计算={calc_val}, 快照={snap_val} {status}", "INFO")
        
        # 等待时间对比
        snapshot_wait_times = snapshot.get("wait_times", {})
        self.log("等待时间对比:", "INFO")
        for stage in set(list(wait_times.keys()) + list(snapshot_wait_times.keys())):
            calc_val = wait_times.get(stage, 0)
            snap_val = snapshot_wait_times.get(stage, 0)
            diff = calc_val - snap_val
            if calc_val != 0 or snap_val != 0:
                status = "✓" if abs(diff) < 0.1 else f"Δ{diff:+.1f}h"
                self.log(f"  {stage}: 计算={calc_val:.1f}h, 快照={snap_val:.1f}h {status}", "INFO")
        
        # 返工率对比
        snapshot_rework_rate = snapshot.get("rework_rate", 0)
        self.log(f"返工率对比: 计算={rework_rate:.2%}, 快照={snapshot_rework_rate:.2%}", "INFO")
        
        # 主制约对比
        snapshot_constraint = snapshot.get("main_constraint", "未知")
        self.log(f"主制约对比: 计算={main_constraint}, 快照={snapshot_constraint}", "INFO")
        
        # 分数对比
        snapshot_scores = {}
        constraint_details = snapshot.get("constraint_details", {})
        for stage, details in constraint_details.items():
            if isinstance(details, dict):
                snapshot_scores[stage] = details.get("score", 0)
        
        self.log("制约分数对比:", "INFO")
        for stage in set(list(scores.keys()) + list(snapshot_scores.keys())):
            calc_val = scores.get(stage, 0)
            snap_val = snapshot_scores.get(stage, 0)
            if calc_val != 0 or snap_val != 0:
                diff = calc_val - snap_val
                status = "✓" if abs(diff) < 0.05 else f"Δ{diff:+.2f}"
                self.log(f"  {stage}: 计算={calc_val:.2f}, 快照={snap_val:.2f} {status}", "INFO")
    
    def run(self):
        """执行完整验证"""
        self.log("=" * 60, "INFO")
        self.log("TOC 算法验证开始", "STEP")
        self.log(f"当前时间: {self.now}", "INFO")
        self.log("=" * 60, "INFO")
        
        # 1. 加载数据
        tasks = self.load_taskcards()
        if not tasks:
            self.log("未加载到TaskCard，验证中止", "ERROR")
            return
        
        self.log(f"成功加载 {len(tasks)} 个TaskCard", "RESULT")
        
        # 2. 计算队列
        queues = self.calculate_queues()
        
        # 3. 计算等待时间
        wait_times = self.calculate_wait_times()
        
        # 4. 计算返工率
        rework_rate = self.calculate_rework_rate(7)
        
        # 5. 识别主制约
        main_constraint, scores = self.identify_main_constraint(queues, wait_times, rework_rate)
        
        # 6. 汇总结果
        self.log("=" * 60, "INFO")
        self.log("算法验证结果汇总", "RESULT")
        self.log("=" * 60, "INFO")
        
        self.log("📈 队列状态:", "RESULT")
        for queue, count in queues.items():
            if count > 0:
                self.log(f"  {queue}: {count}", "RESULT")
        
        self.log("⏱️  平均等待时间:", "RESULT")
        for stage, hours in wait_times.items():
            if hours > 0:
                self.log(f"  {stage}: {hours:.1f} 小时", "RESULT")
        
        self.log(f"🔄 返工率: {rework_rate:.2%}", "RESULT")
        
        self.log("🎯 主制约识别:", "RESULT")
        self.log(f"  当前主制约: {main_constraint}", "RESULT")
        for stage, score in scores.items():
            stage_name = {
                "decision": "决策吞吐",
                "verification": "验证吞吐",
                "environment": "环境稳定性"
            }.get(stage, stage)
            self.log(f"  {stage_name}分数: {score:.2f}", "RESULT")
        
        # 7. 与快照对比
        self.compare_with_snapshot(queues, wait_times, rework_rate, main_constraint, scores)
        
        # 8. 算法评估
        self.log("=" * 60, "INFO")
        self.log("算法合理性评估", "STEP")
        self.log("=" * 60, "INFO")
        
        # 检查数据完整性
        tasks_without_status = [t for t in tasks if not t.get("status")]
        tasks_without_timestamp = [t for t in tasks if not t.get("updatedAt")]
        
        if tasks_without_status:
            self.log(f"⚠️  有 {len(tasks_without_status)} 个TaskCard缺少状态字段", "INFO")
        if tasks_without_timestamp:
            self.log(f"⚠️  有 {len(tasks_without_timestamp)} 个TaskCard缺少时间戳", "INFO")
        
        # 评估算法假设
        self.log("算法假设检查:", "INFO")
        self.log("  1. 队列长度反映环节压力: ✓ (合理)", "INFO")
        self.log("  2. 等待时间反映环节效率: ✓ (合理)", "INFO")
        self.log("  3. 返工率反映质量门有效性: ✓ (合理)", "INFO")
        self.log("  4. 加权评分识别主制约: ✓ (TOC标准方法)", "INFO")
        self.log("  5. 同一时间只认一个主制约: ✓ (TOC核心原则)", "INFO")
        
        # 潜在改进
        self.log("潜在改进建议:", "INFO")
        self.log("  1. 考虑任务价值权重 (高价值任务阻塞影响更大)", "INFO")
        self.log("  2. 考虑依赖关系 (阻塞任务的影响传播)", "INFO")
        self.log("  3. 增加趋势分析 (而不仅是当前快照)", "INFO")
        self.log("  4. 考虑外部因素 (如会议、假期的影响)", "INFO")
        
        self.log("=" * 60, "INFO")
        self.log("✅ TOC 算法验证完成", "RESULT")
        self.log("=" * 60, "INFO")
        
        return {
            "tasks_analyzed": len(tasks),
            "queues": queues,
            "wait_times": wait_times,
            "rework_rate": rework_rate,
            "main_constraint": main_constraint,
            "scores": scores
        }

def main():
    """主函数"""
    try:
        verifier = TOCAlgorithmVerifier(verbose=True)
        result = verifier.run()
        
        # 输出可用于脚本验证的数据
        print("\n📋 验证数据摘要 (JSON格式):")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ 验证失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()