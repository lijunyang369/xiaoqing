#!/usr/bin/env python3
"""
TOC 状态检查脚本
用于扫描 TaskCard、计算指标、更新 ConstraintRecord

使用方法：
1. 手动运行：python scripts/toc-state-check.py
2. 心跳集成：小青在心跳时调用此脚本或使用类似逻辑
3. 定时任务：配置 cron 定期执行

注意事项：
- 需要 Python 3.8+
- 需要 pyyaml 库（可自动安装）
"""

import os
import sys
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 配置路径
WORKSPACE_DIR = Path(__file__).parent.parent
TASKS_DIR = WORKSPACE_DIR / "tasks"  # TaskCard 存储目录（待创建）
TEMPLATES_DIR = WORKSPACE_DIR / "templates"
STATE_DIR = WORKSPACE_DIR / "state"
LOGS_DIR = WORKSPACE_DIR / "logs"

# 确保目录存在
for dir_path in [TASKS_DIR, STATE_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

class TOCStateCalculator:
    """TOC 状态计算器"""
    
    def __init__(self):
        self.now = datetime.now()
    
    def load_taskcards(self) -> List[Dict[str, Any]]:
        """加载所有 TaskCard
        
        注意：初期实现中，TaskCard 可能存储在不同位置。
        此函数需要根据实际存储方式调整。
        """
        tasks = []
        
        # 示例：从内存或特定目录加载
        # 这里返回空列表，实际实现需补充
        return tasks
    
    def calculate_queues(self, tasks: List[Dict[str, Any]]) -> Dict[str, int]:
        """计算各环节队列长度"""
        queues = {
            "waiting_decision": 0,
            "verifying": 0,
            "blocked": 0,
            "executing": 0,
            "ready": 0,
        }
        
        for task in tasks:
            status = task.get("status", "")
            if status in queues:
                queues[status] += 1
        
        return queues
    
    def calculate_avg_wait_times(self, tasks: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算平均等待时间（简化版）"""
        wait_times = {
            "waiting_decision": [],
            "verifying": [],
            "blocked": [],
        }
        
        for task in tasks:
            status = task.get("status", "")
            if status in wait_times:
                # 简化：使用 updatedAt 作为进入时间
                updated_at_str = task.get("updatedAt")
                if updated_at_str:
                    try:
                        updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                        hours = (self.now - updated_at).total_seconds() / 3600
                        wait_times[status].append(hours)
                    except (ValueError, TypeError):
                        pass
        
        avg_wait = {}
        for status, times in wait_times.items():
            if times:
                avg_wait[status] = sum(times) / len(times)
            else:
                avg_wait[status] = 0.0
        
        return avg_wait
    
    def calculate_rework_rate(self, tasks: List[Dict[str, Any]], days: int = 7) -> float:
        """计算返工率"""
        recent_tasks = [t for t in tasks if self.is_recent(t, days)]
        
        total_verified = 0
        total_reworked = 0
        
        for task in recent_tasks:
            if task.get("verifiedAt"):
                total_verified += 1
            
            if task.get("reworkCount", 0) > 0:
                total_reworked += 1
        
        if total_verified == 0:
            return 0.0
        
        return total_reworked / total_verified
    
    def is_recent(self, task: Dict[str, Any], days: int) -> bool:
        """判断任务是否在指定天数内更新"""
        updated_at_str = task.get("updatedAt")
        if not updated_at_str:
            return False
        
        try:
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
            return (self.now - updated_at).days <= days
        except (ValueError, TypeError):
            return False
    
    def load_current_constraint(self) -> Dict[str, Any]:
        """加载当前 ConstraintRecord"""
        constraint_path = STATE_DIR / "constraint-record.yaml"
        
        if constraint_path.exists():
            try:
                with open(constraint_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except (yaml.YAMLError, FileNotFoundError):
                pass
        
        # 返回默认结构
        return {
            "id": "C-000001",
            "name": "主链路决策吞吐",
            "scope": "小青 <-> 俊阳",
            "status": "Suspected",
            "evidence": {
                "queueLength": 0,
                "avgWaitHours": 0,
                "reworkRate": 0.0,
                "interruptFrequencyPerDay": 0
            }
        }
    
    def identify_main_constraint(self, queues: Dict[str, int], 
                                wait_times: Dict[str, float], 
                                rework_rate: float) -> str:
        """识别主制约（简化版）"""
        
        # 计算各环节分数（简化逻辑）
        scores = {}
        
        # 决策环节（waiting_decision）
        decision_score = (
            queues.get("waiting_decision", 0) * 0.4 +
            wait_times.get("waiting_decision", 0) * 0.3 +
            rework_rate * 100 * 0.2  # 放大返工率影响
        )
        scores["decision"] = decision_score
        
        # 验证环节（verifying）
        verification_score = (
            queues.get("verifying", 0) * 0.4 +
            wait_times.get("verifying", 0) * 0.3 +
            rework_rate * 100 * 0.3  # 返工率对验证环节影响更大
        )
        scores["verification"] = verification_score
        
        # 阻塞环节（blocked）
        blocked_score = (
            queues.get("blocked", 0) * 0.5 +
            wait_times.get("blocked", 0) * 0.5
        )
        scores["environment"] = blocked_score  # 假设阻塞主要由环境引起
        
        # 找出分数最高的环节
        main_stage = max(scores.items(), key=lambda x: x[1])
        
        # 映射到可读名称
        stage_map = {
            "decision": "主链路决策吞吐",
            "verification": "验证吞吐",
            "environment": "环境稳定性"
        }
        
        return stage_map.get(main_stage[0], "主链路决策吞吐")
    
    def generate_symptoms(self, queues: Dict[str, int], 
                         wait_times: Dict[str, float], 
                         rework_rate: float) -> List[str]:
        """生成症状描述"""
        symptoms = []
        
        if queues.get("waiting_decision", 0) >= 3:
            symptoms.append("等待决策的任务积压")
        
        if queues.get("verifying", 0) >= 2:
            symptoms.append("验证队列积压")
        
        if wait_times.get("waiting_decision", 0) >= 8:
            symptoms.append("决策等待时间过长")
        
        if rework_rate >= 0.3:
            symptoms.append("返工率较高")
        
        if not symptoms:
            symptoms.append("无明显症状，系统运行平稳")
        
        return symptoms
    
    def save_constraint_record(self, constraint: Dict[str, Any]):
        """保存 ConstraintRecord"""
        constraint_path = STATE_DIR / "constraint-record.yaml"
        
        # 确保有必要字段
        constraint.setdefault("updatedAt", self.now.isoformat())
        
        try:
            with open(constraint_path, 'w', encoding='utf-8') as f:
                yaml.dump(constraint, f, allow_unicode=True, default_flow_style=False)
            
            print(f"✅ 已保存 ConstraintRecord 到 {constraint_path}")
        except Exception as e:
            print(f"❌ 保存失败：{e}")
    
    def log_state_update(self, queues: Dict[str, int], 
                        wait_times: Dict[str, float], 
                        rework_rate: float,
                        main_constraint: str):
        """记录状态更新日志"""
        log_path = LOGS_DIR / f"toc-state-{self.now.strftime('%Y-%m-%d')}.log"
        
        log_entry = {
            "timestamp": self.now.isoformat(),
            "queues": queues,
            "wait_times": wait_times,
            "rework_rate": rework_rate,
            "main_constraint": main_constraint
        }
        
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"❌ 日志记录失败：{e}")
    
    def run(self):
        """执行完整状态计算"""
        print(f"🔍 TOC 状态检查开始 {self.now.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # 1. 加载数据
        tasks = self.load_taskcards()
        print(f"📋 加载到 {len(tasks)} 个 TaskCard")
        
        # 2. 计算指标
        queues = self.calculate_queues(tasks)
        print("📊 队列状态:")
        for stage, count in queues.items():
            if count > 0:
                print(f"  - {stage}: {count}")
        
        wait_times = self.calculate_avg_wait_times(tasks)
        if any(wait_times.values()):
            print("⏱️  平均等待时间:")
            for stage, hours in wait_times.items():
                if hours > 0:
                    print(f"  - {stage}: {hours:.1f} 小时")
        
        rework_rate = self.calculate_rework_rate(tasks, 7)
        print(f"🔄 返工率: {rework_rate:.2%}")
        
        # 3. 识别主制约
        main_constraint = self.identify_main_constraint(queues, wait_times, rework_rate)
        print(f"🎯 识别到主制约: {main_constraint}")
        
        # 4. 更新 ConstraintRecord
        current_constraint = self.load_current_constraint()
        
        # 判断是否需要更新
        if current_constraint.get("name") != main_constraint:
            print(f"🔄 主制约变化: {current_constraint.get('name', '无')} -> {main_constraint}")
            current_constraint["status"] = "Reassessing"
        
        # 更新证据
        current_constraint["evidence"] = {
            "queueLength": queues.get("waiting_decision", 0),
            "avgWaitHours": wait_times.get("waiting_decision", 0),
            "reworkRate": rework_rate,
            "interruptFrequencyPerDay": 0  # 简化版暂不计算
        }
        
        current_constraint["symptoms"] = self.generate_symptoms(queues, wait_times, rework_rate)
        current_constraint["updatedAt"] = self.now.isoformat()
        
        # 5. 保存和记录
        self.save_constraint_record(current_constraint)
        self.log_state_update(queues, wait_times, rework_rate, main_constraint)
        
        print("-" * 50)
        print("✅ TOC 状态检查完成")
        
        # 返回摘要
        return {
            "queues": queues,
            "wait_times": wait_times,
            "rework_rate": rework_rate,
            "main_constraint": main_constraint,
            "constraint_updated": current_constraint
        }

def main():
    """主函数"""
    try:
        calculator = TOCStateCalculator()
        result = calculator.run()
        
        # 输出建议
        print("\n💡 建议:")
        
        queues = result["queues"]
        main_constraint = result["main_constraint"]
        
        if queues.get("waiting_decision", 0) >= 3:
            print("- WaitingDecision 队列 ≥ 3，建议暂停释放新任务")
        
        if queues.get("verifying", 0) >= 2:
            print("- Verifying 队列 ≥ 2，建议优先清验证库存")
        
        if main_constraint == "主链路决策吞吐":
            print("- 当前主制约为决策吞吐，建议聚合决策事项、减少碎片打扰")
        elif main_constraint == "验证吞吐":
            print("- 当前主制约为验证吞吐，建议提前验证介入、缩短验证等待")
        elif main_constraint == "环境稳定性":
            print("- 当前主制约为环境稳定性，建议优先处理环境阻塞")
        
        # 退出码
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ 检查失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()