# NotebookLM MCP 内部工具 - 构建、分发与测试指南

本指南详细说明如何构建、分发和测试 NotebookLM MCP 内部工具，确保公司同事能够顺利安装和使用。

## 1. 构建包

### 1.1 前提条件

- Python 3.9 或更高版本
- `build` 模块（用于构建包）
- `twine` 模块（用于上传到 PyPI，可选）

### 1.2 安装构建依赖

```bash
# 安装 build 模块
pip3 install build

# 安装 twine（如果需要上传到 PyPI）
pip3 install twine
```

### 1.3 构建包

```bash
# 清理之前的构建产物（可选）
rm -rf dist/

# 构建包
python3 -m build

# 构建完成后，会在 dist/ 目录生成以下文件：
# - notebooklm_mcp_cli-0.4.9-py3-none-any.whl（wheel 包）
# - notebooklm-mcp-cli-0.4.9.tar.gz（源码包）
```

### 1.4 验证构建结果

```bash
# 查看构建产物
ls -la dist/

# 验证 wheel 包内容
unzip -l dist/notebooklm_mcp_cli-0.4.9-py3-none-any.whl
```

## 2. 分发包

### 2.1 本地分发

#### 方法一：直接分享构建的包文件

1. 将 `dist/` 目录中的 `.whl` 文件分享给同事
2. 同事可以直接安装：
   ```bash
   pip3 install notebooklm_mcp_cli-0.4.9-py3-none-any.whl
   ```

#### 方法二：从源代码安装

1. 将整个仓库分享给同事，或让他们克隆仓库
2. 同事可以从源代码安装：
   ```bash
   # 克隆仓库
   git clone <仓库地址>
   cd notebooklm-mcp-cli
   
   # 使用 pip 安装
   pip3 install .
   
   # 或使用 uv 安装
   uv tool install .
   ```

### 2.2 发布到 PyPI（可选）

如果需要更广泛的分发，可以发布到 PyPI：

1. 确保你有 PyPI 账号和 API token
2. 上传包：
   ```bash
   # 测试上传到 Test PyPI（可选）
   twine upload --repository testpypi dist/*
   
   # 上传到 PyPI
   twine upload dist/*
   ```
3. 同事就可以通过标准方式安装：
   ```bash
   pip3 install notebooklm-mcp-cli
   # 或
   uv tool install notebooklm-mcp-cli
   ```

### 2.3 内部分发渠道

#### 方法一：公司内部 PyPI 镜像

如果公司有内部 PyPI 镜像，可以将包上传到内部镜像，同事从内部镜像安装：

```bash
# 从内部镜像安装
pip3 install --index-url <内部镜像地址> notebooklm-mcp-cli
```

#### 方法二：公司内部文件服务器

将构建的包文件上传到公司内部文件服务器，同事从服务器下载安装：

```bash
# 从内部服务器下载并安装
wget <服务器地址>/notebooklm_mcp_cli-0.4.9-py3-none-any.whl
pip3 install notebooklm_mcp_cli-0.4.9-py3-none-any.whl
```

## 3. 测试包

### 3.1 本地测试

在构建完成后，进行本地测试以确保包正常工作：

```bash
# 安装本地构建的包
pip3 install dist/notebooklm_mcp_cli-0.4.9-py3-none-any.whl

# 验证安装
nlm --version

# 运行内部工具命令
nlm internal --help

# 测试一键设置
nlm internal setup

# MCP 服务器会在 AI 工具使用时自动启动
```

### 3.2 同事测试流程

同事按照以下步骤测试安装：

1. **安装包**：
   ```bash
   # 从分享的文件安装
   pip3 install notebooklm_mcp_cli-0.4.9-py3-none-any.whl
   
   # 或从源代码安装
   pip3 install .
   ```

2. **运行一键设置**：
   ```bash
   nlm internal setup
   ```
   该命令会：
   - 安装所有必要的依赖
   - 检测本地 AI 工具
   - 交互式配置 AI 工具
   - 自动完成鉴权
   - 自动获取公司的 NotebookLM ID

