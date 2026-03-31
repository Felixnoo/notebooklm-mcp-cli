---
name: notebooklm-skill
version: "1.0.0"
description: "NotebookLM 集成工具，支持安装和查询 Google NotebookLM，为 AI Coding 工具提供 NotebookLM 访问能力。当用户提问中包含 online help、online help bot、notebooklm 或 notebook 等关键词时，自动使用此 SKILL。"
---

# NotebookLM 集成工具

## 核心功能

### 1. 安装 notebooklm-mcp-cli

- 自动检测是否安装了 uv，如果没安装，执行 `curl -Ls https://astral.sh/uv/install.sh | sh`
- 自动执行 `uv tool install notebooklm-mcp-cli` 安装 notebooklm-mcp-cli
- 自动执行 `nlm login` 登录谷歌账号
- 自动执行 `nlm setup add` 命令给当前 AI Coding 工具设置 MCP Server，例如为 Claude Code 设置：nlm setup add claude-code；为 Gemini 设置：nlm setup add gemini

### 2. 查询 NotebookLM

- 自动执行 `nlm notebook list` 查看当前账户可用的 NotebookLM
- 优先使用名称中包含 "Online Help Bot" 关键词的 notebook 进行查询
- 命令示例：`nlm query notebook <notebook-id> "你的问题"`
- 当谷歌 NotebookLM 账户鉴权过期后，提供明确的操作提示

## 支持的 AI 工具

- Gemini CLI
- Claude Code
- 其他支持 MCP 协议的 AI 工具

## 使用方法

### 关键词触发

当你向 AI 工具提问时，只要包含以下关键词之一，就会自动触发此 SKILL：
- online help
- online help bot
- notebooklm
- notebook

### 查询 NotebookLM

当 SKILL 被触发时，它会自动：
1. 检查是否已安装并配置 notebooklm-mcp-cli
2. 列出可用的 NotebookLM 笔记本
3. 优先选择包含 "Online Help Bot" 的笔记本
4. 使用该笔记本进行查询
5. 返回查询结果

### 约束与规范

当决定使用 nlm 工具调用 NotebookLM，并且拿到了返回的 JSON 结果后，你必须遵守以下极其严苛的纪律：
- **100% 原样搬运**：你必须提取工具返回的 `answer` 字段，**一字不差、原封不动**地输出给我。
- **零篡改**：绝对不允许对 `answer` 进行任何形式的总结、提炼、润色、或翻译。

### 示例使用场景

- "总结 25R3.3 中的所有新功能"
- "介绍一下报表引擎"
- "怎么配置 Chat (HCP)"

## 常见问题

### 1. 鉴权过期

**问题**：执行命令时提示鉴权过期

**解决方案**：重新执行 `nlm login` 登录谷歌账号

### 2. 找不到包含 "Online Help Bot" 的笔记本

**问题**：没有找到名称中包含 "Online Help Bot" 的笔记本

**解决方案**：系统会自动选择第一个可用的笔记本进行查询，或者你可以手动指定笔记本 ID

### 3. 安装失败

**问题**：安装过程中出现错误

**解决方案**：
- 检查网络连接
- 确保有权限安装软件
- 尝试使用管理员权限运行命令

## 注意事项

- 本工具使用 Google NotebookLM 的内部 API，可能会随 Google 更新而变化
- 请确保遵守 Google 的使用条款