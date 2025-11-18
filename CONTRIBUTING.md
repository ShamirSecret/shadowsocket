# Contributing to Shadowsocks Server V3

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShamirSecret/shadowsocket.git
   cd shadowsocket
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m shadowsocks_server_ui
   ```

## Project Structure

- `shadowsocks_server_ui/` - Main application code
- `scripts/` - Build and utility scripts
- `docs/` - Documentation
- `.github/workflows/` - CI/CD workflows

## Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and small

## Testing

Before submitting a pull request:

1. Test your changes locally
2. Ensure all imports work correctly
3. Test on both Windows and macOS if possible
4. Verify GUI functionality

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 50 characters
- Add more details in the body if needed

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages (if any)

## Questions?

Feel free to open an issue for questions or discussions.

