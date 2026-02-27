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

**CDISC Library MCP サーバー** — AI アシスタントから臨床データ標準（SDTM、ADaM、CDASH、CT）を直接照会。

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-latest-FF6B35?style=flat-square)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](../LICENSE)
[![テストカバレッジ](https://img.shields.io/badge/カバレッジ-80%25%2B-22C55E?style=flat-square)](../tests/)

<br/>

**🌐 言語切替：** [English README](../README.md) · [中文 README](README.zh.md)

<br/>

</div>

---

## これは何ですか？

**CDISC MCP サーバー**は、AI アシスタント（Claude、VS Code Copilot、Cursor など）を [CDISC Library REST API](https://library.cdisc.org) に接続し、臨床試験データ標準を照会するための 11 個の構造化ツールを提供します。

AI アシスタントに直接質問できます：

> *「SDTM AE ドメインの変数は何ですか？」*
> *「ADaM IG 1.3 の ADSL 変数を一覧表示して」*
> *「利用可能な管理用語パッケージを表示して」*

完全なセットアップ手順については **[ユーザーマニュアル →](user-manual.md)** をご覧ください。

---

## クイックスタート

### ステップ 1：CDISC Library API キーの取得

**https://library.cdisc.org** で登録し、個人用 API キーを取得します。

### ステップ 2：インストール

```bash
# ランタイムのみ
pip install -e .

# 開発依存関係を含む
pip install -e ".[dev]"

# Web エクスプローラー依存関係を含む
pip install -e ".[web]"
```

### ステップ 3：API キーの設定

```bash
# Linux / macOS
export CDISC_API_KEY=あなたのキー

# Windows — コマンドプロンプト
set CDISC_API_KEY=あなたのキー

# Windows — PowerShell
$env:CDISC_API_KEY = "あなたのキー"
```

### ステップ 4：起動

```bash
# MCP サーバーを起動（AI アシスタント統合用）
cdisc-mcp

# または：Web エクスプローラーを起動（インタラクティブなテスト用）
python web/app.py
```

---

## Web エクスプローラー — インタラクティブなクイックテスト

AI クライアントなしで設定を確認し、ツールを探索する最速の方法です。

```bash
# 1. Web 依存関係のインストール
pip install -e ".[web]"

# 2. API キーの設定
export CDISC_API_KEY=あなたのキー      # Linux/macOS
set CDISC_API_KEY=あなたのキー         # Windows CMD
$env:CDISC_API_KEY = "あなたのキー"    # Windows PowerShell

# 3. ブリッジサーバーの起動
python web/app.py

# 4. ブラウザで開く
#    → http://localhost:8080
```

エクスプローラーの機能：
- **サイドバーナビゲーション** — 標準別に整理された 11 個のツール（SDTM / ADaM / CDASH / 用語集）
- **自動生成フォーム** — バージョンとドメインのドロップダウン、変数名のテキスト入力
- **リアルタイム JSON レスポンス** — シンタックスハイライト付き、コピー可能な出力と応答時間表示
- **接続状態インジケーター** — API キーと接続の確認

> **ヒント：** バージョン文字列はハイフン区切りを使用 — `3.4` ではなく `3-4`、`1.3` ではなく `1-3`。
> 例：SDTM-IG `3-4`、ADaM-IG `1-3`、CDASH-IG `2-0`

---

## 利用可能なツール

| # | ツール名 | 標準 | 説明 |
|---|---------|------|------|
| 1 | `list_products` | — | 利用可能なすべての CDISC 標準と公開バージョンを一覧表示 |
| 2 | `get_sdtm_domains` | SDTM | 指定 SDTM-IG バージョンのすべてのデータセットを一覧表示 |
| 3 | `get_sdtm_domain_variables` | SDTM | SDTM ドメイン/データセットのすべての変数を一覧表示 |
| 4 | `get_sdtm_variable` | SDTM | 特定の SDTM 変数の完全な定義を取得 |
| 5 | `get_adam_datastructures` | ADaM | 指定 ADaM-IG バージョンのすべてのデータ構造を一覧表示 |
| 6 | `get_adam_variable` | ADaM | 特定の ADaM 変数の定義を取得 |
| 7 | `get_cdash_domains` | CDASH | 指定 CDASH-IG バージョンのすべてのドメインを一覧表示 |
| 8 | `get_cdash_domain_fields` | CDASH | CDASH ドメインのすべてのデータ収集フィールドを取得 |
| 9 | `list_ct_packages` | CT | 利用可能なすべての管理用語パッケージを一覧表示 |
| 10 | `get_codelist` | CT | CT コードリストの定義とメタデータを取得 |
| 11 | `get_codelist_terms` | CT | CT コードリスト内のすべての有効な用語を一覧表示 |

### バージョン参照

| 標準 | 利用可能なバージョン（ハイフン使用） |
|------|----------------------------------|
| SDTM-IG | `3-4` · `3-3` · `3-2` · `3-1-3` |
| ADaM-IG | `1-3` · `1-2` · `1-1` · `1-0` |
| CDASH-IG | `2-1` · `2-0` · `1-1-1` |

---

## AI アシスタントへの接続

### Claude Desktop

`claude_desktop_config.json` に追加：

```json
{
  "mcpServers": {
    "cdisc": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "あなたのキー"
      }
    }
  }
}
```

### VS Code / Cursor

`.vscode/mcp.json` または対応する MCP 設定に追加：

```json
{
  "servers": {
    "cdisc": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "あなたのキー"
      }
    }
  }
}
```

### Claude Code (CLI)

Claude Code は MCP サーバーを **ユーザー** (グローバル、全プロジェクト対象) と **プロジェクト** (ローカル、現在のプロジェクトのみ) の 2 つのスコープでサポートしています。

**オプション A — CLI コマンド (推奨)**

```bash
# グローバルに追加 (全プロジェクトで利用可能)
claude mcp add cdisc-mcp -e CDISC_API_KEY=あなたのキー -- python -m cdisc_mcp.server

# 現在のプロジェクトのみに追加
claude mcp add cdisc-mcp --scope project -e CDISC_API_KEY=あなたのキー -- python -m cdisc_mcp.server

# サーバーが登録されたか確認
claude mcp list
```

**オプション B — `~/.claude.json` を直接編集**

```json
{
  "mcpServers": {
    "cdisc-mcp": {
      "command": "python",
      "args": ["-m", "cdisc_mcp.server"],
      "env": {
        "CDISC_API_KEY": "あなたのキー"
      }
    }
  }
}
```

> **ヒント：** すでにシステム環境変数に `CDISC_API_KEY` を設定している場合は、`env` ブロックを完全に省略できます。Claude Code は環境変数を自動的に継承します。

登録が完了したら、任意の Claude Code セッションで `/mcp` コマンドを使って状態を確認し、AI との対話形式でツールを利用できます：

```
ユーザー: バージョン 3.4 の SDTM にはどのようなドメインが定義されていますか？
Claude: [自動的に version="3-4" パラメータを使用して get_sdtm_domains を呼び出し] ...
```

---

## 自作の Python ツールでの利用

公式の MCP クライアント SDK を使えば、あらゆる Python スクリプトからプログラム内で CDISC MCP の各ツールを呼び出せます。

### クライアントライブラリのインストール

```bash
pip install mcp
```

### 最小構成のサンプル

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

            # 利用可能なすべてのツールをリストアップ
            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            # ツールの呼び出し
            result = await session.call_tool(
                "get_sdtm_domains",
                arguments={"version": "3-4"},
            )
            print(result.content[0].text)

asyncio.run(main())
```

### 再利用可能なヘルパー関数のサンプル

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
    """初期化済みの MCP セッションを返す非同期コンテキストマネージャー"""
    async with stdio_client(_SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

async def call(tool: str, **kwargs) -> dict:
    async with cdisc_session() as s:
        result = await s.call_tool(tool, arguments=kwargs)
        return json.loads(result.content[0].text)

# --- 使用例 ---
async def demo():
    # SDTM のドメイン一覧を取得
    domains = await call("get_sdtm_domains", version="3-4")

    # AE (有害事象) ドメインに含まれるすべての変数を取得
    variables = await call("get_sdtm_domain_variables", version="3-4", domain="AE")

    # AETERM (有害事象の分類用語) 1つの定義のみを取得
    aeterm = await call("get_sdtm_variable", version="3-4", domain="AE", variable="AETERM")

    print(aeterm)

asyncio.run(demo())
```

### 利用可能なツールの署名 (早見表)

```python
# プロダクト・バージョン情報
await session.call_tool("list_products", {})

# SDTM
await session.call_tool("get_sdtm_domains",          {"version": "3-4"})
await session.call_tool("get_sdtm_domain_variables", {"version": "3-4", "domain": "AE"})
await session.call_tool("get_sdtm_variable",         {"version": "3-4", "domain": "AE", "variable": "AETERM"})

# ADaM
await session.call_tool("get_adam_datastructures",   {"version": "1-3"})
await session.call_tool("get_adam_variable",         {"version": "1-3", "data_structure": "ADSL", "variable": "USUBJID"})

# CDASH
await session.call_tool("get_cdash_domains",         {"version": "2-0"})
await session.call_tool("get_cdash_domain_fields",   {"version": "2-0", "domain": "AE"})

# Controlled Terminology (管理用語)
await session.call_tool("list_ct_packages",          {})
await session.call_tool("get_codelist",              {"package_id": "sdtmct-2024-03-29", "codelist_id": "C66781"})
await session.call_tool("get_codelist_terms",        {"package_id": "sdtmct-2024-03-29", "codelist_id": "AGEU"})
```

> **バージョンの書式指定：** ドット記号は使わず、常に代えてハイフン記号を使用してください (例: `"3.4"` ではなく `"3-4"` と指定)。

---

## アーキテクチャ

```
MCP クライアント（Claude / VS Code / Cursor）
        │
        │  MCP プロトコル（stdio）
        ▼
   server.py  ──── FastMCP ツール登録
        │
        ▼
   tools/  ──────── ドメイン関数（sdtm、adam、cdash、terminology、search）
        │
        ▼
   client.py  ───── CDISCClient（非同期 HTTP · TTL キャッシュ · リトライ）
        │
        │  HTTPS
        ▼
   library.cdisc.org/api  ──── CDISC Library REST API
```

**主要な設計方針：**
- `CDISCClient` は 1 時間 TTL のインメモリキャッシュを持つシングルトン非同期 HTTP クライアント
- `429` と `5xx` レスポンスのみリトライ；`4xx` は即座に例外をスロー
- ツール関数は純粋な非同期関数 — モックなしで独立してテスト可能
- `format_response()` は HAL `_links` メタデータを除去し、LLM が使いやすい構造化データを抽出

---

## 開発

### テストの実行

```bash
# カバレッジ付きの完全なテストスイート（≥80% 必須）
pytest

# 特定のモジュール
pytest tests/test_tools.py tests/test_client.py -v
```

### コード品質

```bash
ruff check src/ tests/    # リンティング
mypy src/                 # 型チェック
```

---

## ライセンス

MIT — [LICENSE](../LICENSE) 参照

---

<div align="center">

CDISC 標準を扱う臨床データ専門家のために構築。

**[ユーザーマニュアル](user-manual.md)** · **[CDISC Library](https://library.cdisc.org)** · **[API ドキュメント](https://www.cdisc.org/cdisc-library/api-documentation)**

</div>
