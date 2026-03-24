# NotebookLM MCP & CLI 用户文档

## 1. 服务使用指南

### 1.1 项目介绍

NotebookLM MCP & CLI 是一个提供程序化访问 Google NotebookLM 的工具，通过命令行界面 (CLI) 或模型上下文协议 (MCP) 服务器与 NotebookLM 进行交互。本工具允许用户通过命令行或 AI 助手 (如 Claude、Gemini、Cursor 等) 操作 NotebookLM，实现自动化工作流程和更灵活的使用方式。

### 1.2 安装方法

#### 使用 uv (推荐)
```bash
uv tool install notebooklm-mcp-cli
```

#### 使用 pip
```bash
pip install notebooklm-mcp-cli
```

#### 使用 pipx
```bash
pipx install notebooklm-mcp-cli
```

### 1.3 基本使用流程

1. **认证**：使用 `nlm login` 命令登录 Google 账户
2. **配置 MCP 服务器**：使用 `nlm setup add` 命令为 AI 工具配置 MCP 服务器
3. **管理笔记本**：创建、列出、查询笔记本
4. **添加资源**：添加 URL、文本、文件、YouTube 视频、Google Drive 文档等资源
5. **生成内容**：创建音频、视频、报告、测验等内容
6. **下载产物**：下载生成的音频、视频、报告等

### 1.4 核心功能介绍

#### 命令行界面 (CLI)

**笔记本管理**
```bash
nlm notebook list                      # 列出所有笔记本
nlm notebook create "研究项目"         # 创建笔记本
nlm notebook query <id> "问题"         # 与笔记本交互
```

**资源管理**
```bash
nlm source add <notebook> --url "https://..."  # 添加 URL
nlm source add <notebook> --text "内容" --title "笔记"  # 添加文本
nlm source add <notebook> --file document.pdf  # 上传文件
nlm source add <notebook> --youtube "https://..."  # 添加 YouTube
nlm source add <notebook> --drive <doc-id>     # 添加 Drive 文档
```

**内容生成**
```bash
nlm audio create <notebook> --confirm          # 创建音频
nlm video create <notebook> --confirm          # 创建视频
nlm report create <notebook> --confirm         # 创建报告
nlm quiz create <notebook> --confirm           # 创建测验
nlm flashcards create <notebook> --confirm     # 创建闪卡
nlm slides create <notebook> --confirm         # 创建幻灯片
```

**下载产物**
```bash
nlm download audio <notebook> <artifact-id> --output podcast.mp3
nlm download video <notebook> <artifact-id> --output video.mp4
nlm download report <notebook> <artifact-id> --output report.md
```

**研究功能**
```bash
nlm research start "查询" --notebook-id <id> --mode fast  # 快速搜索
nlm research start "查询" --notebook-id <id> --mode deep  # 深度研究
```

#### MCP 服务器

MCP 服务器允许 AI 助手与 NotebookLM 交互，支持自然语言命令：

- "列出我所有的 NotebookLM 笔记本"
- "创建一个关于量子计算的笔记本"
- "为这个笔记本生成一个播客"
- "添加这个 URL 到我的笔记本"

### 1.5 常见使用场景

**研究与发现**
- 创建研究笔记本并添加相关资源
- 使用研究功能自动发现和导入相关资源
- 跨笔记本查询获取综合信息

**内容创建**
- 从研究内容生成音频播客
- 创建视频讲解和幻灯片
- 生成报告、测验和闪卡

**智能管理**
- 检查并同步 Google Drive 资源
- 使用标签组织笔记本
- 批量操作多个笔记本

**分享与协作**
- 设置笔记本的公开访问权限
- 邀请其他用户作为查看者或编辑者

## 2. 认证流程说明

### 2.1 认证原理

NotebookLM 使用浏览器 cookie 进行认证（没有官方 API）。CLI/MCP 通过 Chrome DevTools Protocol (CDP) 从任何基于 Chromium 的浏览器中自动提取这些 cookie。

**支持的浏览器**（按优先级）：Google Chrome、Arc (macOS)、Brave、Microsoft Edge、Chromium、Vivaldi、Opera。

### 2.2 自动模式认证（推荐）

此方法会自动启动浏览器并在登录后提取 cookie。

**步骤**：
1. 完全关闭浏览器（Mac 上使用 Cmd+Q，或从任务栏退出）
2. 运行 `nlm login` 命令
3. 在打开的浏览器窗口中登录 Google 账户
4. 等待 "SUCCESS!" 消息

