<div align="center">

<br/>

```
 ██████╗██████╗ ██╗███████╗ ██████╗    ███╗   ███╗ ██████╗██████╗
██╔════╝██╔══██╗██║██╔════╝██╔════╝    ████╗ ████║██╔════╝██╔══██╗
██║     ██║  ██║██║███████╗██║         ██╔████╔██║██║     ██████╔╝
██║     ██║  ██║██║╚════██║██║         ██║╚██╔╝██║██║     ██╔═══╝
╚██████╗██████╔╝██║███████║╚██████╗    ██║ ╚═╝ ██║╚██████╗██║
 ╚═════╝╚═════╝ ╚═╝╚══════╝ ╚═════╝    ╚═╝     ╚═╝ ╚═════╝╚═╝
```

<br/>

**CDISC Library MCP 服务器** — 让 AI 助手直接查询临床数据标准（SDTM、ADaM、CDASH、CT）。

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-latest-FF6B35?style=flat-square)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](../LICENSE)
[![测试覆盖率](https://img.shields.io/badge/覆盖率-80%25%2B-22C55E?style=flat-square)](../tests/)

<br/>

**🌐 语言切换：** [English README](../README.md) · [日本語 README](README.ja.md)

<br/>

</div>

---

## 这是什么？

**CDISC MCP 服务器**将 AI 助手（Claude、VS Code Copilot、Cursor 等）与 [CDISC Library REST API](https://library.cdisc.org) 连接起来，提供 11 个结构化工具用于查询临床试验数据标准。

你可以直接向 AI 助手提问：

> *"SDTM AE 数据域有哪些变量？"*
> *"列出 ADaM IG 1.3 中 ADSL 的所有变量"*
> *"有哪些可用的受控术语包？"*

完整配置指南请参阅 **[用户手册 →](user-manual.md)**

---

## 快速开始

### 第一步：获取 CDISC Library API 密钥

在 **https://library.cdisc.org** 注册并获取个人 API 密钥。

### 第二步：安装

```bash
# 仅运行时依赖
pip install -e .

# 含开发依赖
pip install -e ".[dev]"

# 含 Web 探索器依赖
pip install -e ".[web]"
```

### 第三步：配置 API 密钥

```bash
# Linux / macOS
export CDISC_API_KEY=你的密钥

# Windows — 命令提示符
set CDISC_API_KEY=你的密钥

# Windows — PowerShell
$env:CDISC_API_KEY = "你的密钥"
```

### 第四步：启动

```bash
# 启动 MCP 服务器（用于 AI 助手集成）
cdisc-mcp

# 或者：启动 Web 探索器（快速交互测试）
python web/app.py
```

---

## Web 探索器 — 快速交互测试

无需任何 AI 客户端即可验证配置和探索工具的最快方式。

```bash
# 1. 安装 Web 依赖
pip install -e ".[web]"

# 2. 设置 API 密钥
export CDISC_API_KEY=你的密钥        # Linux/macOS
set CDISC_API_KEY=你的密钥           # Windows CMD
$env:CDISC_API_KEY = "你的密钥"      # Windows PowerShell

# 3. 启动服务器
python web/app.py

# 4. 在浏览器中打开
#    → http://localhost:8080
```

Web 探索器功能：
- **侧边栏导航** — 按标准分类的 11 个工具（SDTM / ADaM / CDASH / 术语）
- **自动生成表单** — 版本和域名的下拉菜单，变量名称的文本输入框
- **实时 JSON 响应** — 语法高亮、可复制的输出，显示响应时间
- **连接状态指示器** — 确认 API 密钥和连接状态

> **提示：** 版本号使用连字符格式——`3-4` 而非 `3.4`，`1-3` 而非 `1.3`。
> 示例：SDTM-IG `3-4`，ADaM-IG `1-3`，CDASH-IG `2-0`

---

## 可用工具

| # | 工具名称 | 标准 | 功能描述 |
|---|---------|------|---------|
| 1 | `list_products` | — | 列出所有可用的 CDISC 标准及其发布版本 |
| 2 | `get_sdtm_domains` | SDTM | 列出指定 SDTM-IG 版本的所有数据集 |
| 3 | `get_sdtm_domain_variables` | SDTM | 列出某 SDTM 域/数据集的所有变量 |
| 4 | `get_sdtm_variable` | SDTM | 获取特定 SDTM 变量的完整定义 |
| 5 | `get_adam_datastructures` | ADaM | 列出指定 ADaM-IG 版本的所有数据结构 |
| 6 | `get_adam_variable` | ADaM | 获取特定 ADaM 变量的定义 |
| 7 | `get_cdash_domains` | CDASH | 列出指定 CDASH-IG 版本的所有域 |
| 8 | `get_cdash_domain_fields` | CDASH | 获取某 CDASH 域的所有数据采集字段 |
| 9 | `list_ct_packages` | CT | 列出所有可用的受控术语包 |
| 10 | `get_codelist` | CT | 获取 CT 代码列表的定义和元数据 |
| 11 | `get_codelist_terms` | CT | 列出 CT 代码列表中的所有有效术语 |

### 版本参考

| 标准 | 可用版本（使用连字符） |
|------|----------------------|
| SDTM-IG | `3-4` · `3-3` · `3-2` · `3-1-3` |
| ADaM-IG | `1-3` · `1-2` · `1-1` · `1-0` |
| CDASH-IG | `2-1` · `2-0` · `1-1-1` |

---

## 连接 AI 助手

### Claude Desktop

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "cdisc": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "你的密钥"
      }
    }
  }
}
```

### VS Code / Cursor

在 `.vscode/mcp.json` 或对应的 MCP 配置中添加：

```json
{
  "servers": {
    "cdisc": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "你的密钥"
      }
    }
  }
}
```

### Claude Code (CLI)

Claude Code 支持在两个范围内配置 MCP 服务器：**用户** (全局级别，适用于所有项目) 与 **项目** (本地级别，仅限当前项目)。

**选项 A — 命令行方式 (推荐)**

```bash
# 全局添加 (适用于所有项目)
claude mcp add cdisc-mcp -e CDISC_API_KEY=你的密钥 -- python -m cdisc_mcp.server

