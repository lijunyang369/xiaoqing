#!/usr/bin/env python3
"""
TOC 轻量检查脚本
用于心跳时快速扫描 TaskCard，检查 WIP 超限，决定是否触发完整检查

设计原则：
- 极快执行：< 5 秒
- 最小依赖：只使用标准库
- 简单输出：JSON 格式，便于小青解析
- 触发决策：明确是否需触发 toc-monitor 子进程

使用方法：
1. 心跳时调用：python scripts/toc-quick-check.py
2. 返回 JSON：包含队列状态和触发建议
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 配置路径
WORKSPACE_DIR = Path(__file__).parent.parent
TASKS_DIR = WORKSPACE_DIR / "tasks"
STATE_DIR = WORKSPACE_DIR / "state"

# WIP 限制
WIP_LIMITS = {
    "executing": 3,
    "waiting_decision": 2,
    "verifying": 2,
}

# 异常阈值
THRESHOLDS = {
    "queue_growth": 3,  # 单环节队列超过此值视为异常
    "multi_queue": 2,   # 多个环节队列同时有值可能有问题
}

class TOCQuickChecker:
    """TOC 轻量检查器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.now = datetime.now()
        self.results = {
            "timestamp": self.now.isoformat(),
            "check_type": "quick",
            "execution_time_ms": 0,
            "tasks_scanned": 0,
            "queues": {},
            "wip_status": {},
            "anomalies": [],
            "trigger_suggestion": "none",  # none, full_check, immediate_action
            "trigger_reason": "",
            "summary": ""
        }
    
    def log(self, message: str):
        """输出日志"""
        if self.verbose:
            print(f"  {message}")
    
    def load_taskcards_quick(self) -> List[Dict[str, Any]]:
        """快速加载 TaskCard（仅读取必要字段）"""
        start_time = datetime.now()
        tasks = []
        
        if not TASKS_DIR.exists():
            self.log(f"目录不存在: {TASKS_DIR}")
            return tasks
        
        task_files = list(TASKS_DIR.glob("*.yaml")) + list(TASKS_DIR.glob("*.yml"))
        
        for task_file in task_files[:50]:  # 限制文件数，防止过多
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    # 只读取前几行获取关键字段
                    content = f.read(2048)  # 只读2KB，通常足够
                    task = yaml.safe_load(content)
                    if task and isinstance(task, dict):
                        # 只保留必要字段
                        essential = {
                            "id": task.get("id", ""),
                            "status": task.get("status", ""),
                            "updatedAt": task.get("updatedAt"),
                            "reworkCount": task.get("reworkCount", 0),
                        }
                        tasks.append(essential)
            except (yaml.YAMLError, FileNotFoundError, UnicodeDecodeError):
                continue  # 跳过有问题的文件
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        self.log(f"快速加载 {len(tasks)} 个TaskCard，耗时 {elapsed:.0f}ms")
        
        return tasks
    
    def calculate_queues(self, tasks: List[Dict[str, Any]]) -> Dict[str, int]:
        """计算队列长度"""
        queues = {
            "waiting_decision": 0,
            "verifying": 0,
            "blocked": 0,
            "executing": 0,
            "ready": 0,
            "done": 0,
            "captured": 0,
            "clarified": 0,
            "rework": 0,
        }
        
        status_count = {}
        
        for task in tasks:
            status = task.get("status", "")
            if status:
                queues[status] = queues.get(status, 0) + 1
                status_count[status] = status_count.get(status, 0) + 1
        
        # 只保留有值的队列
        queues = {k: v for k, v in queues.items() if v > 0}
        
        self.results["tasks_scanned"] = len(tasks)
        self.results["queues"] = queues
        self.results["status_distribution"] = status_count
        
        return queues
    
    def check_wip_limits(self, queues: Dict[str, int]) -> Dict[str, Dict]:
        """检查 WIP 限制"""
        wip_status = {}
        
        for queue, limit in WIP_LIMITS.items():
            count = queues.get(queue, 0)
            within_limit = count <= limit
            wip_status[queue] = {
                "count": count,
                "limit": limit,
                "within_limit": within_limit,
                "exceeded_by": max(0, count - limit) if not within_limit else 0
            }
            
            if not within_limit:
                self.results["anomalies"].append({
                    "type": "wip_exceeded",
                    "queue": queue,
                    "count": count,
                    "limit": limit,
                    "message": f"{queue} 队列超限: {count} > {limit}"
                })
        
        self.results["wip_status"] = wip_status
        return wip_status
    
    def detect_anomalies(self, queues: Dict[str, int], wip_status: Dict[str, Dict]):
        """检测异常模式"""
        
        # 1. 单个队列异常增长
        for queue, count in queues.items():
            if count >= THRESHOLDS["queue_growth"]:
                if queue not in WIP_LIMITS or count > WIP_LIMITS[queue]:
                    # 已由 WIP 检查处理
                    continue
                self.results["anomalies"].append({
                    "type": "queue_growth",
                    "queue": queue,
                    "count": count,
                    "threshold": THRESHOLDS["queue_growth"],
                    "message": f"{queue} 队列增长到 {count}，接近阈值"
                })
        
        # 2. 多环节同时有队列（可能系统压力大）
        active_queues = [q for q in ["waiting_decision", "verifying", "blocked"] if queues.get(q, 0) > 0]
        if len(active_queues) >= THRESHOLDS["multi_queue"]:
            self.results["anomalies"].append({
                "type": "multi_queue_active",
                "queues": active_queues,
                "count": len(active_queues),
                "threshold": THRESHOLDS["multi_queue"],
                "message": f"多个环节有队列: {', '.join(active_queues)}"
            })
        
        # 3. 检查是否有长时间未更新的任务（简化版）
        # 在实际实现中需要检查时间戳，这里先跳过
        
        return len(self.results["anomalies"]) > 0
    
    def make_trigger_decision(self, queues: Dict[str, int], 
                            wip_status: Dict[str, Dict],
                            has_anomalies: bool) -> None:
        """做出触发决策"""
        
        # 检查是否到达预定时间（由小青在心跳时判断）
        # 这里只基于数据异常做决策
        
        immediate_action = False
        trigger_full_check = False
        
        # 需要立即行动的情况
        for queue, status in wip_status.items():
            if not status["within_limit"] and status["exceeded_by"] > 0:
                immediate_action = True
                self.results["trigger_suggestion"] = "immediate_action"
                self.results["trigger_reason"] = f"{queue} 队列超限 {status['count']} > {status['limit']}"
                self.results["summary"] = f"⚠️ {queue} 队列超限，需要立即处理"
                return
        
        # 需要完整检查的情况
        if has_anomalies:
            trigger_full_check = True
            anomaly_types = [a["type"] for a in self.results["anomalies"]]
            self.results["trigger_suggestion"] = "full_check"
            self.results["trigger_reason"] = f"检测到异常: {', '.join(anomaly_types[:3])}"
            self.results["summary"] = "🔍 检测到系统异常，建议触发完整检查"
            return
        
        # 系统正常
        self.results["trigger_suggestion"] = "none"
        self.results["trigger_reason"] = "系统运行正常，无异常检测"
        self.results["summary"] = "✅ 系统运行正常，WIP 未超限"
    
    def generate_human_summary(self) -> str:
        """生成人类可读摘要"""
        queues = self.results["queues"]
        wip_status = self.results["wip_status"]
        trigger = self.results["trigger_suggestion"]
        
        lines = []
        lines.append(f"## TOC 轻量检查 {self.now.strftime('%H:%M')}")
        lines.append("")
        
        if queues:
            lines.append("📊 队列状态:")
            for queue, count in sorted(queues.items()):
                limit_info = ""
                if queue in wip_status:
                    status = wip_status[queue]
                    limit_info = f" (上限:{status['limit']})" if status['limit'] > 0 else ""
                    if not status["within_limit"]:
                        limit_info += " ⚠️超限"
                lines.append(f"  - {queue}: {count}{limit_info}")
        else:
            lines.append("📊 队列状态: 无活跃任务")
        
        lines.append("")
        
        if self.results["anomalies"]:
            lines.append("⚠️ 异常检测:")
            for anomaly in self.results["anomalies"][:3]:  # 最多显示3个
                lines.append(f"  - {anomaly['message']}")
            lines.append("")
        
        lines.append(f"🎯 触发建议: {self.results['trigger_suggestion']}")
        lines.append(f"📝 原因: {self.results['trigger_reason']}")
        
        execution_time = self.results.get("execution_time_ms", 0)
        lines.append(f"⏱️  执行时间: {execution_time:.0f}ms")
        
        return "\n".join(lines)
    
    def run(self) -> Dict[str, Any]:
        """执行完整检查"""
        start_time = datetime.now()
        
        try:
            # 1. 快速加载数据
            tasks = self.load_taskcards_quick()
            
            # 2. 计算队列
            queues = self.calculate_queues(tasks)
            
            # 3. 检查 WIP 限制
            wip_status = self.check_wip_limits(queues)
            
            # 4. 检测异常
            has_anomalies = self.detect_anomalies(queues, wip_status)
            
            # 5. 做出触发决策
            self.make_trigger_decision(queues, wip_status, has_anomalies)
            
            # 6. 生成摘要
            human_summary = self.generate_human_summary()
            self.results["human_summary"] = human_summary
            
            # 计算执行时间
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            self.results["execution_time_ms"] = elapsed
            
            if self.verbose:
                print(human_summary)
            
            return self.results
            
        except Exception as e:
            self.results["error"] = str(e)
            self.results["trigger_suggestion"] = "full_check"
            self.results["trigger_reason"] = f"轻量检查出错: {e}"
            self.results["summary"] = "❌ 轻量检查失败，建议触发完整检查"
            return self.results

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TOC 轻量检查脚本")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--json", "-j", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()
    
    try:
        checker = TOCQuickChecker(verbose=args.verbose or not args.json)
        results = checker.run()
        
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            if not args.verbose:
                print(results["human_summary"])
        
        # 根据触发建议设置退出码
        if results["trigger_suggestion"] == "immediate_action":
            sys.exit(2)  # 需要立即行动
        elif results["trigger_suggestion"] == "full_check":
            sys.exit(1)  # 建议完整检查
        else:
            sys.exit(0)  # 正常
        
    except Exception as e:
        print(f"❌ 检查失败: {e}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()