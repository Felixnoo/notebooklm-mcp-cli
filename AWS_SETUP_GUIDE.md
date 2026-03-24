# AWS 云服务器配置指南

本指南详细说明如何在 AWS 上配置一个 t2.micro 实例，安装 Ubuntu 22.04 LTS，配置 Python 3.11+ 环境，安装项目依赖，并配置网络安全组。

## 1. AWS 控制台操作

### 1.1 登录 AWS 管理控制台
- 访问 [AWS 管理控制台](https://aws.amazon.com/console/)
- 使用您的 AWS 账户登录

### 1.2 启动 EC2 实例
1. 在服务列表中选择 "EC2"
2. 点击 "启动实例"
3. 填写实例配置：
   - **名称**：notebooklm-mcp-server
   - **应用程序和操作系统镜像 (Amazon Machine Image)**：
     - 选择 "Ubuntu"
     - 选择 "Ubuntu Server 22.04 LTS (HVM), SSD Volume Type"
     - 架构：64 位 (x86)
   - **实例类型**：选择 "t2.micro" (2 vCPU, 4GB 内存)
   - **密钥对**：创建或选择现有密钥对（用于 SSH 访问）
   - **网络设置**：
     - VPC：使用默认 VPC
     - 子网：使用默认子网
     - **安全组**：创建新安全组，名称为 "notebooklm-mcp-security-group"
     - **入站规则**：
       - SSH (22)：源 0.0.0.0/0
       - HTTP (80)：源 0.0.0.0/0
       - HTTPS (443)：源 0.0.0.0/0
   - **存储**：使用默认配置 (8GB gp2 根卷)
4. 点击 "启动实例"

## 2. 连接到实例

### 2.1 获取实例公共 IP
- 在 EC2 控制台中，找到您的实例
- 复制公共 IPv4 地址

### 2.2 SSH 连接
```bash
# 使用您的密钥对连接到实例
ssh -i /path/to/your-key.pem ubuntu@<instance-public-ip>
```

## 3. 系统配置

### 3.1 更新系统包
```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2 安装必要的系统依赖
```bash
sudo apt install -y python3-pip python3-venv git curl
```

### 3.3 安装 Python 3.11
Ubuntu 22.04 默认包含 Python 3.10，我们需要安装 Python 3.11：

```bash
# 添加 deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y

# 更新包列表
sudo apt update

# 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 更新 pip
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
sudo update-alternatives --set python3 /usr/bin/python3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3
```

## 4. 项目配置

### 4.1 克隆项目代码
```bash
# 克隆项目
cd ~
git clone https://github.com/jacob-bd/notebooklm-mcp-cli.git
cd notebooklm-mcp-cli
```

### 4.2 创建虚拟环境
```bash
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate
```

### 4.3 安装项目依赖
```bash
# 安装核心依赖
pip install -e .

# 可选：安装开发依赖
# pip install -e .[dev]
```

## 5. 验证安装

### 5.1 检查 Python 版本
```bash
python3 --version
# 输出应为 Python 3.11+ 版本
```

### 5.2 检查 CLI 安装
```bash
nlm --help
# 应显示 CLI 帮助信息
```

### 5.3 检查 MCP 服务器安装
```bash
notebooklm-mcp --help
# 应显示 MCP 服务器帮助信息
```

## 6. 启动 MCP 服务器

### 6.1 启动服务器
```bash
# 在后台启动 MCP 服务器
nohup notebooklm-mcp > mcp-server.log 2>&1 &
```

### 6.2 检查服务器状态
```bash
# 查看服务器日志
cat mcp-server.log

# 检查服务器是否在运行
ps aux | grep notebooklm-mcp
```

## 7. 网络配置验证

### 7.1 检查安全组规则
- 在 EC2 控制台中，选择您的实例
- 点击 "安全" 选项卡
- 确认安全组规则已正确配置（开放 22、80、443 端口）

### 7.2 测试端口访问
```bash
# 测试 SSH 端口
ssh -i /path/to/your-key.pem ubuntu@<instance-public-ip>

# 测试 HTTP 端口
curl http://<instance-public-ip>

# 测试 HTTPS 端口
curl https://<instance-public-ip> --insecure
```

## 8. 维护和监控

### 8.1 设置自动更新
```bash
# 配置自动安全更新
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 8.2 监控实例
- 在 AWS 控制台中，使用 CloudWatch 监控实例性能
- 设置必要的告警以监控 CPU、内存和磁盘使用情况

## 9. 故障排除

### 9.1 常见问题
- **无法连接到实例**：检查安全组规则是否正确配置，确保 SSH 端口 22 对您的 IP 开放
- **依赖安装失败**：确保 Python 版本正确，网络连接正常
- **服务器启动失败**：查看日志文件 `mcp-server.log` 了解详细错误信息

### 9.2 日志位置
- MCP 服务器日志：`~/notebooklm-mcp-cli/mcp-server.log`
- 系统日志：`/var/log/syslog`

## 10. 总结

通过以上步骤，您已成功在 AWS t2.micro 实例上配置了 NotebookLM MCP 服务器环境。服务器现在应该可以正常运行，并通过 HTTP/HTTPS 端口接收请求。

### 后续步骤
- 配置域名和 HTTPS 证书
- 设置持续集成/持续部署 (CI/CD) 流程
- 配置数据库（如果需要）
- 实现监控和告警系统