3. **使用 AI 工具**：
   当你在 AI 工具中提问时，AI 工具会自动启动 MCP 服务器。
   
   服务器启动时会：
   - 从 GitHub Secret Gist 获取最新 ID
   - 检测 ID 有效性
   - 自动更新 ID（如果有变化）

4. **在 AI 工具中测试**：
   - **Claude Code**：直接提问，例如 "根据公司的 NotebookLM 文档，如何设置 MCP 服务器？"
   - **Cursor**：使用 `@notebooklm` 指令，例如 "@notebooklm 公司的项目架构是什么？"
   - **Gemini CLI**：直接提问，AI 会自动通过 MCP 查询 NotebookLM

### 3.3 验证功能

测试以下关键功能：

1. **ID 管理**：
   - 检查 MCP 服务器是否能从 Gist 获取 ID
   - 测试 ID 更新功能
   - **查看获取到的 NotebookLM ID**：
     - 方法一：查看配置文件
       ```bash
       cat ~/.notebooklm-mcp-cli/config.toml
       ```
     - 方法二：使用命令行工具
       ```bash
       nlm config get company.id
       ```
     - 方法三：查看 GitHub Gist
       - Gist URL: https://gist.github.com/Felixnoo/f87fea475b39aa024e2a81cfa1825592
       - 原始内容 URL: https://gist.githubusercontent.com/Felixnoo/f87fea475b39aa024e2a81cfa1825592/raw

2. **AI 工具集成**：
   - 测试与 Claude Code 的集成
   - 测试与 Cursor 的集成
   - 测试与 Gemini CLI 的集成

3. **鉴权功能**：
   - 测试自动鉴权流程
   - 测试鉴权信息的保存和使用

## 4. 常见问题与解决方案

### 4.1 构建问题

#### 问题：构建失败，提示缺少依赖
**解决方案**：
```bash
pip3 install --upgrade build
```

#### 问题：构建过程中出现权限错误
**解决方案**：
```bash
# 使用 --user 选项
python3 -m build --user
```

### 4.2 安装问题

#### 问题：安装后 `nlm` 命令不可用
**解决方案**：
- 检查 Python 的 `bin` 目录是否在 PATH 中
- 重新安装并使用 `--user` 选项
  ```bash
  pip3 install --user notebooklm_mcp_cli-0.4.9-py3-none-any.whl
  ```

#### 问题：依赖冲突
**解决方案**：
- 使用虚拟环境安装
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip3 install notebooklm_mcp_cli-0.4.9-py3-none-any.whl
  ```

### 4.3 运行问题

#### 问题：无法访问 GitHub Gist
**解决方案**：
- 确保网络连接正常
- 确保同事有公司 GitHub 账户
- 检查 Gist URL 是否正确

#### 问题：鉴权失败
**解决方案**：
- 确保同事有公司 NotebookLM 的访问权限
- 运行 `nlm login` 手动完成鉴权
- 检查浏览器是否正常启动

#### 问题：AI 工具无法访问 MCP
**解决方案**：
- 确保 MCP 服务器正在运行：`nlm mcp status`
- 重启 MCP 服务器：`nlm mcp stop && nlm mcp start`
- 检查 AI 工具的 MCP 配置是否正确

### 4.4 日志查看

当遇到问题时，可以查看 MCP 服务器的日志：

```bash
# 查看日志文件
ls -la ~/.notebooklm-mcp/logs/

# 查看最新日志
tail -f ~/.notebooklm-mcp/logs/mcp-server.log
```

## 5. 版本管理

### 5.1 版本号更新

当需要发布新版本时，更新 `pyproject.toml` 文件中的版本号：

```toml
[project]
name = "notebooklm-mcp-cli"
version = "0.4.10"  # 更新版本号
```

## 6. ID 检测与更新时机

工具会在以下时机检测并更新 NotebookLM ID：

### 6.1 MCP 服务器启动时

当 MCP 服务器启动时（无论是通过 AI 工具自动启动还是手动启动），会执行以下步骤：
1. 首先尝试从 GitHub Gist 获取最新的 ID
2. 如果 Gist 中有 ID 且与当前配置不同，则更新配置
3. 如果无法从 Gist 获取 ID，则使用配置文件中已有的 ID
4. 如果配置文件中也没有 ID，则尝试自动发现一个有效的 NotebookLM ID

### 6.2 手动触发

你也可以通过以下命令手动触发 ID 检查和更新：

```bash
# 检查当前配置的 Notebook ID 是否有效
nlm internal check-id