# 仅在当前项目中添加
claude mcp add cdisc-mcp --scope project -e CDISC_API_KEY=你的密钥 -- python -m cdisc_mcp.server

# 确认服务器是否已成功注册
claude mcp list
```

**选项 B — 直接编辑 `~/.claude.json`**

```json
{
  "mcpServers": {
    "cdisc-mcp": {
      "command": "python",
      "args": ["-m", "cdisc_mcp.server"],
      "env": {
        "CDISC_API_KEY": "你的密钥"
      }
    }
  }
}
```

> **提示：** 如果 `CDISC_API_KEY` 已经存在于你的系统环境变量中，可以完全省略 `env` 块——Claude Code 会自动继承。

注册完成后，在任意 Claude Code 会话中输入 `/mcp` 确认状态，然后就可以对话方式使用这些工具了：

```
提问: SDTM 版本 3.4 定义了哪些数据域?
Claude: [自动调用带有 version="3-4" 参数的 get_sdtm_domains 接口] ...
```

---

## 在你开发的 Python 工具中集成

通过官方提供的 MCP 客户端库 (SDK)，你可以在任何 Python 脚本中通过编程方式调用 CDISC MCP 工具。

### 安装客户端库

```bash
pip install mcp
```

### 极简示例

```python
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command="python",
    args=["-m", "cdisc_mcp.server"],
    env={"CDISC_API_KEY": os.environ["CDISC_API_KEY"]},
)

async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 列出所有可用的工具
            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            # 执行工具调用
            result = await session.call_tool(
                "get_sdtm_domains",
                arguments={"version": "3-4"},
            )
            print(result.content[0].text)

asyncio.run(main())
```

### 可复用封装示例

```python
import asyncio, os, json
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_SERVER = StdioServerParameters(
    command="python",
    args=["-m", "cdisc_mcp.server"],
    env={"CDISC_API_KEY": os.environ["CDISC_API_KEY"]},
)

