# Contributing to VSS Integration System

Thank you for your interest in contributing to VSS Integration System! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic understanding of Vietnamese social security system

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/lalala1.git
   cd lalala1
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements_v3.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for all public functions
- Keep functions small and focused

### Commit Messages
Use conventional commits format:
```
feat: add new VSS data extraction feature
fix: resolve API timeout issue
docs: update deployment guide
test: add unit tests for data validator
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   pytest tests/ -v --cov=src
   flake8 src/
   mypy src/
   ```

4. **Submit Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all tests pass

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_processor.py -v
```

### Writing Tests
- Write unit tests for all new functions
- Use descriptive test names
- Test both success and failure cases
- Mock external API calls

Example:
```python
def test_process_mst_success():
    """Test successful MST processing"""
    processor = CompleteVSSIntegrationProcessor()
    result = await processor.process_complete_enterprise_vss_data("5200958920")
    assert result.is_successful
    assert result.total_employees > 0
```

## 📚 Documentation

### Code Documentation
- Use docstrings for all public functions
- Include type hints
- Provide usage examples

### User Documentation
- Update README.md for new features
- Add deployment instructions
- Include troubleshooting guides

## 🐛 Bug Reports

When reporting bugs, please include:
- OS and Python version
- VSS System version
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs

## 💡 Feature Requests

For feature requests:
- Describe the use case
- Explain expected behavior
- Consider backwards compatibility
- Provide implementation ideas if possible

## 🔒 Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Report security issues privately
- Follow secure coding practices

## 📞 Getting Help

- Check existing issues and discussions
- Join our community discussions
- Contact maintainers for urgent issues

## 🏆 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to VSS Integration System! 🎉
