# 背景

我不懂技术，但是想借助 AI 全面分析目前这个项目，把它做成一个 SKILL，供其他公司内部同事使用这个 SKILL，可以支持常见的 AI Coding 工具，包括 Gemini CLI、Claude Code 等，至少覆盖当前项目已经支持的 AI 工具。

# 需求

我希望通过这个 SKILL，能让 AI Coding 工具在识别到合适的提问时，自动使用这个工具去查询 notebooklm。拿到 SKILL 的人不需要关心这个项目本身，也不需要在本地克隆当前的仓库代码。

目前我能想到的大致思路是，这个 SKILL 中主要包括 2 大能力：
- 第一大能力是安装 notebooklm-mcp-cli，包括：
  - 让 AI 自动检测是否安装了 uv，如果没安装，就执行 curl -Ls https://astral.sh/uv/install.sh | sh
   - 然后 AI 自动执行 uv tool install notebooklm-mcp-cli 安装 notebooklm-mcp-cli
   - 然后 AI 自动执行 nlm login 登录谷歌账号
   - 然后，AI 自动执行 nlm setup add 命令给当前 AI Coding 工具设置 MCP Server
- 第二大能力是查询 notebooklm，包括：
  - AI 自动执行 nlm notebook list 查看当前账户可用的 NotebookLM，记住名称中包含“Online Help Bot”关键词的 notebook 的 ID，调用 MCP 的时候首选用这个 notebook 进行查询。命令示例：nlm query notebook 43235141-3c7c-4335-9d19-24d13d6ddcfa "你的问题"
  - 当谷歌 NotebookLM 账户鉴权过期后，给用户明确的操作提示

需要输出：
- 在根目录输出一个 SKILL 文档，按照 AI 行业最新的通用结构和要求进行编写
- 注意 src/notebooklm_tools/data/SKILL.md 这个文件只是参考，你自己根据当前项目总结出 SKILL 文档的内容，不要直接复制或修改这个文件的内容
- 安装 SKILL 的教程文档包括两种模式：
  - 手动安装
  - 通过一条命令直接安装，现在这个仓库是我用自己的 github 账号 fork 原仓库的，注意我想要的不是在本地的脚本，而是执行命令后，能自动从网络上抓取 SKILL 并安装。这个可能要单独开发实现，先讨论可行性和方案