@asynccontextmanager
async def cdisc_session():
    """创建一个异步上下文管理器，返回已初始化的 MCP 会话。"""
    async with stdio_client(_SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

async def call(tool: str, **kwargs) -> dict:
    async with cdisc_session() as s:
        result = await s.call_tool(tool, arguments=kwargs)
        return json.loads(result.content[0].text)

# --- 实战演示 ---
async def demo():
    # 获取 SDTM 数据域
    domains = await call("get_sdtm_domains", version="3-4")

    # 获取 AE (不良事件) 域下包含的所有变量
    variables = await call("get_sdtm_domain_variables", version="3-4", domain="AE")

    # 单独查询不良事件分类术语 (AETERM) 的定义
    aeterm = await call("get_sdtm_variable", version="3-4", domain="AE", variable="AETERM")

    print(aeterm)

asyncio.run(demo())
```

### 工具调用签名速查

```python
# 产品 / 版本查询
await session.call_tool("list_products", {})

# SDTM (研究数据列表模型) 相关
await session.call_tool("get_sdtm_domains",          {"version": "3-4"})
await session.call_tool("get_sdtm_domain_variables", {"version": "3-4", "domain": "AE"})
await session.call_tool("get_sdtm_variable",         {"version": "3-4", "domain": "AE", "variable": "AETERM"})

# ADaM (分析数据集模型) 相关
await session.call_tool("get_adam_datastructures",   {"version": "1-3"})
await session.call_tool("get_adam_variable",         {"version": "1-3", "data_structure": "ADSL", "variable": "USUBJID"})

# CDASH (临床数据收集标准) 相关
await session.call_tool("get_cdash_domains",         {"version": "2-0"})
await session.call_tool("get_cdash_domain_fields",   {"version": "2-0", "domain": "AE"})

# Controlled Terminology (受控术语体系) 相关
await session.call_tool("list_ct_packages",          {})
await session.call_tool("get_codelist",              {"package_id": "sdtmct-2024-03-29", "codelist_id": "C66781"})
await session.call_tool("get_codelist_terms",        {"package_id": "sdtmct-2024-03-29", "codelist_id": "AGEU"})
```

> **要求：** 版本的表示必须使用连字符 (破折号) 而不是点号进行分割 — 即应为 `"3-4"` 而不可写作 `"3.4"`。

---

## 系统架构

```
MCP 客户端（Claude / VS Code / Cursor）
        │
        │  MCP 协议（stdio）
        ▼
   server.py  ──── FastMCP 工具注册
        │
        ▼
   tools/  ──────── 领域函数（sdtm、adam、cdash、terminology、search）
        │
        ▼
   client.py  ───── CDISCClient（异步 HTTP · TTL 缓存 · 重试）
        │
        │  HTTPS
        ▼
   library.cdisc.org/api  ──── CDISC Library REST API
```

**关键设计决策：**
- `CDISCClient` 是带 1 小时 TTL 内存缓存的单例异步 HTTP 客户端
- 仅重试 `429` 和 `5xx` 响应；`4xx` 立即抛出异常
- 工具函数为纯异步函数——无需 Mock 即可独立测试
- `format_response()` 去除 HAL `_links` 元数据，提取 LLM 可用的结构化数据

---

## 开发

### 运行测试

```bash
# 带覆盖率的完整测试（≥80% 要求）
pytest

# 指定模块
pytest tests/test_tools.py tests/test_client.py -v
```

### 代码质量

```bash
ruff check src/ tests/    # 代码检查
mypy src/                 # 类型检查
```

---

## 许可证

MIT — 详见 [LICENSE](../LICENSE)

---

<div align="center">

专为使用 CDISC 标准的临床数据专业人员构建。

**[用户手册](user-manual.md)** · **[CDISC Library](https://library.cdisc.org)** · **[API 文档](https://www.cdisc.org/cdisc-library/api-documentation)**

</div>
