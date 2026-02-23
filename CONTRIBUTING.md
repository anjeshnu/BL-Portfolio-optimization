# Contributing to Black-Litterman Portfolio Optimization

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/black-litterman-portfolio.git
   cd black-litterman-portfolio
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

## Development Workflow

### 1. Create a Branch

Create a new branch for your feature or bugfix:

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

### 2. Make Changes

- Write clear, commented code
- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Update tests as needed

### 3. Run Tests

Before committing, ensure all tests pass:

```bash
pytest tests/ -v
```

### 4. Format Code

Use black for code formatting:

```bash
black src/ tests/
```

Check with flake8:

```bash
flake8 src/ tests/
```

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: Brief description of changes"
```

Commit message format:
- Use present tense ("Add feature" not "Added feature")
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description if needed

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what was changed and why
- Reference to any related issues

## Code Style Guidelines

### Python

- Follow PEP 8
- Use meaningful variable names
- Maximum line length: 100 characters
- Use type hints where appropriate
- Add docstrings to all public functions and classes

Example docstring format:

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of function.
    
    Parameters
    ----------
    param1 : Type1
        Description of param1
    param2 : Type2
        Description of param2
        
    Returns
    -------
    ReturnType
        Description of return value
        
    Raises
    ------
    ValueError
        When certain conditions are met
    """
    # Implementation
```

### Notebooks

- Clear markdown explanations before code cells
- Remove execution counts before committing
- Include visualization outputs
- Add section headers for organization

## Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Use pytest fixtures for common setups
- Test edge cases and error conditions
- Aim for >80% code coverage

Example test:

```python
def test_function_name():
    """Test that function_name works correctly."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected_output
    assert isinstance(result, ExpectedType)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_black_litterman.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```

## Documentation Guidelines

### Code Documentation

- Add docstrings to all modules, classes, and functions
- Use NumPy-style docstrings
- Include parameter types and return types
- Provide examples in docstrings when helpful

### Markdown Documentation

- Use clear headers and subheaders
- Include code examples
- Add links to related sections
- Keep language clear and concise

## Adding New Features

When adding substantial new features:

1. **Open an issue first** to discuss the feature
2. **Update documentation** in `docs/`
3. **Add tests** for the new functionality
4. **Update README** if the feature affects usage
5. **Add example notebook** demonstrating the feature

## Reporting Bugs

When reporting bugs, include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Minimal code example
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, package versions

## Suggesting Enhancements

Enhancement suggestions should include:

- **Use Case**: Why is this enhancement needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Additional Context**: Any other relevant information

## Code Review Process

All contributions go through code review:

1. Maintainer reviews code for:
   - Correctness
   - Code quality
   - Test coverage
   - Documentation
2. Request changes if needed
3. Once approved, maintainer merges PR

## Community Guidelines

- Be respectful and constructive
- Welcome newcomers
- Focus on the code, not the person
- Assume good intentions
- Help others learn

## Questions?

If you have questions:

- Open an issue for general questions
- Comment on relevant issues for specific questions
- Check existing issues and documentation first

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers this project.

---

Thank you for contributing! 🎉