**后台流程**：
1. 检测第一个可用的支持浏览器（或配置的首选浏览器）
2. 创建用于认证的专用浏览器配置文件
3. 启动启用远程调试的浏览器
4. 用户通过浏览器登录 NotebookLM
5. 提取并缓存 cookie、CSRF 令牌和账户电子邮件
6. 自动关闭浏览器

### 2.3 文件模式认证

此方法允许手动提取和提供 cookie，适用于：
- 自动模式在系统上不起作用
- 有干扰的浏览器扩展（如 Google Antigravity IDE）
- 偏好手动控制

**步骤**：
1. 打开 Chrome 并访问 https://notebooklm.google.com
2. 确保已登录
3. 按 F12（或 Mac 上的 Cmd+Option+I）打开 DevTools
4. 点击 Network 选项卡
5. 在过滤框中输入：`batchexecute`
6. 点击任何笔记本以触发请求
7. 点击列表中的 `batchexecute` 请求
8. 在右侧面板中，滚动到 Request Headers
9. 找到以 `cookie:` 开头的行
10. 右键点击 cookie 值并选择 Copy value
11. 粘贴到文本文件并保存
12. 运行 `nlm login --manual --file /path/to/cookies.txt`

### 2.4 多用户配置

通过创建命名配置文件使用多个 Google 账户：

```bash
# 为不同账户创建配置文件
nlm login --profile work       # 打开浏览器 - 使用工作账户登录
nlm login --profile personal   # 打开浏览器 - 使用个人账户登录

# 列出所有配置文件
nlm login profile list

# 切换默认配置文件
nlm login switch personal

# 使用配置文件
nlm notebook list                    # 使用默认（个人）
nlm notebook list --profile work     # 使用工作账户
```

**多配置文件工作原理**：
- 每个配置文件获得：
  - 独立的凭证：存储在 `~/.notebooklm-mcp-cli/profiles/<name>/`
  - 独立的浏览器配置文件：在 `~/.notebooklm-mcp-cli/chrome-profiles/<name>/` 中的隔离浏览器会话
  - 捕获的电子邮件：在登录期间自动提取以便于识别

### 2.5 认证状态管理

**令牌存储位置**：
所有数据存储在 `~/.notebooklm-mcp-cli/` 下：

```
~/.notebooklm-mcp-cli/
├── config.toml                    # CLI 配置
├── aliases.json                   # 笔记本别名
├── profiles/                      # 认证配置文件
│   ├── default/
│   │   └── auth.json              # Cookies、令牌、电子邮件
│   ├── work/
│   │   └── auth.json
│   └── personal/
│       └── auth.json
├── chrome-profile/                # Chrome 配置文件（单配置文件用户）
└── chrome-profiles/               # Chrome 配置文件（多配置文件用户）
    ├── work/
    └── personal/
```

**令牌过期**：
- **Cookies**：通常稳定数周，但有些会在每次请求时轮换
- **CSRF 令牌**：在每次 MCP 客户端初始化时自动刷新
- **会话 ID**：在每次 MCP 客户端初始化时自动刷新

当开始看到认证错误时，只需再次运行 `nlm login` 来刷新。

### 2.6 安全注意事项

- Cookies 存储在本地的 `~/.notebooklm-mcp-cli/profiles/<name>/auth.json` 文件中
- 每个浏览器配置文件包含您的 Google 登录信息
- 切勿共享您的 `auth.json` 文件或提交到版本控制
- 仓库中的 `cookies.txt` 文件是模板 - 不要提交真实的 cookies

## 3. API 参考文档

### 3.1 API 概述

NotebookLM MCP 使用内部 API 与 Google NotebookLM 进行交互。这些 API 是未文档化的，可能会随时更改。本参考文档提供了对这些 API 的详细说明，仅用于调试 API 问题或添加新功能。

### 3.2 核心 API 端点

**基础端点**：
```
POST https://notebooklm.google.com/_/LabsTailwindUi/data/batchexecute
```

**请求格式**：
```
Content-Type: application/x-www-form-urlencoded

f.req=<URL-encoded JSON>&at=<CSRF token>
```

**查询端点**（流式）：
```
POST /_/LabsTailwindUi/data/google.internal.labs.tailwind.orchestration.v1.LabsTailwindOrchestrationService/GenerateFreeFormStreamed
```

### 3.3 常用 API 调用

#### 列出笔记本
```python
# RPC ID: wXbhsf
params = [null, 1, null, [2]]
```

