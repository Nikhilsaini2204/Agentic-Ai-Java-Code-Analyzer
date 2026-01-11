# Java Code Analyzer 🤖

> **Production-grade agentic AI system for autonomous Java code analysis**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

An intelligent, autonomous AI agent that analyzes Java codebases with human-like reasoning and decision-making capabilities.

## 🌟 Features

- **Truly Agentic**: Makes autonomous decisions about analysis strategy
- **Multi-Tool Integration**: Uses multiple analysis tools intelligently
- **Adaptive Reasoning**: Adjusts approach based on findings
- **Memory System**: Learns patterns across analyses
- **Production-Ready**: Enterprise-grade architecture and error handling
- **Free LLM**: Uses Groq's free Llama 3.3 70B API

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          Agent Brain (LLM)              │
│  - Autonomous decision making           │
│  - Strategic planning                   │
│  - Multi-step reasoning                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Agent Controller                │
│  - Agent loop management                │
│  - Tool orchestration                   │
│  - Memory management                    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│          Tool Ecosystem                 │
│  - Code analysis                        │
│  - Security scanning                    │
│  - Complexity metrics                   │
│  - And more...                          │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Git
- Free Groq API key ([get one here](https://console.groq.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/java-code-analyzer.git
cd java-code-analyzer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install-dev

# Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Verify installation
make check-env
```

### Usage

```bash
# Analyze a Java file
python -m analyzer.cli.main analyze path/to/YourCode.java

# With verbose output
python -m analyzer.cli.main analyze path/to/YourCode.java --verbose

# Or use the Makefile
make run
```

## 📋 Development Commands

```bash
make help              # Show all available commands
make install-dev       # Install development dependencies
make setup             # Complete project setup
make test              # Run all tests
make lint              # Run linting
make format            # Format code
make type-check        # Run type checking
make quality           # Run all quality checks
make clean             # Clean build artifacts
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit         # Unit tests only
make test-integration  # Integration tests only

# Generate coverage report
make coverage
```

## 📦 Project Structure

```
java-code-analyzer/
├── src/analyzer/          # Main package
│   ├── core/             # Agent logic
│   ├── llm/              # LLM integrations
│   ├── tools/            # Analysis tools
│   ├── memory/           # Memory systems
│   └── cli/              # Command-line interface
├── tests/                # Test suite
├── config/               # Configuration
├── docs/                 # Documentation
└── data/                 # Runtime data
```

## 🔧 Configuration

Edit `.env` file or set environment variables:

```bash
# Primary LLM (groq, ollama, claude)
PRIMARY_LLM=groq
GROQ_API_KEY=your_key_here

# Agent settings
MAX_ITERATIONS=15
TIMEOUT_SECONDS=300

# Memory
ENABLE_MEMORY=true
MEMORY_BACKEND=file

# Logging
LOG_LEVEL=INFO
ENABLE_TRACING=true
```

## 🏢 Production Deployment

See [docs/deployment.md](docs/deployment.md) for production deployment guide.

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make quality` to ensure code quality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Powered by [Groq](https://groq.com/) (free Llama 3.3 70B API)
- Built with [Pydantic](https://pydantic.dev/), [Typer](https://typer.tiangolo.com/), and [Rich](https://rich.readthedocs.io/)

## 📧 Contact

- Issues: [GitHub Issues](https://github.com/yourusername/java-code-analyzer/issues)
- Email: nikhilsaini6742@gmail.com

---

**Made with ❤️ by Nikhil Saini**
