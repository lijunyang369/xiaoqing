# TASKS.md

最后更新：2026-03-19

## 进行中

### 1) GitHub 云端同步打通
- 状态：进行中
- 目标：将 `C:\Users\wei\.openclaw` 根仓库成功推送到 `git@github.com:lijunyang369/xiaoqing.git`
- 已完成：
  - 根仓库已迁到 `C:\Users\wei\.openclaw`
  - remote 已配置为 GitHub 仓库
  - 本地 GitHub SSH key 已生成并配置默认使用
- 当前阻塞：
  - GitHub 端公钥授权 / push 结果仍待最终验证
- 下一步：
  - 继续验证 `ssh -T git@github.com` 与 `git push`

### 2) browser-ops / 青览打通 GitHub 浏览器配置
- 状态：进行中
- 目标：通过专职浏览器 agent 完成 GitHub 相关网页配置
- 已完成：
  - `browser-ops` agent 已创建
  - 已加载到 gateway
  - browser 官方能力存在
  - 当前用户手动启动 browser 后，青览已推进本地 GitHub SSH 准备工作
  - Discord 已配置完成，后续浏览器类任务可优先尝试通过 Discord 线程/子会话承接
- 当前阻塞：
  - 浏览器自动控制链在 agent 侧仍不稳定，尚未可靠完成 GitHub 页面自动操作
- 下一步：
  - 继续围绕 GitHub 配置链推进，优先完成 SSH/push 验证；随后在 Discord 中验证青览线程化承接能力

### 3) Discord 持久会话配置
- 状态：已完成
- 目标：让 Discord 成为可承载持久子会话/线程化协作的渠道
- 已完成：
  - Discord 渠道已写入配置并通过校验
  - Bot 已成功登录并已能回复
  - 已开启 `threadBindings.enabled = true`
  - 已开启 `threadBindings.spawnSubagentSessions = true`
- 当前说明：
  - 配置目标已完成；后续如要验证 thread/子会话体验，再在 Discord 实际使用中继续检验

### 4) news-brief / 青闻日报试运行
- 状态：进行中
- 目标：产出一版可交付的每日首次汇报样例（AI / 科学 / 中国新闻）
- 已完成：
  - `news-brief` agent 已创建并加载
  - 已接入每日首次汇报规则
- 当前阻塞：
  - 试运行任务耗时长，尚未拿到完整可交付样例
- 下一步：
  - 继续后台慢跑，拿到首版正式日报样例

## 待处理 / 待修复

### 5) gateway restart 后缺少主动状态汇报
- 状态：待修复
- 目标：每次 gateway restart 后，主动汇报“当前状态 / 本次改动 / 是否生效 / 剩余问题”
- 当前问题：
  - 实际执行过 restart 后，未稳定做到主动汇报当前任务状态与结果
- 下一步：
  - 将 restart 后状态汇报视为强制收尾步骤，未汇报前不算任务完成

## 已完成（近期）
- Auto-compaction 自动压缩验证：当前无问题，移出待验证
- 常规 exec 免审批已打通（官方 approvals --gateway 路径）
- ngrok 自启动已配置
- 每日首次交互已接入 ngrok 状态 / 域名变化汇报
- `news-brief`、`browser-ops`、`windows-ops` agent 已加载
- 根仓库 Git 结构已整理到 `C:\Users\wei\.openclaw`
