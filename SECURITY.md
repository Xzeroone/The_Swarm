# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it privately:

- Open a [Security Advisory](https://github.com/Xzeroone/The_Swarm/security/advisories/new)

Please do not open a public issue for security vulnerabilities.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| main    | ✅        |

## Security Considerations

### Code Execution

The Swarm executes generated Python code in a sandboxed environment:
- **Workspace isolation**: All file operations restricted to `./agent_workspace/`
- **Dangerous patterns blocked**: `eval()`, `exec()`, `os.system()`, etc.
- **Execution timeout**: 15 second hard limit
- **No network access**: Skills cannot make HTTP requests (by design)

### Local-Only Operation

- **No external API calls**: Works entirely offline after model download
- **No telemetry**: We don't collect or send any data
- **No cloud sync**: All data stays on your machine

### Best Practices

1. Review generated code in `agent_workspace/skills/` before using in production
2. Don't store sensitive information in memory files
3. Run with least-privilege user account
4. Regularly update Ollama and models

## Known Limitations

- **Single-file skills**: Each skill must be self-contained
- **No system commands**: Cannot execute shell commands
- **No network access**: By design for security
