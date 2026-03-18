# NotebookLM MCP 配置指南（MacBook）

本指南将详细说明如何在 MacBook 上配置 NotebookLM MCP（Model Context Protocol）服务器，以便在 AI coding 工具中使用。

## 目录

1. [准备工作](#准备工作)
2. [安装 NotebookLM MCP CLI](#安装-notebooklm-mcp-cli)
3. [认证设置](#认证设置)
4. [配置 MCP 服务器](#配置-mcp-服务器)
5. [在 AI 工具中设置](#在-ai-工具中设置)
   - [Claude Code](#claude-code)
   - [Cursor](#cursor)
   - [Gemini CLI](#gemini-cli)
   - [其他工具](#其他工具)
6. [测试 MCP 连接](#测试-mcp-连接)
7. [故障排除](#故障排除)
8. [常见问题](#常见问题)

## 准备工作

在开始之前，请确保：

- 你有一个 Google 账户，并且已经登录到 NotebookLM
- 你的 MacBook 运行的是 macOS
- 你已经安装了 Python 3.11 或更高版本
- 你可以访问终端应用程序

## 安装 NotebookLM MCP CLI

### 方法 1：使用 uv（推荐）

1. 打开终端应用程序（在应用程序 > 实用工具中）
2. 安装 uv（如果尚未安装）：
   ```bash
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```
3. 安装 NotebookLM MCP CLI：
   ```bash
   uv tool install notebooklm-mcp-cli
   ```

### 方法 2：使用 pip

1. 打开终端应用程序
2. 运行以下命令：
   ```bash
   pip install notebooklm-mcp-cli
   ```

### 方法 3：使用 pipx

1. 打开终端应用程序
2. 安装 pipx（如果尚未安装）：
   ```bash
   brew install pipx
   pipx ensurepath
   ```
3. 安装 NotebookLM MCP CLI：
   ```bash
   pipx install notebooklm-mcp-cli
   ```

### 验证安装

安装完成后，运行以下命令验证安装成功：

```bash
nlm --version
```

你应该看到版本信息，例如：`nlm version 0.4.9`

## 认证设置

在使用 MCP 服务器之前，你需要先认证到 NotebookLM：

1. 打开终端应用程序
2. 运行以下命令：
   ```bash
   nlm login
   ```
3. 系统会自动打开 Chrome 浏览器，让你登录 Google 账户
4. 登录后，浏览器会自动关闭，cookies 会被提取并保存
5. 终端会显示认证成功的消息

### 验证认证

运行以下命令验证认证是否成功：

```bash
nlm login --check
```

你应该看到类似以下的输出：
```
✓ Authentication valid!
  Profile: default
  Notebooks found: X
  Account: your-email@example.com
```

## 配置 MCP 服务器

### 自动配置（推荐）

NotebookLM MCP CLI 提供了自动配置功能，可以为常见的 AI 工具设置 MCP 服务器：

#### 配置 Claude Code

```bash
nlm setup add claude-code
```

#### 配置 Cursor

```bash
nlm setup add cursor
```

#### 配置 Gemini CLI

```bash
nlm setup add gemini
```

### 检查已配置的工具

运行以下命令查看已配置的工具：

```bash
nlm setup list
```

## 在 AI 工具中设置

### Claude Code

1. 打开 Claude Code 应用程序
2. 点击左上角的菜单按钮
3. 选择 "Settings" > "MCP"
4. 你应该看到 "notebooklm-mcp" 已经在列表中
5. 如果没有，点击 "Add MCP Server"，输入以下信息：
   - Name: notebooklm-mcp
   - Command: notebooklm-mcp

### Cursor

1. 打开 Cursor 应用程序
2. 点击左上角的菜单按钮
3. 选择 "Settings" > "MCP"
4. 确保 "notebooklm-mcp" 已启用

### Gemini CLI

1. 打开终端应用程序
2. 运行以下命令：
   ```bash
   gemini mcp add --scope user notebooklm-mcp notebooklm-mcp
   ```

### 其他工具

对于其他支持 MCP 的工具，你可以生成 JSON 配置：

```bash
nlm setup add json
```

然后按照工具的说明添加 MCP 服务器配置。

## 测试 MCP 连接

### 在 Claude Code 中测试

1. 打开 Claude Code
2. 在聊天窗口中输入：
   ```
   List all my NotebookLM notebooks
   ```
3. Claude 应该会调用 MCP 工具并返回你的 NotebookLM 笔记本列表

### 在 Cursor 中测试

1. 打开 Cursor
2. 在聊天窗口中输入：
   ```
   List all my NotebookLM notebooks
   ```
3. Cursor 应该会调用 MCP 工具并返回你的 NotebookLM 笔记本列表

### 在 Gemini CLI 中测试

1. 打开终端应用程序
2. 运行以下命令：
   ```bash
   gemini chat
   ```
3. 在聊天中输入：
   ```
   List all my NotebookLM notebooks
   ```
4. Gemini 应该会调用 MCP 工具并返回你的 NotebookLM 笔记本列表

## 指定具体的 Notebook

当你有多个 NotebookLM 笔记本时，你可以指定 AI 工具使用某一个具体的笔记本。

### 获取 Notebook ID

1. 打开终端应用程序
2. 运行以下命令列出所有笔记本：
   ```bash
   nlm notebook list
   ```
3. 在输出中找到你想要使用的笔记本，复制其 ID

### 在 AI 工具中指定 Notebook

#### 在 Claude Code、Cursor 或 Gemini 中

当你向 AI 提问时，明确指定 notebook ID：

```
使用 notebook ID: <notebook-id> 查询关于...的内容
```

例如：
```
使用 notebook ID: abc123def456 查询关于量子计算的笔记内容
```

#### 具体工具示例

##### Claude Code
1. 打开 Claude Code
2. 输入：
   ```
   请使用 notebook ID: abc123def456 告诉我这个笔记本中关于机器学习的内容
   ```

##### Cursor
1. 打开 Cursor
2. 输入：
   ```
   请查询 notebook ID: abc123def456 中的项目计划
   ```

##### Gemini CLI
1. 打开终端
2. 运行 `gemini chat`
3. 输入：
   ```
   请使用 notebook ID: abc123def456 总结这个笔记本的主要内容
   ```

### 使用笔记本别名

为了更方便地引用笔记本，你可以创建别名：

1. 打开终端应用程序
2. 运行以下命令创建别名：
   ```bash
   nlm alias set my-research <notebook-id>
   ```
3. 然后在 AI 工具中使用别名：
   ```
   使用笔记本别名: my-research 查询关于...的内容
   ```

### 其他操作指定 Notebook

除了查询外，你还可以在其他操作中指定 notebook：

- **查看笔记本详情**：
  ```
  请获取 notebook ID: abc123def456 的详细信息
  ```

- **获取笔记本摘要**：
  ```
  请获取 notebook ID: abc123def456 的 AI 生成摘要
  ```

- **向指定笔记本添加资源**：
  ```
  请向 notebook ID: abc123def456 添加 URL: https://example.com/article
  ```

## 故障排除

### 认证问题

如果遇到认证错误：

1. 重新运行认证命令：
   ```bash
   nlm login
   ```
2. 确保你在浏览器中登录了正确的 Google 账户

### MCP 服务器连接问题

如果 AI 工具无法连接到 MCP 服务器：

1. 检查 MCP 服务器是否正在运行
2. 运行诊断命令：
   ```bash
   nlm doctor
   ```
3. 按照诊断结果的建议进行修复

### 权限问题

如果遇到权限错误：

1. 确保你有足够的权限运行命令
2. 对于 pip 安装，可能需要使用 `sudo`：
   ```bash
   sudo pip install notebooklm-mcp-cli
   ```

## 常见问题

### Q: MCP 服务器需要一直运行吗？

A: 不需要。当 AI 工具需要使用 MCP 功能时，会自动启动 MCP 服务器。

### Q: 我可以在多个 AI 工具中同时使用 MCP 吗？

A: 是的，多个 AI 工具可以同时使用同一个 MCP 服务器。

### Q: MCP 会使用我的 Google 账户权限做什么？

A: MCP 只会访问 NotebookLM 相关的功能，如查看笔记本、添加资源、生成内容等。

### Q: 认证会过期吗？

A: 是的，认证会在 2-4 周后过期。当过期时，你需要重新运行 `nlm login` 命令。

### Q: 我可以使用多个 Google 账户吗？

A: 是的，你可以使用配置文件功能：
   ```bash
   nlm login --profile work
   nlm login --profile personal
   nlm login switch work
   ```

## 总结

通过以上步骤，你应该已经成功在 MacBook 上配置了 NotebookLM MCP 服务器，并在 AI 工具中设置了连接。现在你可以在 AI 工具中直接询问关于 NotebookLM 内容的问题，AI 会自动查询 MCP 并给你回答。

如果遇到任何问题，请运行 `nlm doctor` 命令进行诊断，或参考项目的 [GitHub 仓库](https://github.com/jacob-bd/notebooklm-mcp-cli) 获取更多帮助。