#### 创建笔记本
```python
# RPC ID: CCqFvf
params = [title, null, null, [2], [1,null,null,null,null,null,null,null,null,null,[1]]]
```

#### 添加资源
```python
# RPC ID: izAoDd
# URL 资源
source_data = [
    None,
    None,
    [url],  # 普通网站的 URL 在位置 2
    None, None, None, None, None, None, None,
    1
]

# YouTube 资源
source_data = [
    None,
    None,
    None,  # YouTube 的位置 2 必须为 None
    None, None, None, None,
    [url],  # YouTube 的 URL 在位置 7
    None, None,
    1
]

# 文本资源
source_data = [
    None,
    [title, text_content],  # 标题和内容在位置 1
    None,
    2,  # 类型指示器在位置 3
    None, None, None, None, None, None,
    1
]

# Google Drive 资源
source_data = [
    [document_id, mime_type, 1, title],  # Drive 文档在位置 0
    None, None, None, None, None, None, None, None, None,
    1
]

params = [[[source_data]], notebook_id, [2], settings]
```

#### 查询笔记本
```python
# 使用单独的流式端点
params = [
    [  # 资源 ID - 每个都在嵌套数组中
        [[["source_id_1"]]],
        [[["source_id_2"]]],
    ],
    "您的问题在这里",  # 查询文本
    None,
    [2, None, [1]],  # 配置
    "conversation-uuid"  # 用于后续问题
]
```

#### 创建工作室内容
```python
# RPC ID: R7cb6c
# 音频概述
params = [
    [2],                           # 配置
    notebook_id,                   # 笔记本 UUID
    [
        None, None,
        1,                         # STUDIO_TYPE_AUDIO
        [[[source_id1]], [[source_id2]], ...],  # 资源 ID（嵌套数组）
        None, None,
        [
            None,
            [
                focus_prompt,      # AI 应该关注的焦点文本
                length_code,       # 1=Short, 2=Default, 3=Long
                None,
                [[source_id1], [source_id2], ...],  # 资源 ID（更简单的格式）
                language_code,     # "en", "es" 等
                None,
                format_code        # 1=Deep Dive, 2=Brief, 3=Critique, 4=Debate
            ]
        ]
    ]
]

# 视频概述
params = [
    [2],                           # 配置
    notebook_id,                   # 笔记本 UUID
    [
        None, None,
        3,                         # STUDIO_TYPE_VIDEO
        [[[source_id1]], [[source_id2]], ...],  # 资源 ID（嵌套数组）
        None, None, None, None,
        [
            None, None,
            [
                [[source_id1], [source_id2], ...],  # 资源 ID
                language_code,     # "en", "es" 等
                focus_prompt,      # 焦点文本
                None,
                format_code,       # 1=Explainer, 2=Brief
                visual_style_code  # 1=Auto, 2=Custom, 3=Classic 等
            ]
        ]
    ]
]
```

### 3.4 错误处理

**常见错误**：

1. **401 Unauthorized** 或 **403 Forbidden**：Cookies 已过期，需要重新认证
2. **浏览器正在运行但未启用远程调试**：完全关闭浏览器后重试
3. **自动模式连接失败**：尝试使用文件模式 `nlm login --manual`
4. **Cookie 文件显示 "缺少必需的 cookie"**：确保复制的是 cookie 值，而不是标头名称

### 3.5 最佳实践

1. **使用配置文件**：为不同的 Google 账户使用单独的配置文件
2. **定期刷新认证**：当遇到认证错误时，运行 `nlm login` 刷新
3. **使用别名**：为常用笔记本创建别名以简化命令
4. **使用 `--wait`**：添加资源时使用 `--wait` 确保它们在查询前准备就绪
5. **使用 `--confirm`**：在脚本中为所有创建/删除命令使用 `--confirm`
6. **轮询状态**：音频/视频生成需要 1-5 分钟，使用 `nlm studio status` 轮询
7. **运行诊断**：使用 `nlm doctor` 诊断安装、认证或配置问题

## 4. 服务管理

### 4.1 配置管理

```bash
nlm config show                         # 显示所有设置
nlm config get auth.default_profile     # 获取特定值
nlm config set auth.default_profile work  # 设置默认配置文件
nlm config set output.format json       # 更改默认输出格式
```

**可用设置**：

