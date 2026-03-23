# TASKS.md

最后更新：2026-03-23

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
- 状态：已完成
- 目标：通过专职浏览器 agent 完成 GitHub 相关网页配置
- 已完成：
  - `browser-ops` agent 已创建并加载到 gateway
  - Discord 侧 `青览` 账号已成功登录并可承接会话
  - WSL 自管浏览器验收通过，可访问 GitHub
  - 已确认：青览已具备承接 GitHub / 浏览器页面类任务的能力
- 当前说明：
  - 当前可用主路径是 WSL 自管浏览器
  - `chrome-relay` 仍未稳定可用，不作为当前默认执行路径
- 下一步：
  - 浏览器公开页 / 无登录页任务优先分流给青览处理
  - 需要登录态、2FA、验证码或高风险写操作时，再切人工浏览器接管

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
- Discord 双 bot（`小青` / `青览`）已成功上线
- WSL 自管浏览器验收通过，青览已具备浏览器页面类任务承接能力
- 根仓库 Git 结构已整理到 `C:\Users\wei\.openclaw`
