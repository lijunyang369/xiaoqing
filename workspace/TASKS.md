# TASKS.md

最后更新：2026-03-19

## 进行中

### 1) GitHub 云端同步打通
- 状态：进行中
- 目标：将 `C:\Users\wei\.openclaw` 根仓库成功推送到 `git@github.com:lijunyang369/xiaoqing.git`
- 已完成：
  - 根仓库已迁到 `C:\Users\wei\.openclaw`
  - remote 已配置为 GitHub 仓库
- 当前阻塞：
  - SSH 鉴权失败：`Permission denied (publickey)`
- 下一步：
  - 打通本机 GitHub SSH key 或改走 HTTPS/token

### 2) browser-ops / 青览打通 GitHub 浏览器配置
- 状态：进行中
- 目标：通过专职浏览器 agent 完成 GitHub 相关网页配置
- 已完成：
  - `browser-ops` agent 已创建
  - 已加载到 gateway
- 当前阻塞：
  - 尚未确认当前环境是否把可实操的 browser 工具面暴露给 agent
- 下一步：
  - 验证 browser 工具面可用性，再进入 GitHub 页面配置

### 3) news-brief / 青闻日报试运行
- 状态：进行中
- 目标：产出一版可交付的每日首次汇报样例（AI / 科学 / 中国新闻）
- 已完成：
  - `news-brief` agent 已创建并加载
  - 已接入每日首次汇报规则
- 当前阻塞：
  - 试运行任务耗时长，尚未拿到完整可交付样例
- 下一步：
  - 继续后台慢跑，拿到首版正式日报样例

## 待验证

### 4) Auto-compaction 自动压缩是否真正生效
- 状态：待验证
- 背景：官方支持 compaction，且当前已把 `agents.defaults.compaction.mode` 从 `safeguard` 改为 `default`
- 已确认：
  - 当前配置值为 `default`
- 待验证点：
  - 长会话逼近上限时，是否会自动压缩并无感续跑
- 触发方式：
  - 后续一旦再次出现上下文逼近/达到上限，立即复查

## 已完成（近期）
- 常规 exec 免审批已打通（官方 approvals --gateway 路径）
- ngrok 自启动已配置
- 每日首次交互已接入 ngrok 状态 / 域名变化汇报
- `news-brief`、`browser-ops`、`windows-ops` agent 已加载
- 根仓库 Git 结构已整理到 `C:\Users\wei\.openclaw`