| 键 | 默认值 | 描述 |
|-----|---------|-------------|
| `output.format` | `table` | 默认输出格式（table, json） |
| `output.color` | `true` | 启用彩色输出 |
| `output.short_ids` | `true` | 显示缩短的 ID |
| `auth.browser` | `auto` | 登录首选浏览器（auto, chrome, arc, brave, edge, chromium, vivaldi, opera）。如果首选浏览器未找到，会回退到自动检测。 |
| `auth.default_profile` | `default` | 未指定 `--profile` 时使用的配置文件。**注意：** MCP 服务器始终使用活动的默认配置文件。更改此设置将立即切换 MCP 服务器的 Google 账户。 |

### 4.2 别名管理

```bash
nlm alias set myproject <notebook-id>   # 创建别名
nlm alias list                          # 列出所有别名
nlm alias get myproject                 # 解析为 UUID
nlm alias delete myproject              # 删除别名

# 在任何地方使用别名
nlm notebook get myproject
nlm source list myproject
```

### 4.3 MCP 服务器配置

```bash
nlm setup add claude-code       # 配置 Claude Code
nlm setup add gemini            # 写入 ~/.gemini/settings.json
nlm setup add cursor            # 写入 ~/.cursor/mcp.json
nlm setup add windsurf          # 写入 mcp_config.json
nlm setup add json              # 为任何工具生成 JSON 配置

nlm setup remove gemini         # 从 Gemini CLI 中移除

nlm setup list                  # 显示所有客户端和配置状态
```

### 4.4 技能安装

```bash
nlm skill list                           # 显示安装状态
nlm skill install claude-code            # 为 Claude Code 安装
nlm skill install cursor                 # 为 Cursor AI 安装
nlm skill install agents               # 为 Gemini CLI / Codex 安装
nlm skill uninstall <tool>               # 移除技能
```

**支持的工具**：`claude-code`, `cursor`, `agents`, `opencode`, `antigravity`, `cline`, `openclaw`, `other`

## 5. 故障排除

### 5.1 常见问题

1. **`uv tool upgrade` 未安装最新版本**
   - 症状：运行 `uv tool upgrade notebooklm-mcp-cli` 安装旧版本
   - 原因：`uv tool upgrade` 尊重原始安装的版本约束
   - 解决方法：强制重新安装 `uv tool install --force notebooklm-mcp-cli`

2. **认证失败**
   - 确保浏览器完全关闭
   - 尝试使用不同的浏览器
   - 尝试文件模式认证

3. **MCP 服务器连接问题**
   - 确保已认证：`nlm login --check`
   - 检查 MCP 配置：`nlm setup list`
   - 运行诊断：`nlm doctor`

4. **内容生成失败**
   - 检查笔记本是否有足够的资源
   - 检查网络连接
   - 尝试使用更简洁的提示

### 5.2 诊断工具

运行诊断以排查安装、认证和配置问题：

```bash
nlm doctor              # 运行所有检查
nlm doctor --verbose    # 包括其他详细信息（Python 版本、路径等）
```

**执行的检查**：

| 类别 | 检查内容 |
|----------|---------------|
| 安装 | 包版本、`nlm` 和 `notebooklm-mcp` 二进制路径 |
| 认证 | 配置文件状态、cookie 存在、CSRF 令牌、账户电子邮件 |
| 浏览器 | 安装了基于 Chromium 的浏览器，为无头认证保存了配置文件 |
| AI 工具 | 每个支持的客户端的 MCP 配置状态 |

每个问题都包含建议的修复方案（例如，"运行 `nlm login` 进行认证"）。

## 6. 限制

- **速率限制**：免费套餐每天约有 50 个查询
- **无官方支持**：API 可能会随时更改而不通知
- **Cookie 过期**：每隔几周需要重新提取 cookie

## 7. 安全注意事项

- 本工具使用未文档化的内部 API，可能会随时更改
- 认证信息存储在本地文件中，请妥善保管
- 不要在生产环境中使用此工具
- 使用风险自负，仅用于个人/实验目的

## 8. 总结

NotebookLM MCP & CLI 提供了一种强大的方式来程序化访问 Google NotebookLM，通过命令行界面或 AI 助手实现自动化工作流程。本用户文档提供了详细的使用指南、认证流程说明和 API 参考，帮助用户充分利用此工具的功能。

通过遵循本文档中的指导，用户可以：
- 快速安装和配置工具
- 有效地管理笔记本和资源
- 生成各种类型的内容
- 与 AI 助手无缝集成
- 排查常见问题

祝您使用愉快！