# 手动从 Gist 刷新 Notebook ID
nlm internal refresh-id
```

### 6.3 ID 更新流程

当检测到新的 ID 时，工具会：
1. 记录 ID 变更到日志
2. 更新本地配置文件
3. 使用新的 ID 进行后续的 NotebookLM 查询

这样可以确保工具始终使用最新的、有效的 NotebookLM ID，无需手动干预。

### 6.2 发布流程

1. 更新版本号
2. 构建新包
3. 测试新包
4. 分发新包
5. 通知同事升级

### 6.3 升级命令

同事可以使用以下命令升级到最新版本：

```bash
# 使用 pip
pip3 install --upgrade notebooklm-mcp-cli

# 或使用 uv
uv tool upgrade notebooklm-mcp-cli
```

## 7. 安全注意事项

1. **Gist URL 保护**：不要公开 Secret Gist URL，只分享给公司内部同事
2. **鉴权信息**：鉴权信息存储在本地配置文件中，确保不要共享该文件
3. **版本控制**：不要将构建产物提交到版本控制系统，将 `dist/` 目录添加到 `.gitignore`

## 8. 完全卸载

如果需要完全卸载 NotebookLM MCP 内部工具，可以按照以下步骤操作：

### 8.1 从 AI 工具中移除

```bash
# 从 Claude Code 中移除
nlm setup remove claude-code

# 从 Cursor 中移除
nlm setup remove cursor

# 从 Gemini 中移除
nlm setup remove gemini

# 从其他工具中移除
nlm setup remove <tool-name>
```

### 8.2 卸载包

```bash
# 使用 pip
pip3 uninstall notebooklm-mcp-cli

# 或使用 uv
uv tool uninstall notebooklm-mcp-cli
```

### 8.3 删除配置文件和缓存数据

```bash
# 删除配置文件和缓存数据
rm -rf ~/.notebooklm-mcp

# 删除鉴权信息
rm -rf ~/.notebooklm-mcp-cli
```

### 8.4 验证卸载

```bash
# 检查命令是否仍然存在
which nlm
which notebooklm-mcp

# 检查配置目录是否已删除
ls -la ~/.notebooklm-mcp
ls -la ~/.notebooklm-mcp-cli
```

如果以上命令都返回不存在的信息，则表示卸载完成。

## 9. 命令参考

### 9.1 `nlm internal` 命令组

- **`nlm internal setup`**：一键完成安装、配置、鉴权和 ID 获取
- **`nlm internal install`**：安装依赖并配置 AI 工具
- **`nlm internal auth`**：完成鉴权并获取公司的 NotebookLM ID
- **`nlm internal check-id`**：检查当前配置的 Notebook ID 是否有效
- **`nlm internal refresh-id`**：手动从 Gist 刷新 Notebook ID

### 9.2 其他常用命令

- **`nlm mcp start`**：启动 MCP 服务器
- **`nlm mcp stop`**：停止 MCP 服务器
- **`nlm mcp status`**：查看 MCP 服务器状态
- **`nlm login`**：手动登录 NotebookLM
- **`nlm login --check`**：检查登录状态

## 10. 在 AI 工具中使用

启动 MCP 服务器后，你可以在以下 AI coding 工具中直接向 NotebookLM 提问：

### 10.1 Claude Code

在 Claude Code 中，你可以直接提问，例如：

```
根据公司的 NotebookLM 文档，如何设置 MCP 服务器？
```

### 10.2 Cursor

在 Cursor 中，你可以使用 `@notebooklm` 指令：

```
@notebooklm 公司的项目架构是什么？
```

### 10.3 Gemini CLI

在 Gemini CLI 中，你可以直接提问，AI 会自动通过 MCP 查询 NotebookLM。

## 11. 联系支持

如果遇到无法解决的问题，请联系：

- **技术支持**：[技术支持邮箱]
- **管理员**：[管理员联系方式]

---

**更新时间**：2026-03-18
**文档版本**：1.2.0