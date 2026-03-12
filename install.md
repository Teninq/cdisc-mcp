# cdisc-mcp Auto-Install Guide

> **AI Assistant:** You have been asked to install the `cdisc-mcp` MCP server for this user.
> Follow the steps below sequentially. Ask the user for any missing information marked **[ASK]**.

## Prerequisites Check

1. Verify Python ≥ 3.11 is installed:
   ```bash
   python --version
   ```
   If missing, tell the user to install Python 3.11+ from https://python.org before continuing.

2. Verify `pip` is available:
   ```bash
   pip --version
   ```

## Step 1 · Get CDISC Library API Key

**[ASK]** Does the user already have a CDISC Library API key?
- **Yes** → proceed to Step 2, ask them to provide the key.
- **No** → instruct them to register at https://library.cdisc.org (free account), then return here with the key.

Store the key as: `CDISC_API_KEY=<their_key>`

## Step 2 · Clone or locate the repository

**[ASK]** Has the user already cloned the repository?
- **Yes** → ask for the local path and `cd` into it.
- **No** → clone it:
  ```bash
  git clone https://github.com/Teninq/cdisc-mcp.git
  cd cdisc-mcp
  ```

## Step 3 · Install the package

```bash
pip install -e .
```

Verify install succeeded:
```bash
cdisc-mcp --help
```
Expected output: usage / help text. If this fails, run `pip install -e .` again and check for errors.

## Step 4 · Register with AI assistant

**[ASK]** Which AI assistant does the user want to connect?
- **A** Claude Code (CLI) — most common
- **B** Claude Desktop
- **C** VS Code / Cursor

### Option A — Claude Code (CLI)

**[ASK]** Global (all projects) or project-only scope?
- **Global:**
  ```bash
  claude mcp add cdisc-mcp -e CDISC_API_KEY=<key> -- python -m cdisc_mcp.server
  ```
- **Project-only:**
  ```bash
  claude mcp add cdisc-mcp --scope project -e CDISC_API_KEY=<key> -- python -m cdisc_mcp.server
  ```

Verify:
```bash
claude mcp list
```
Expected: `cdisc-mcp` appears in the list.

### Option B — Claude Desktop

Locate or create `claude_desktop_config.json`:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add or merge the following into `mcpServers`:
```json
{
  "mcpServers": {
    "cdisc-mcp": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "<key>"
      }
    }
  }
}
```

Restart Claude Desktop to pick up changes.

### Option C — VS Code / Cursor

Create or edit `.vscode/mcp.json` in your project root:
```json
{
  "servers": {
    "cdisc-mcp": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "<key>"
      }
    }
  }
}
```

Reload VS Code / Cursor.

## Step 5 · Verify end-to-end

Ask the AI assistant (or test with the web explorer):

> "Use the cdisc-mcp tool to list all available CDISC products."

Expected: a list of SDTM, ADaM, CDASH, and CT standards with version numbers.

**Web Explorer (optional quick check):**
```bash
pip install -e ".[web]"
# Set CDISC_API_KEY in your environment first
python web/app.py
# Open http://localhost:8080
```

## Done!

The `cdisc-mcp` server is now installed and connected. You can query clinical data standards (SDTM, ADaM, CDASH, Controlled Terminology) directly from your AI assistant.

For full documentation, see: https://github.com/Teninq/cdisc-mcp
