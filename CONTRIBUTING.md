# Contributing to Jnana

Thank you for your interest in contributing to Jnana! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/[your-username]/Jnana.git
   cd Jnana
   ```

2. **Set up development environment**
   ```bash
   ./scripts/install.sh
   source venv/bin/activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Configure pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Code Style

We use the following tools for code quality:

- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking
- **pytest** for testing

Run all checks:
```bash
# Format code
black jnana/ tests/ examples/
isort jnana/ tests/ examples/

# Type checking
mypy jnana/

# Run tests
pytest tests/ -v
```

### Testing

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names and docstrings
- Test both success and failure cases

Example test structure:
```python
def test_feature_name():
    """Test that feature works correctly under normal conditions."""
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result.expected_property == expected_value
```

### Documentation

- Update docstrings for all public functions and classes
- Follow Google-style docstring format
- Update README.md for user-facing changes
- Add examples for new features

### Commit Messages

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:
```
feat(core): add hybrid processing mode
fix(data): resolve hypothesis serialization issue
docs(integration): update Wisteria integration guide
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run the test suite**
   ```bash
   pytest tests/ -v
   black --check jnana/ tests/
   isort --check-only jnana/ tests/
   mypy jnana/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(component): add new feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots for UI changes
   - Ensure all CI checks pass

## Issue Reporting

When reporting issues, please include:

- **Environment information**
  - Python version
  - Operating system
  - Jnana version
  - Relevant dependencies

- **Steps to reproduce**
  - Minimal code example
  - Expected behavior
  - Actual behavior
  - Error messages/logs

- **Additional context**
  - Configuration files (with API keys removed)
  - Screenshots if applicable

## Feature Requests

For feature requests, please:

1. Check existing issues to avoid duplicates
2. Provide a clear use case
3. Describe the proposed solution
4. Consider implementation complexity
5. Discuss potential alternatives

## Code Review Guidelines

### For Contributors

- Keep PRs focused and reasonably sized
- Respond to feedback promptly
- Be open to suggestions and changes
- Test your changes thoroughly

### For Reviewers

- Be constructive and respectful
- Focus on code quality and maintainability
- Check for proper testing
- Verify documentation updates
- Consider performance implications

## Architecture Guidelines

### Core Principles

1. **Modularity**: Keep components loosely coupled
2. **Extensibility**: Design for future enhancements
3. **Compatibility**: Maintain backward compatibility
4. **Performance**: Consider scalability implications
5. **Usability**: Prioritize user experience

### Integration Patterns

When adding new integrations:

1. Use the event system for communication
2. Follow the unified data model
3. Provide configuration options
4. Include comprehensive tests
5. Document integration points

### Error Handling

- Use appropriate exception types
- Provide helpful error messages
- Log errors with sufficient context
- Handle edge cases gracefully
- Fail fast when appropriate

## Release Process

1. **Version Bumping**
   - Follow semantic versioning (MAJOR.MINOR.PATCH)
   - Update version in `setup.py` and `__init__.py`

2. **Changelog**
   - Update CHANGELOG.md with new features and fixes
   - Group changes by type (Added, Changed, Fixed, etc.)

3. **Testing**
   - Run full test suite
   - Test installation process
   - Verify examples work correctly

4. **Documentation**
   - Update README if needed
   - Refresh integration guides
   - Check all links and references

## Community Guidelines

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Provide constructive feedback
- Follow the code of conduct

## Getting Help

- **Documentation**: Check the docs/ directory
- **Examples**: See examples/ for usage patterns
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Jnana! 🧠✨
