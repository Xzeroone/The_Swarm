# Contributing to The Swarm

Thanks for your interest in contributing!

## Quick Start

1. Fork the repo
2. Clone: `git clone https://github.com/YOUR_USERNAME/The_Swarm.git`
3. Create venv: `python3 -m venv venv && source venv/bin/activate`
4. Install deps: `pip install -r requirements.txt`
5. Pull model: `ollama pull qwen2.5-coder:3b`
6. Test: `python3 autonomous_agent.py -d "Create a hello function"`

## Ways to Contribute

- **Bug fixes** - Check [Issues](https://github.com/Xzeroone/The_Swarm/issues)
- **New features** - Propose in Discussions first
- **Model support** - Add support for new Ollama models
- **Documentation** - Improve guides, add examples
- **Testing** - Add test cases for edge conditions

## Code Style

- Python: PEP 8, type hints preferred
- Bash: Follow [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- Comments: Explain "why", not "what"

## Pull Request Process

1. Update relevant documentation
2. Test your changes: `python3 autonomous_agent.py -d "test directive"`
3. Keep PRs focused (one feature/fix per PR)
4. Link related issues

## Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests (if available)
python3 test_agent.py

# Run example usage
python3 example_usage.py
```

## Roadmap

Check [ROADMAP.md](ROADMAP.md) for planned features.

## Questions?

Open a [Discussion](https://github.com/Xzeroone/The_Swarm/discussions) for questions or ideas.
