# Contribution Guidelines

Thank you for your interest in contributing to IceBreaker!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/icebreaker.git`
3. Install dev dependencies: `pip install -e ".[dev]"`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add tests for new functionality
4. Run the test suite: `pytest`
5. Format code: `black icebreaker/ tests/`
6. Lint: `ruff check icebreaker/ tests/`
7. Commit: `git commit -m "Add feature: description"`
8. Push: `git push origin feature/your-feature-name`
9. Open a Pull Request

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions focused and small

## Testing

- All new features must have tests
- Maintain test coverage > 80%
- Use pytest fixtures for common setup

## Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

## Questions?

Open an issue for discussion before major changes.
