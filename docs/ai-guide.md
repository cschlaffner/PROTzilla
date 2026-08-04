# AI Guide

PROTzilla provides two ways to work with its AI tools:

1. the integrated AI assistant in the PROTzilla interface,
2. an external AI client, such as Claude or Codex, connected through the PROTzilla Model Context Protocol (MCP) server.

Both options use the same PROTzilla MCP tools and can inspect or modify the same runs, workflows, and steps. The main difference is how the AI client plans a task and coordinates repeated tool calls.

## Choosing an AI Client

### Integrated AI Assistant

The integrated assistant is the quickest option to set up. It is suitable for questions, explanations, inspecting a run, and smaller or clearly defined changes. No separate AI application is required.

Setup only requires:

1. an API key from a supported AI provider,
2. a provider selected in the PROTzilla settings,
3. a model selected for that provider.

### Claude or Codex through MCP

Claude and Codex require a separate installation and MCP configuration. Their more mature agent environments, tool loops, and context-handling features can make them better suited to long, complex, or highly autonomous tasks.

They do not receive additional PROTzilla tools. They use the same MCP server as the integrated assistant, but may plan and verify multi-step tasks more effectively.

## Available PROTzilla Capabilities

Depending on the task, an AI client can use PROTzilla tools to:

- explain available steps and their definitions,
- inspect saved workflows and existing runs,
- create and configure runs,
- add, connect, rename, and remove steps,
- set step parameters and input files,
- calculate individual steps or complete runs,
- inspect tables, images, and other result artifacts,
- create and configure Custom Python Steps.

Requests should describe the desired result, relevant input files, important parameters, and how the result should be verified. Complex tasks are more reliable when they include clear completion criteria.

[TODO: Paper Reproduction example]

## Setting Up the Integrated AI Assistant

Open the PROTzilla settings and select **AI**.

1. Select an AI provider.
2. Select a model offered for that provider.
3. Enter a valid API key.
4. Save the settings.

The available providers and models are supplied through LiteLLM. API usage and billing are handled by the selected provider.

Open the assistant using the chat button in the PROTzilla navigation bar.

## Setting Up Claude Code

Start PROTzilla, then register its local MCP server:

```bash
claude mcp add --scope user --transport http protzilla http://127.0.0.1:5175/mcp
```

Use `claude mcp list` to verify the connection. This command configures Claude Code, not Claude Desktop. See the [Claude Desktop guide](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop) for its separate local extension setup.

## Setting Up Codex

The PROTzilla repository already contains the required Codex MCP configuration.
Start PROTzilla and open its repository in Codex. After the project is trusted,
Codex connects to `http://127.0.0.1:5175/mcp` automatically.

Users of the optional Codex CLI can register the same server with:

```bash
codex mcp add protzilla --url http://127.0.0.1:5175/mcp
```

Use `codex mcp list` to verify the connection. See the current [Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp) for further details.
