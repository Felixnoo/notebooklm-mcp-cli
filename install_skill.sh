#!/bin/bash

# NotebookLM SKILL 安装脚本
echo "=== NotebookLM SKILL 安装脚本 ==="

# 检查是否安装了 uv
echo "检查 uv 是否安装..."
if ! command -v uv &> /dev/null; then
    echo "uv 未安装，开始安装..."
    curl -Ls https://astral.sh/uv/install.sh | sh
    if [ $? -ne 0 ]; then
        echo "uv 安装失败，请手动安装后重试"
        exit 1
    fi
    echo "uv 安装成功"
else
    echo "uv 已安装"
fi

# 安装 notebooklm-mcp-cli
echo "安装 notebooklm-mcp-cli..."
uv tool install notebooklm-mcp-cli
if [ $? -ne 0 ]; then
    echo "notebooklm-mcp-cli 安装失败"
    exit 1
fi
echo "notebooklm-mcp-cli 安装成功"

# 登录谷歌账号
echo "请登录谷歌账号以使用 NotebookLM..."
nlm login
if [ $? -ne 0 ]; then
    echo "登录失败，请手动执行 'nlm login' 后重试"
    exit 1
fi
echo "登录成功"

# 为常用 AI 工具设置 MCP Server
echo "为常用 AI 工具设置 MCP Server..."

# 检测已安装的 AI 工具
detected_tools=()

if command -v claude &> /dev/null; then
    detected_tools+=("Claude Code")
fi

if command -v gemini &> /dev/null; then
    detected_tools+=("Gemini")
fi

if command -v cursor &> /dev/null; then
    detected_tools+=("Cursor")
fi

if command -v cline &> /dev/null; then
    detected_tools+=("Cline")
fi

if command -v antigravity &> /dev/null; then
    detected_tools+=("Antigravity")
fi

# 显示检测结果
if [ ${#detected_tools[@]} -eq 0 ]; then
    echo "未检测到任何支持的 AI 工具，跳过设置"
else
    echo "检测到以下 AI 工具："
    for i in "${!detected_tools[@]}"; do
        echo "$((i+1)). ${detected_tools[$i]}"
    done
    
    # 让用户选择要设置的工具
    echo "请选择要设置 MCP Server 的工具（输入数字，多个数字用空格分隔，全部设置输入 'all'）："
    read -r user_input
    
    if [ "$user_input" == "all" ]; then
        # 设置所有检测到的工具
        for tool in "${detected_tools[@]}"; do
            case "$tool" in
                "Claude Code")
                    echo "设置 Claude Code..."
                    nlm setup add claude-code || echo "Claude Code 设置失败，跳过"
                    ;;
                "Gemini")
                    echo "设置 Gemini..."
                    nlm setup add gemini || echo "Gemini 设置失败，跳过"
                    ;;
                "Cursor")
                    echo "设置 Cursor..."
                    nlm setup add cursor || echo "Cursor 设置失败，跳过"
                    ;;
                "Cline")
                    echo "设置 Cline..."
                    nlm setup add cline || echo "Cline 设置失败，跳过"
                    ;;
                "Antigravity")
                    echo "设置 Antigravity..."
                    nlm setup add antigravity || echo "Antigravity 设置失败，跳过"
                    ;;
            esac
        done
    else
        # 设置用户选择的工具
        for num in $user_input; do
            if [ "$num" -ge 1 ] && [ "$num" -le ${#detected_tools[@]} ]; then
                tool=${detected_tools[$((num-1))]}
                case "$tool" in
                    "Claude Code")
                        echo "设置 Claude Code..."
                        nlm setup add claude-code || echo "Claude Code 设置失败，跳过"
                        ;;
                    "Gemini")
                        echo "设置 Gemini..."
                        nlm setup add gemini || echo "Gemini 设置失败，跳过"
                        ;;
                    "Cursor")
                        echo "设置 Cursor..."
                        nlm setup add cursor || echo "Cursor 设置失败，跳过"
                        ;;
                    "Cline")
                        echo "设置 Cline..."
                        nlm setup add cline || echo "Cline 设置失败，跳过"
                        ;;
                    "Antigravity")
                        echo "设置 Antigravity..."
                        nlm setup add antigravity || echo "Antigravity 设置失败，跳过"
                        ;;
                esac
            fi
        done
    fi
fi

echo "=== 安装完成 ==="
echo "现在你可以在 AI 工具中使用 NotebookLM SKILL 了！"
echo "使用方法：向 AI 工具提问时，它会自动使用 NotebookLM 进行查询"
