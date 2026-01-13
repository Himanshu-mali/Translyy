# Contributing to FastAPI Multi-Service Backend

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/your-username/fastapi-translate.git
cd fastapi-translate
```

2. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Set up development environment**
```bash
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
```

4. **Make your changes**
   - Follow PEP 8 style guide
   - Add docstrings to functions
   - Test your changes locally

5. **Run the server locally**
```bash
uvicorn app.main:app --reload
```

## Code Style

- Use 4 spaces for indentation
- Keep functions under 50 lines
- Add type hints where possible
- Use descriptive variable names

## Testing

Before submitting a PR:
- Test the API endpoints locally
- Verify error handling
- Check edge cases

## Submitting Changes

1. **Commit with clear messages**
```bash
git commit -m "feat: add new feature" 
git commit -m "fix: resolve issue with X"
git commit -m "docs: update README"
```

2. **Push to your branch**
```bash
git push origin feature/your-feature-name
```

3. **Create a Pull Request**
   - Describe what you changed
   - Reference any related issues
   - Include test results

## Bug Reports

When reporting bugs:
- Describe the issue clearly
- Include steps to reproduce
- Share error messages/logs
- Mention your OS and Python version

## Feature Requests

For new features:
- Explain the use case
- Describe expected behavior
- Discuss implementation approach

## Questions?

Open an issue or discussion for questions about contributing.
