# CDISC MCP Server — User Manual

## Table of Contents

1. [What Is This?](#1-what-is-this)
2. [What Is MCP?](#2-what-is-mcp)
3. [Prerequisites](#3-prerequisites)
4. [Installation](#4-installation)
5. [Getting Your CDISC API Key](#5-getting-your-cdisc-api-key)
6. [Connecting to an AI Assistant](#6-connecting-to-an-ai-assistant)
   - [Claude Desktop](#61-claude-desktop)
   - [VS Code with Claude Extension](#62-vs-code-with-claude-extension)
   - [Other MCP-Compatible Clients](#63-other-mcp-compatible-clients)
7. [Available Tools Reference](#7-available-tools-reference)
8. [Typical Usage Workflows](#8-typical-usage-workflows)
9. [Understanding the Response Format](#9-understanding-the-response-format)
10. [Errors and Troubleshooting](#10-errors-and-troubleshooting)

---

## 1. What Is This?

**cdisc-mcp** is a bridge between an AI assistant (such as Claude) and the
[CDISC Library](https://library.cdisc.org) — the official, machine-readable
repository of clinical data standards published by CDISC.

Without this server, an AI assistant has only its training-time knowledge of
CDISC standards, which may be out of date. With this server running, the AI
can call into the live CDISC Library API in real time to look up:

- SDTM domain definitions and variable specifications
- ADaM data structure and variable definitions
- CDASH data collection domains and fields
- Controlled Terminology (CT) codelists and valid terms

All of this happens automatically in the background — as a user you simply
ask questions in natural language and the AI handles the tool calls.

---

## 2. What Is MCP?

**MCP (Model Context Protocol)** is an open standard that lets AI assistants
call external tools and data sources in a structured, safe way. Think of it
as a plug-in system for AI:

```
You (natural language)
       │
       ▼
  AI Assistant  ◄──── decides which tool to call
       │
       ▼
  cdisc-mcp  ◄──── this server, running locally on your machine
       │
       ▼
  CDISC Library API  ◄──── official CDISC standards data
```

The server runs as a local process on your computer. The AI client (Claude
Desktop, VS Code, etc.) communicates with it over a private channel — no
data leaves your machine except for the CDISC Library API calls themselves.

You do **not** interact with the server directly. You talk to the AI in plain
language and it uses the server whenever it needs CDISC data.

---

## 3. Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11 or later | `python --version` to check |
| pip | any recent | bundled with Python |
| CDISC Library account | — | Free registration at library.cdisc.org |
| MCP-compatible AI client | — | Claude Desktop, VS Code, etc. |

---

## 4. Installation

Open a terminal and run:

```bash
# 1. Clone or download the project
git clone https://github.com/your-org/cdisc-mcp.git
cd cdisc-mcp

# 2. Install the package
pip install -e .
```

Verify the installation succeeded:

```bash
cdisc-mcp --help
```

You should see a short help message. If you see `command not found`, make
sure Python's `Scripts` folder is on your PATH.

---

## 5. Getting Your CDISC API Key

1. Go to [https://library.cdisc.org](https://library.cdisc.org).
2. Click **Sign In / Register** and create a free account (or log in if you
   already have one).
3. After logging in, navigate to **My Account → API Key**.
4. Copy the key — it looks like a long alphanumeric string.

Set the key as an environment variable **before** starting the server or
configuring your AI client:

**Windows (Command Prompt)**
```cmd
set CDISC_API_KEY=your_key_here
```

**Windows (PowerShell)**
```powershell
$env:CDISC_API_KEY = "your_key_here"
```

**Linux / macOS**
```bash
export CDISC_API_KEY=your_key_here
```

> **Tip:** Add this line to your shell profile (`~/.bashrc`, `~/.zshrc`, or
> your PowerShell profile) so it is set automatically on every session.

---

## 6. Connecting to an AI Assistant

### 6.1 Claude Desktop

Claude Desktop reads its MCP server list from a JSON configuration file.

**Location of the config file:**

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

Open (or create) that file and add the following block inside the top-level
`mcpServers` object. If the file does not exist yet, create it with the full
content shown below.

```json
{
  "mcpServers": {
    "cdisc": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "your_key_here"
      }
    }
  }
}
```

Replace `"your_key_here"` with your actual key.

**Save the file and restart Claude Desktop.** You should see a small plug icon
or a "Tools" indicator in the chat window confirming the server is connected.

> **Alternative:** If `cdisc-mcp` is not on your PATH, use the full path to
> the executable, e.g. `"C:\\Python311\\Scripts\\cdisc-mcp.exe"` on Windows.

---

### 6.2 VS Code with Claude Extension

Open your VS Code `settings.json` (Ctrl+Shift+P → "Open User Settings (JSON)")
and add:

```json
{
  "claude.mcpServers": {
    "cdisc": {
      "command": "cdisc-mcp",
      "env": {
        "CDISC_API_KEY": "your_key_here"
      }
    }
  }
}
```

Reload the window (Ctrl+Shift+P → "Reload Window") to pick up the change.

---

### 6.3 Other MCP-Compatible Clients

Any MCP client that launches servers via a subprocess command will work.
The server is started with:

```
cdisc-mcp
```

and it communicates over **stdio** (standard input/output), which is the
default MCP transport. Provide `CDISC_API_KEY` as an environment variable
to the process.

---

## 7. Available Tools Reference

The server exposes 12 tools. You never call them by name — the AI selects
the right tool automatically — but knowing what they do helps you ask the
right questions.

### Discovery tools

#### `list_products`
Lists all CDISC standards available in the Library, with their published
version numbers.

**When to trigger it:** Ask the AI *"What CDISC standards are available?"*
or *"What are the current SDTM versions?"*

---

#### `search_cdisc`
Full-text search across all standards — variable names, labels, descriptions,
and CT terms.

**Parameters:**
- `query` — keyword or phrase, e.g. `"adverse event"`, `"AEDECOD"`, `"body weight"`

**When to trigger it:** Ask *"Search for 'adverse event' across all CDISC standards"*
or *"Find any variable related to body weight."*

---

### SDTM tools

#### `get_sdtm_domains`
Lists all domains defined in a specific SDTM-IG version.

**Parameters:**
- `version` — e.g. `"3.4"`, `"3.3"`

**When to trigger it:** *"List all SDTM domains in version 3.4."*

---

#### `get_sdtm_domain_variables`
Returns all variables defined in a single SDTM domain.

**Parameters:**
- `version` — e.g. `"3.4"`
- `domain` — two-letter code, e.g. `"AE"`, `"DM"`, `"LB"`

**When to trigger it:** *"What variables are in the SDTM AE domain?"*

---

#### `get_sdtm_variable`
Returns the full specification of one SDTM variable — data type, length,
controlled terms, notes, etc.

**Parameters:**
- `version` — e.g. `"3.4"`
- `domain` — e.g. `"AE"`
- `variable` — e.g. `"AETERM"`, `"AEDECOD"`

**When to trigger it:** *"What is the definition of AETERM in SDTM 3.4?"*

---

### ADaM tools

#### `get_adam_datastructures`
Lists all data structures (datasets) defined in an ADaM version.

**Parameters:**
- `version` — e.g. `"1.3"`, `"2.1"`

**When to trigger it:** *"What ADaM data structures exist in version 1.3?"*

---

#### `get_adam_variable`
Returns the definition of one ADaM variable within a specific data structure.

**Parameters:**
- `version` — e.g. `"1.3"`
- `data_structure` — e.g. `"ADSL"`, `"ADAE"`
- `variable` — e.g. `"USUBJID"`, `"AVAL"`

**When to trigger it:** *"What is AVAL in ADaM ADAE?"*

---

### CDASH tools

#### `get_cdash_domains`
Lists all domains in a CDASH version.

**Parameters:**
- `version` — e.g. `"2.0"`, `"1.1"`

**When to trigger it:** *"List CDASH domains for version 2.0."*

---

#### `get_cdash_domain_fields`
Returns all data collection fields in a CDASH domain, including CRF
instructions and mapping guidance.

**Parameters:**
- `version` — e.g. `"2.0"`
- `domain` — e.g. `"DM"`, `"AE"`, `"VS"`

**When to trigger it:** *"Show me the CDASH vital signs fields."*

---

### Controlled Terminology tools

#### `list_ct_packages`
Lists all published CT packages with their release dates and identifiers.

**When to trigger it:** *"What CT packages are available?"* or
*"When was the latest SDTM CT published?"*

---

#### `get_codelist`
Returns the definition and metadata of one codelist (name, concept ID,
submission value, extensibility).

**Parameters:**
- `package_id` — e.g. `"sdtmct-2024-03-29"`
- `codelist_id` — concept ID (`"C66781"`) or submission value (`"AGEU"`)

**When to trigger it:** *"Give me the definition of the AGEU codelist."*

---

#### `get_codelist_terms`
Returns all valid submission values in a codelist (up to 100 shown).

**Parameters:**
- `package_id` — e.g. `"sdtmct-2024-03-29"`
- `codelist_id` — e.g. `"AGEU"`, `"SEX"`

**When to trigger it:** *"What are the valid values for the SEX codelist?"*

> **Note:** If the response contains `"has_more": true`, the codelist has
> more than 100 terms. Ask the AI to paginate or narrow the search.

---

## 8. Typical Usage Workflows

### Workflow A — Exploring a new standard

> "What versions of SDTM are available in the CDISC Library?"

The AI calls `list_products`, reads the versions, then you can follow up:

> "Show me all domains in SDTM 3.4."
> "What variables are in the AE domain?"
> "Give me the full definition of AEDECOD."

---

### Workflow B — Checking variable specifications during dataset build

> "I'm building an SDTM AE dataset. What are the required variables in version 3.4?"

The AI calls `get_sdtm_domain_variables` and filters by required/expected
core status. Follow up with:

> "What controlled terminology does AEOUT use?"

---

### Workflow C — CRF design with CDASH

> "I need to design a vital signs CRF. What fields does CDASH 2.0 define for the VS domain?"

The AI calls `get_cdash_domain_fields` and returns field names, questions to
display, data types, and SDTM mapping guidance.

---

### Workflow D — Finding valid CT terms

> "What are the valid values I can use for AGEU (age unit) in the latest SDTM CT?"

The AI calls `list_ct_packages` to find the latest package, then
`get_codelist_terms` to list the valid submission values.

---

### Workflow E — Cross-standard search

> "Is there any variable related to 'body mass index' across SDTM and ADaM?"

The AI calls `search_cdisc` with query `"body mass index"` and returns
matching results from all standards simultaneously.

---

## 9. Understanding the Response Format

The server normalises CDISC Library API responses before returning them to
the AI. Key things to know:

### HAL links are removed

The CDISC Library API uses HAL (Hypertext Application Language) — every
response includes `_links` blocks with navigation URLs. These are stripped
because they are not useful to an AI and would waste context space.

### Long lists are truncated

Any list with more than 100 items is truncated. A sentinel entry is added
at the end:

```json
{
  "_truncated": true,
  "total_count": 342,
  "message": "Results truncated: showing 99 of 342 items."
}
```

When you see this, ask for a more specific query (e.g. add a domain filter)
to get the data you need.

### Top-level lists are wrapped

When a tool returns a list, it is wrapped in an envelope for easier handling:

```json
{
  "items": [ ... ],
  "total_returned": 42,
  "has_more": false
}
```

---

## 10. Errors and Troubleshooting

### "CDISC_API_KEY environment variable is required"

The server could not find your API key. Make sure you have set the
`CDISC_API_KEY` environment variable in the section of your OS or in the
`"env"` block of the MCP client config (see Section 6). Restart the client
after changing environment variables.

---

### "Invalid CDISC API key (HTTP 401)"

The key was found but rejected by the CDISC Library API. Double-check that
you copied the key correctly with no extra spaces. Log in to
[library.cdisc.org](https://library.cdisc.org) to verify the key is still
active.

---

### "Resource not found" (HTTP 404)

The version number, domain code, or variable name does not exist. Common
causes:

- Typo in the version string — versions are like `"3.4"`, not `"v3.4"`.
- Wrong domain code — SDTM domains are two letters (`"AE"`), not full names
  (`"Adverse Events"`).
- The requested resource genuinely does not exist in that version — use
  `list_products` or `get_sdtm_domains` first to discover valid values.

---

### "Rate limit exceeded"

The CDISC Library API has a rate limit. The server retries automatically with
exponential back-off, but if traffic is too high the error surfaces. Wait a
few seconds and try again. Responses are cached for one hour — repeated
queries for the same resource will not count against the rate limit.

---

### The AI does not seem to use CDISC tools

Check that the server is connected:

1. **Claude Desktop:** Look for a plug icon or "Tools" badge in the chat window.
   If absent, re-check the config file path and JSON syntax, then restart.
2. **VS Code:** Check the Claude extension panel for connected MCP servers.
3. **All clients:** Try running `cdisc-mcp` in a terminal manually. If it
   starts without error and waits for input, the binary is working.

---

### Server crashes immediately on Windows

Ensure `CDISC_API_KEY` is set in the `"env"` block of your MCP client config
(see Section 6). Environment variables set with `set` in a Command Prompt are
not visible to processes launched by the AI client unless passed explicitly
through the config.

---

### Slow first response

The first call to each unique API endpoint fetches live data from the CDISC
Library. Subsequent calls for the same resource return instantly from the
in-memory cache (TTL: 1 hour). This is expected behaviour.
