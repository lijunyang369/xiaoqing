# BOOT.md

## 1. 设计目标

Gateway 重启后，boot 阶段需要检查中断任务，并按统一模板输出任务恢复说明和当前未完成任务。

## 2. 执行顺序

1. 确认 Gateway 已就绪
2. 执行 `~/.openclaw/workspace/scripts/recover-interrupted.sh`
3. 输出 boot 回复

## 3. boot 回复规则

boot 检查完成后，直接按 `templates/boot-recovery-reply-template.md` 回复，不追加任何其它内容。
