# Contributing to TransPort-PH

Thank you for considering contributing to TransPort-PH! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in the [Issues](https://github.com/yourusername/TransPort-PH/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Detailed description of the issue or suggestion
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)

### Submitting Changes

1. **Fork the repository**

```bash
git clone https://github.com/yourusername/TransPort-PH.git
cd TransPort-PH
```

2. **Create a new branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

3. **Make your changes**
   - Follow the code style guidelines (see below)
   - Add tests if applicable
   - Update documentation as needed

4. **Test your changes**

```bash
# Run the affected scripts
python src/data_collection/your_modified_script.py

# Check for linting issues (if using)
flake8 src/
black --check src/
```

5. **Commit your changes**

```bash
git add .
git commit -m "Brief description of changes"
```

Use clear, descriptive commit messages:
- `feat: Add new data source for traffic patterns`
- `fix: Correct path handling in dashboard`
- `docs: Update installation instructions`
- `refactor: Reorganize preprocessing modules`

6. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of changes
   - Reference any related issues

## 📝 Code Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Use type hints where appropriate

Example:

```python
def calculate_congestion_index(
    traffic_data: pd.DataFrame,
    baseline_speed: float = 50.0
) -> pd.Series:
    """
    Calculate congestion index from traffic data.
    
    Args:
        traffic_data: DataFrame containing speed measurements
        baseline_speed: Reference speed for free-flow conditions
        
    Returns:
        Series with congestion index values (0-100)
    """
    # Implementation here
    pass
```

### File Organization

- Use the established directory structure:
  - `src/data_collection/` - Data gathering scripts
  - `src/preprocessing/` - Data cleaning and transformation
  - `src/models/` - Model training and prediction
  - `src/analysis/` - Analysis and evaluation
  - `src/visualization/` - Plots and dashboards
  - `config/` - Configuration files
  - `tests/` - Unit and integration tests

### Path Handling

- **Always use pathlib** instead of `os.path`
- **Use centralized config** from `config/config.py`
- Don't hardcode paths

Good:
```python
from config import DATA_DIR, RAW_DATA

output_path = RAW_DATA["worldbank"]
```

Bad:
```python
output_path = "../data/worldbank_data.csv"
```

### Documentation

- Add docstrings to all public functions and classes
- Update README.md if you add new features
- Add inline comments for complex logic
- Update relevant documentation in `docs/`

## 🧪 Testing

- Write tests for new functionality
- Ensure existing tests pass
- Test on your local environment before submitting

## 🔄 Development Workflow

1. **Set up development environment**

```bash
# Clone and setup
git clone https://github.com/yourusername/TransPort-PH.git
cd TransPort-PH

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (optional)
pip install jupyter black flake8 pytest mypy
```

2. **Make changes iteratively**
   - Start with small, focused changes
   - Test frequently
   - Commit often with clear messages

3. **Before submitting**
   - Review your changes
   - Test thoroughly
   - Update documentation
   - Ensure code follows style guidelines

## Areas for Contribution

We welcome contributions in these areas:

### Data Sources
- Adding new data collection scripts
- Improving data quality and coverage
- Handling edge cases and missing data

### Models
- Implementing new forecasting models
- Improving model performance
- Adding model interpretability features

### Analysis
- New policy scenarios
- Additional causal inference methods
- Sensitivity analyses

### Visualization
- Dashboard improvements
- New visualization types
- Interactive features

### Documentation
- Tutorials and examples
- Code documentation
- User guides

### Testing
- Unit tests
- Integration tests
- Performance benchmarks

## 📚 Resources

- [Project README](README.md)
- [Quick Start Guide](docs/QUICK_START.md)
- [Dashboard Guide](docs/DASHBOARD_GUIDE.md)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)

## Questions?

If you have questions about contributing:

- Open a [Discussion](https://github.com/yourusername/TransPort-PH/discussions)
- Check existing [Issues](https://github.com/yourusername/TransPort-PH/issues)
- Contact the maintainers

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

Thank you for contributing to TransPort-PH! 

